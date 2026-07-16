# Memory Safety

DLang is memory-safe by construction. The model is **pure Mutable Value Semantics (MVS)** — the discipline pioneered by **Hylo** — with DLang's own keywords: every piece of data is a *value* with exactly one owner, mutation happens through the owner (never through an alias), and the compiler destroys each owner automatically at its last use. Use-after-free, double-free, use-after-move, dangling references, and aliased mutation are **compile-time errors**, rejected at **zero runtime cost**. There is no garbage collector, no reference counting, and no borrow-lifetime annotations.

This is not opt-in and there is no flag: the checks run on **every build**. Raw pointers still exist, but only on the *Builtin floor* — inside the audited implementations of owning types — never in application code (see [the boundary law](#the-boundary-law-no-raw-memory-outside-the-floor)).

## The vocabulary, at a glance

| Keyword / form | Where | Meaning |
|---|---|---|
| `nocopy` | before `struct` | the type is **affine**: moved, not copied; exactly one owner |
| `deinit` | method name | destructor; the compiler calls it **automatically at the value's last use** |
| `nodrop` | before `struct` | reserved: asserts a `deinit` that only releases memory (currently inert) |
| `borrow` | before a parameter (the default) | read-only access; caller keeps ownership |
| `inout` | before a parameter | exclusive mutable access with **write-back** — the caller sees the mutation |
| `sink` | before a parameter | ownership transfers into the callee |
| `set` | before a parameter | an **out-slot**: starts uninitialized, the callee must assign it on every path |
| `yields` | in an accessor signature | declares a **projection** accessor (in-place access to an element) |
| `yield e` | inside a `yields` body | the expression the projection exposes |
| `inout e = xs.at(i)` | statement | binds a projection for a run of statements; the owner is locked while it lives |
| `.copy()` | method call | explicit deep copy of an affine value — the only way to duplicate one |

## Values are the default

A plain `struct` is a value. Assigning or passing it copies it, and a copy is independent — there is no aliasing to reason about and no pointer to dangle. Implicit copying is allowed **only for data that needs no cleanup**; anything with a destructor is move-only by rule (below).

```dlang
Point :: struct { x: int  y: int }
val p: Point = Point { x: 1, y: 2 }
val q: Point = p          // an independent copy — mutating q never affects p
```

## Owned resources — `nocopy` (affine) types

A resource that must be released exactly once — a socket, a file, a growable buffer — is a **`nocopy`** struct. A `nocopy` value is *affine*: it is **moved, not copied**. Assignment transfers ownership, and using the old binding afterward is a compile error — the same defect as a use-after-free, caught before the program runs.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () { /* close the fd */ }     // destructor — runs automatically
shutdown :: (sink s: Socket) { }               // `sink` = takes ownership

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  shutdown(s)                // ownership consumed here
  val leaked: int = s.fd     // ERROR[E_USE_AFTER_MOVE]
  shutdown(s)                // ERROR[E_USE_AFTER_MOVE]  (a double free, statically)
  return leaked
}
```

The standard containers are themselves `nocopy` owners: **`List(T)`, `Map(K, V)`, `ByteBuf`, `Pool(T)`** all own their heap storage this way. That means `val ys = xs` on a `List` is a **move** — the honest cost model. To hand the same contents to two owners, ask for it explicitly with `xs.copy()`.

Affinity is **contagious**: a struct containing a `nocopy` field is itself `nocopy`, so an owned value cannot be smuggled out through a copyable wrapper.

### Automatic destruction — ASAP `deinit`

A `nocopy` type may define `deinit`. The compiler inserts the call **at the value's static last use** — as soon as possible, not at scope end — with no drop flags and no runtime bookkeeping, exactly once on **every** path (fall-through, early `return`, `break`, `continue`). This is Mojo-style ASAP destruction: you never write a free, and you cannot forget one.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () { println("socket closed") }
peek :: (s: Socket) -> int = s.fd     // borrow — does NOT consume

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  val a: int = peek(s)      // borrow — still owned
  val b: int = peek(s)      // borrow again — fine
  return a + b              // "socket closed" printed after the last use of s
}
```

`string` values are managed the same way (the compiler frees dead intermediates of `+`/interpolation on the spot — see the note on strings below), and a `List`'s `deinit` recursively drops every element before releasing the buffer.

## Parameter conventions — `borrow`, `inout`, `sink`, `set`

A convention on a parameter states what the callee does with the argument. This is the whole "reference" story in DLang: references exist only *at call boundaries*, are created implicitly (no `&` at the call site), and cannot escape the call.

| Convention | Callee's access | Ownership |
|---|---|---|
| `borrow` (default) | read-only | caller keeps it |
| `inout` | exclusive read-write, **written back** | caller keeps it, sees the mutation |
| `sink` | full | transfers to the callee |
| `set` | write-first (starts **uninitialized**) | caller keeps the initialized result |

```dlang
peek    :: (s: Socket) -> int = s.fd          // borrow: call repeatedly
rename  :: (inout p: Pessoa, n: string) { p.nome = n }   // caller's p changes
consume :: (sink s: Socket) { }               // s dies here (its deinit runs in the callee)
firstTwo :: (xs: List(int), set a: int, set b: int) {    // out-slots
  a = xs.get(0)
  b = xs.get(1)                               // every path MUST assign a and b
}
// caller: `var a: int` (uninitialized is fine) then firstTwo(xs, a, b)
```

The rules that keep this sound:

- **A plain (borrow) parameter is immutable.** Assigning to it or through it is `E_IMMUTABLE`. If you want the caller to see a change, say so: `inout`.
- **`inout` is real write-back.** The argument must be a mutable lvalue rooted at a `var`; the caller's value is updated when the call returns. This matters for affine values especially: passing a `nocopy` struct as a plain parameter gives the callee a *read-only view*, not a mutable alias.
- **A borrow may not escape.** Returning, storing, or `sink`-ing a borrowed parameter is `E_REF_ESCAPES` — a borrow never outlives its call.
- **Law of Exclusivity.** Two `inout` arguments may not alias the same storage (`E_EXCLUSIVITY`); a mutable borrow is always exclusive.
- **`set` is checked by definite assignment.** The callee must assign the slot on every path (`E_SET_UNASSIGNED`) and may not read it before the first assignment (`E_SET_BEFORE_ASSIGN`). `set` is the PVS replacement for "construct the result where it has to live" — out-construction in place, with no pointer.

```dlang
bump2 :: (inout a: int, inout b: int) { }
main :: () -> int {
  var x: int = 1
  bump2(x, x)     // ERROR[E_EXCLUSIVITY]: 'x' aliased by two inout arguments
  return x
}
```

## Projections — `yields`, auto-deref, and `inout` bindings

Move-only containers need a way to touch *one element in place* without copying it out or moving it. That is a **projection**: a second-class, receiver-rooted reference produced by a `yields` accessor. `List(T).at` is the model:

```dlang
xs.at(i).hp = 99                 // auto-deref: mutate a field of element i in place
xs.at(i).inventory.add("potion") // nested owners mutate in place too
```

To keep a projection across several statements, bind it with `inout`:

```dlang
inout e = xs.at(i)     // e projects element i
e.hp = e.hp - 10
e.shield = 0
// while e is live, xs is LOCKED: using xs here is E_EXCLUSIVITY
// (a grow could reallocate the buffer and dangle the projection)
```

Any other retention of a projection — a `val`/`var` binding, storing it in a field, returning it, passing it to an ordinary function — is `E_REF_ESCAPES`, on every build. To *keep* an element, move it out with `xs.removeAt(i)`.

You can declare projections on your own owners:

```dlang
Cell :: struct { v: int }
Board :: nocopy struct { cells: List(Cell) }
Board.cell :: (x: int, y: int) yields Cell = _.cells.at(y * 8 + x).value
// (forwarding an inner projection derefs it with .value; block bodies use `yield e`)

board.cell(3, 4).v = 1        // member access auto-derefs, same as List.at
```

A projection of a *scalar* (`yields int`) is written through `.value` — `score.cell(i).value = 9` — since there is no member to auto-deref. Inside a `yields` body the compiler permits the receiver-rooted `ref` it needs; callers never see a pointer.

## Graphs and shared identity — `Pool(T)` + `Handle`, or indices

Single ownership expresses trees. For **cycles, back-references, and ECS-shaped lifetimes** (entities that refer to each other and die independently), DLang's answer is *indices instead of pointers*:

- **`Pool(T)` + `Handle`** (`import("std/collections/pool")`): a slot store with **generational handles**. `Handle { slot, gen }` is a plain copyable value — store it in fields, lists, other entities; cycles are free. Killing an entity bumps its slot's generation, so every stale copy of its handle becomes *detectably dead* (`alive(h) == false`) instead of dangling:

```dlang
inline import("std/collections/pool")

var mobs: Pool(Mob) = Pool(Mob).empty()
val h: Handle = mobs.spawn(Mob { hp: 10, target: Handle { slot: -1, gen: -1 } })
if (mobs.alive(h)) {
  mobs.at(h).hp = 9        // .at(h) is a projection, same rules as List.at
}
mobs.kill(h)               // idempotent; the slot is recycled by a later spawn
```

- **The index encoding**: for append-only stores (an AST, an interning table), plain `int` indices into a `List(Node)` work directly — an index cannot dangle into a store that never shrinks. This is how the DLang compiler itself represents its syntax trees.

There are **no region/arena blocks in the language**. The old `region { … }` / `detach` tier was removed when the pure-MVS model landed (writing them is `E_NOT_SUPPORTED`, with a migration hint): everything a region did is covered by owners that die at last use, `Pool`/indices for graphs, and `set` out-parameters for building results in place.

## The boundary law — no raw memory outside the floor

`Ptr(T)`, `New`, `Undo`, `ref`, and `_alloc.*` still exist — they are what `List` and `string` are *built out of* — but they are confined to the **Builtin floor**. Raw operations are legal only:

1. inside the methods of a `nocopy` + `deinit` **owning handle** (the raw implementation surface of `List`, `Map`, `ByteBuf`, your own resource wrappers),
2. in **extern C signatures** (FFI declarations with no body),
3. in `string`'s own implementation,
4. in `yields` accessor bodies (the receiver-rooted `ref`),
5. in the fixed runtime hooks.

Anywhere else — a signature, a struct field, a local, an allocation in ordinary code — is **`E_RAW_OUTSIDE_BUILTIN`**, on every build, with **no module allowlist**: the standard library obeys the same law, and the compiler is migrating its own sources to it. `--raw-floor` disables the law only for below-the-model code (the compiler's bootstrap and the allocator-introspecting proof harnesses); it is not for applications.

FFI buffers cross API boundaries as opaque `long` addresses (`ByteBuf.addr(i)`, `cast(long, s.cstr())`), and a C-owned resource is wrapped in an owning handle whose `deinit` releases it exactly once. See [Manual Memory](13-manual-memory.md) for the floor in full.

## Strings and ASAP reclamation

`string` is a value with compiler-managed ownership: interpolation and `+` temporaries, `println` arguments, and accumulation locals (`var s` … `s = s + piece` in a loop) are freed **on the spot** by compiler-inserted drops. The accumulation idiom is therefore the *preferred* way to build strings — it no longer leaks. (It is still O(n²) copying for very large outputs; divide-and-conquer join those.)

## The error codes

| Code | Rejected program shape |
|---|---|
| `E_USE_AFTER_MOVE` | using / re-consuming an affine value after it was moved |
| `E_IMMUTABLE` | writing through a plain (borrow) parameter |
| `E_EXCLUSIVITY` | aliased `inout` arguments; touching an owner while its projection is live |
| `E_REF_ESCAPES` | a borrow or projection escaping its call / statement scope |
| `E_SET_UNASSIGNED` / `E_SET_BEFORE_ASSIGN` | a `set` out-slot not assigned on every path / read too early |
| `E_RAW_OUTSIDE_BUILTIN` | any raw-memory vocabulary outside the sanctioned floor |
| `E_NOT_SUPPORTED` | the removed `region` / `detach` tier |

## Techniques and prior art

The model is a synthesis of established techniques — DLang's contribution is committing to the *pure* combination, with no unsafe user-facing tier left over:

- **Mutable Value Semantics** — values with single ownership, mutation only through the owner, no first-class references: **Hylo** (formerly Val). DLang is a Hylo-purist implementation with its own keyword surface.
- **Parameter-passing conventions** (`borrow` / `inout` / `sink` / `set`) and **second-class references** — also from **Hylo**, mirrored by **Swift**'s `borrowing`/`consuming`; `set` is Hylo's out-initialization convention.
- **Law of Exclusivity** — exclusive mutable access, from **Swift** (SE-0176).
- **Projections** — subscript-style `yields` accessors are Hylo's (and Swift's) accessor coroutines; the compile-time root-lock replaces runtime exclusivity checks.
- **Affine types / move semantics** — `nocopy` is the ownership discipline of **Rust**, the linear types of **Austral**, the abilities of **Move**.
- **ASAP destruction with no drop flags** — from **Mojo**'s ASAP destruction and the reuse analysis of **Perceus** (Koka).
- **Generational indices** — `Pool(T)` + `Handle` is the ECS idiom Hylo and the Rust game-dev community converged on: dynamic staleness instead of lexical lifetimes.

An earlier iteration of the model also had Tofte–Talpin-style lexical regions for pointer graphs; they were **deleted** when projections, `set`, and `Pool` proved sufficient — a lexical raw zone was the one place the safety claim stayed conditional, and Hylo demonstrates the model stands without it.

## The guarantees, at a glance

| Bug | Outcome |
|---|---|
| use-after-free / double-free | **compile error** (`E_USE_AFTER_MOVE`) |
| dangling reference | unrepresentable — references never escape a call |
| aliased mutation | **compile error** (`E_EXCLUSIVITY`) |
| projection dangling across a grow | **compile error** (root lock / `E_REF_ESCAPES`) |
| stale entity handle | **detectable** (`pool.alive(h) == false`), never a dangle |
| raw pointer in application code | **compile error** (`E_RAW_OUTSIDE_BUILTIN`) |
| forgotten cleanup | impossible — `deinit` is automatic, exactly once, ASAP |
| runtime cost of all of the above | **zero** — entirely static |

## Related

- [Manual Memory — the Builtin floor](13-manual-memory.md)
- [Garbage Collection (why there is none)](14-garbage-collection.md)
- [Dynamic Allocation — owning values](18-dynamic-allocation.md)
- [Pointers and References](12-pointers-and-references.md)
- [Parameter Passing](10-parameter-passing.md)
- [Constructors and Destructors](21-constructors-and-destructors.md)

[← Index](README.md)
