# Manual Memory — the Builtin Floor

Ordinary DLang code **does not manage memory**. Every allocation belongs to an owning value — a `string`, a `List`, a `Map`, a `ByteBuf`, a `Pool`, or an owner you write yourself — and the compiler destroys each owner at its static last use ([Memory Safety](14a-memory-safety.md)). There is no user-facing `malloc`, no arena block, and no `free` call to forget.

But *somebody* has to implement `List`, and somebody has to hold the raw resource a C library hands back. That somebody is the **Builtin floor**: the audited bottom layer where the raw vocabulary — `Ptr(T)`, `New`, `Undo`, `ref`, `_alloc.*` — is legal. This page is about writing floor code correctly. If you are not implementing an owning handle or binding C, you should never need it.

## The boundary law

Raw memory operations are legal **only**:

1. inside the methods of a **`nocopy` + `deinit` owning handle** — the struct whose whole job is to own an allocation or a foreign resource,
2. in **extern C signatures** (bodiless declarations — see [C Interop](50-c-interop.md)),
3. in `string`'s own implementation,
4. in `yields` accessor bodies (the receiver-rooted `ref`),
5. in the fixed runtime hooks.

Anywhere else they are **`E_RAW_OUTSIDE_BUILTIN`**, on every build. There is no module allowlist — the standard library plays by the same rules, and the same handful of primitives underneath `List` are the ones you get for your own owners.

## The GOLD RULE

> **Every design states who owns each allocation and where it dies.**

On the floor that rule is literal: each `New` must belong to exactly one owning handle, and that handle's `deinit` is where it dies. The compiler guarantees `deinit` runs exactly once, at the owner's last use — your job is only to make `deinit` release everything the handle owns.

## Writing an owning handle

The canonical floor citizen: a `nocopy` struct whose *methods* do the raw work and whose `deinit` releases the allocation. Nothing outside the methods ever sees a pointer.

```dlang
// A growable stack of ints, implemented raw — this is exactly how List works.
IntStack :: nocopy struct {
  data: Ptr(int)
  len : int
  cap : int
}

IntStack.empty :: () -> IntStack = IntStack { data: null, len: 0, cap: 0 }

IntStack.push :: (v: int) {
  if (_.len == _.cap) {
    var grown: int = _.cap * 2
    if (grown == 0) {
      grown = 4
    }
    val buf: Ptr(int) = _alloc.alloc(int, grown)   // legal: owning-handle method
    for (i : 0..(_.len - 1)) {
      buf[i] = _.data[i]
    }
    if (_.cap > 0) {
      _alloc.free(_.data)
    }
    _.data = buf
    _.cap = grown
  }
  _.data[_.len] = v
  _.len = _.len + 1
}

IntStack.pop :: () -> int {
  _.len = _.len - 1
  return _.data[_.len]
}

IntStack.deinit :: () {          // the compiler calls this at last use
  if (_.cap > 0) {
    _alloc.free(_.data)
  }
}
```

Callers use `IntStack` as a plain safe value: it moves like any `nocopy` type, `E_USE_AFTER_MOVE` protects it, and its buffer is freed automatically. The `Ptr(int)` field is legal *because* the struct is a `nocopy`+`deinit` owner; the same field on a copyable struct is rejected wherever that struct is used.

Inside the methods, the raw vocabulary is the classic one:

```dlang
val h: Ptr(Pessoa) = New(Pessoa)    // heap-allocate one T   (= _alloc.alloc(T))
Undo(h)                             // the paired free       (= _alloc.free(h))
val buf: Ptr(int) = New(int, 8)     // N contiguous elements
buf[3] = 42                         // unchecked pointer indexing
val p: Ptr(int) = ref score         // address-of
p.value = 10                        // dereference
```

There is no bounds checking and no lifetime checking in here — this is deliberately the audited layer where the guarantee is your code's responsibility, kept small enough to audit.

## Wrapping a C resource

A resource allocated by C — an `addrinfo` list, an SSL session, a file mapping — gets the same treatment: an owning handle whose methods do the raw calls and whose `deinit` releases it exactly once. `AddrInfoList` in `std/net/socket.dlang` is the model:

```dlang
getaddrinfo  :: (node: Ptr(byte), service: Ptr(byte), hints: Ptr(byte), res: Ptr(byte)) -> int
freeaddrinfo :: (res: Ptr(byte)) -> void

AddrInfoList :: nocopy struct { head: long }     // the raw list, carried as an opaque long
AddrInfoList.deinit :: () {
  if (_.head != cast(long, 0)) {
    freeaddrinfo(cast(Ptr(byte), _.head))        // released exactly once, automatically
  }
}
```

Two floor idioms complete the FFI story:

- **Scratch buffers** for C out-structs are a `ByteBuf` local: `ByteBuf.new(n)` + `.zeros(n)`, pass `.addr(0)` (an opaque `long`) to C, read fields back with `.i32at`/`.i64at`. The buffer dies at last use like any owner — `std/time` and `std/net` are the models.
- **Addresses travel as `long`.** A `Ptr` expression may flow *one hop* into an extern C argument or an owning-handle/`string` method; anything beyond that crosses as an opaque `long` (`ByteBuf.addr(i)`, `cast(long, s.cstr())`). Pointers never spread through signatures.

## What about `defer`?

`defer` still exists as a general control-flow tool (run a statement at function exit), but it is **no longer how memory is released** — `deinit` at last use replaced the `defer Undo(p)` idiom, and it cannot be forgotten or doubled. Reach for `defer` for non-memory effects (logging, unlocking in code that predates an owner, test teardown).

## The allocator is an implementation detail

Owners' methods route allocations through the runtime's allocator (`std/mem/allocator.dlang`). There is **no supported way for ordinary code to swap it** — no ambient-allocator API surfaces above the floor. The two remaining artifacts (`debugAllocator` leak tracking, and the bulk arena the compiler wraps its own pipeline in during its self-migration) are tooling, compiled with `--raw-floor` — the flag that disables the boundary law for below-the-model code. Applications never need that flag.

## Design rationale

Manual memory did not disappear — it got a *place*. The floor keeps DLang a systems language: real pointers, exact layout, zero-cost FFI, allocation you can read. The boundary law keeps the floor from leaking upward: the unsafe vocabulary is confined to types whose single responsibility is ownership, small enough to audit, wrapped in an interface the checker can trust. Every safety property above (moves, borrows, projections, ASAP `deinit`) rests on these handles being correct — which is why the language makes "where raw code may live" a compiler-enforced law rather than a convention.

## Related

- [Memory Safety](14a-memory-safety.md)
- [Dynamic Allocation — owning values](18-dynamic-allocation.md)
- [Pointers and References](12-pointers-and-references.md)
- [C Interop](50-c-interop.md)
- [Constructors and Destructors](21-constructors-and-destructors.md)

[← Index](README.md)
