# Pointers and References

DLang application code has **no first-class pointers and no first-class references**. That sentence is the design: under pure Mutable Value Semantics (see [Memory Safety](14a-memory-safety.md)), data is values, mutation goes through the owner, and the aliasing that makes pointers dangerous is unrepresentable. References exist only in two second-class, compiler-controlled forms — parameter conventions and projections — and raw pointers exist only on the *Builtin floor*, inside the audited implementations of owning types.

This page explains all three layers: what you use instead of a pointer, the two safe reference forms, and the raw `Ptr(T)` vocabulary you will meet if you implement an owning handle or bind C.

## What replaces each pointer habit

| Pointer habit | Value replacement |
|---|---|
| out-parameter (`f(&result)`) | a `set` parameter — the callee initializes the caller's slot in place |
| mutate the caller's variable | an `inout` parameter — exclusive access, written back |
| heap object mutated from afar | a `nocopy` struct mutated through its methods |
| pointer into a container element | a projection — `xs.at(i).field = v`, or `inout e = xs.at(i)` |
| linked nodes, cycles, graphs | `Pool(T)` + copyable `Handle` values, or `int` indices into an append-only `List` |
| shared read access | a copyable view struct |
| byte buffer passed around | a `string` value, or an owning `ByteBuf` (crosses FFI as an opaque `long`) |

## Safe references #1 — parameter conventions

`borrow` (the default), `inout`, `sink`, and `set` create the only references ordinary code ever touches, implicitly, at a call boundary. They cannot be stored, returned, or otherwise outlive the call (`E_REF_ESCAPES`), and mutable ones are exclusive (`E_EXCLUSIVITY`). There is deliberately no `&` at the call site — the callee's signature carries the convention:

```dlang
rename :: (inout p: Pessoa, novo: string) { p.nome = novo }

var pessoa: Pessoa = Pessoa { nome: "Gabriel", idade: 25 }
rename(pessoa, "Bruno")     // no &: the signature says inout, write-back is guaranteed
println(pessoa.nome)        // "Bruno"
```

See [Parameter Passing](10-parameter-passing.md) for the full convention table.

## Safe references #2 — projections (`yields`)

A projection gives in-place access to an *element of an owner* — one `List` slot, one `Pool` entity, one field of a nested owner — without copying or moving it. It is produced by a `yields` accessor and is aggressively second-class: use it in the expression, or hold it briefly in an `inout` binding while the compiler locks the owner.

```dlang
xs.at(i).hp = 99            // mutate element i in place (member access auto-derefs)

inout e = xs.at(i)          // hold the projection for a few statements
e.hp = e.hp - 10
e.name = "wounded"
// xs is locked while e lives — using xs here is E_EXCLUSIVITY,
// because growing xs could reallocate and dangle the projection
```

Declare your own with `yields`:

```dlang
Grid :: nocopy struct { cells: List(Cell)  width: int }
Grid.cell :: (x: int, y: int) yields Cell = _.cells.at(y * _.width + x).value

grid.cell(1, 1).v = 9      // auto-deref member write, exactly like List.at
```

Retaining a projection any other way — binding it with `val`/`var`, storing it, returning it, passing it to an ordinary function — is `E_REF_ESCAPES`. To keep an element, move it out (`xs.removeAt(i)`).

## The floor — raw `Ptr(T)`, `ref`, and `.value`

Inside the Builtin floor — the methods of a `nocopy`+`deinit` owning handle, extern C signatures, `string`'s implementation, `yields` bodies, and the runtime hooks — the raw vocabulary is available, because something has to implement `List` and talk to C. Everywhere else it is `E_RAW_OUTSIDE_BUILTIN`. See [Manual Memory](13-manual-memory.md) for when you are allowed to be here.

A pointer is `Ptr(T)` — the same parenthesised notation as `List(T)`. You take an address with `ref`, and you read or write the pointee through the single property `.value`:

```dlang
// legal ONLY inside an owning handle's methods (or the rest of the floor):
val score: int = 99
val p: Ptr(int) = ref score     // address-of
p.value = 10                    // write through the pointer
println(p.value)                // 10
```

Funnelling every dereference through `.value` keeps each memory access explicit and gives the floor one visible checkpoint per access — there is no `*`/`&` punctuation and no implicit dereferencing.

**Rebinding versus mutating** stays unambiguous: bare assignment rebinds the pointer, `.value` assignment mutates the pointee.

```dlang
var a: int = 10
var b: int = 20
var pa: Ptr(int) = ref a
val pb: Ptr(int) = ref b
pa = pb          // rebind: pa now points at b
pa.value = 50    // mutate: writes 50 into b
```

`null` is a valid `Ptr(T)` value, compared directly with `==`/`!=`. `.value` chains into fields (`p.value.nome = "Gabriel"`), and `p[i]` indexes an N-element allocation. There is **no bounds check and no lifetime check** on raw pointer access — which is exactly why the boundary law confines it to the floor.

**FFI:** a `Ptr` expression may flow *directly* into an extern C argument (one hop); anything longer-lived crosses as an opaque `long` (`ByteBuf.addr(i)`, `cast(long, s.cstr())`). See [C Interop](50-c-interop.md).

## Function pointers are different

A function value already carries its callable type `(int, int) -> int`; it is not a `Ptr(T)` and is not dereferenced with `.value`. See [Function Pointers](33-function-pointers.md).

## Design rationale

Pointers earn their danger from two powers: they alias, and they outlive things. DLang removes both from application code instead of checking them — conventions and projections give the two legitimate uses of a reference (pass access down, touch an element in place) with escape and exclusivity enforced statically, and every remaining raw pointer lives behind the boundary law in code whose job is precisely to be audited. The result is C-grade data layout and FFI with no user-visible aliasing at all.

## Related

- [Memory Safety](14a-memory-safety.md)
- [Manual Memory — the Builtin floor](13-manual-memory.md)
- [Parameter Passing](10-parameter-passing.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [C Interop](50-c-interop.md)

[← Index](README.md)
