# Memory Safety

DLang is growing a **static memory-safety model**: use-after-free, double-free, use-after-move, and a pointer escaping its arena are **compile-time errors**, rejected before the program can run and at **zero runtime cost** in release builds. There is no garbage collector and no hidden bookkeeping — safety comes from the *shape* of the program, checked by the compiler.

This is opt-in in the sense that raw `Ptr(T)` + `Undo` (see [Manual Memory](13-manual-memory.md)) still exist as an explicit, unchecked escape hatch. But the safe idioms below make whole classes of bug **unrepresentable** rather than merely detectable.

## The problem, in one program

With raw pointers, a use-after-free and a double-free compile cleanly and blow up at runtime:

```dlang
Socket :: struct { fd: int }
main :: () -> int {
  val s: Ptr(Socket) = New(Socket)
  s.value.fd = 42
  Undo(s)                        // free
  val leaked: int = s.value.fd   // use-after-free (reads freed memory)
  Undo(s)                        // double free
  return leaked
}
```

```
$ doven before.dlang
compile: OK              # the compiler accepted the buggy program
$ ./before
free(): double free detected in tcache 2   # crash, at runtime
```

The model turns this into a compile error.

## Tier 1 — values are the default

DLang is value-semantics by default. A plain `struct` is a value: assigning or passing it copies it, and there is no pointer to dangle. Most data lives here, and it is safe for free — there is nothing to manage.

```dlang
Point :: struct { x: int  y: int }
val p: Point = Point { x: 1, y: 2 }
val q: Point = p          // an independent copy
```

## Owned resources — `nocopy` (affine) types

A resource that must be released exactly once — a socket, a file, a lock — is a **`nocopy`** struct. A `nocopy` value is *affine*: it is **moved, not copied**. It has exactly one live owner, and using it after that ownership has been given away is a compile error — the same defect as a use-after-free.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () = { /* close the fd */ }   // destructor — runs automatically
shutdown :: (sink s: Socket) { }               // `sink` = takes ownership

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  shutdown(s)                // ownership consumed here
  val leaked: int = s.fd     // ERROR: use of 's' after it was moved
  shutdown(s)                // ERROR: 's' consumed twice (double free)
  return leaked
}
```

```
7:21: error[E_USE_AFTER_MOVE]: use of 's' after it was moved (a `nocopy` value is consumed when moved)
8:12: error[E_USE_AFTER_MOVE]: use of 's' after it was moved (a `nocopy` value is consumed when moved)
```

Both the use-after-consume and the double-consume are rejected. Because there is exactly one owner, there is no second reference that could dangle.

### Automatic destruction (`deinit`)

A `nocopy` type may define `deinit`, which the compiler calls **automatically at the value's last use** — no manual `Undo`, no `defer`, no drop flags, and exactly once on **every** path (fall-through, early `return`, or a nested scope).

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () = { println("socket closed") }
use :: (s: Socket) -> int = s.fd     // borrows — does NOT consume

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  val a: int = use(s)     // borrow — still owned
  val b: int = use(s)     // borrow again — fine
  return a + b
}
// prints "socket closed" exactly once, when `s` is last used
```

Affinity is **contagious**: a plain struct that contains a `nocopy` field automatically becomes `nocopy` itself, so you cannot smuggle an owned value out through a copyable wrapper.

## Parameter conventions — `borrow`, `sink`, `inout`

A convention on a parameter says how the callee uses the argument. This is what lets you pass a `nocopy` value to a helper *without* consuming it.

| Convention | Meaning |
|---|---|
| `borrow` (default) | read-only access; the caller keeps ownership |
| `sink` | ownership transfers into the callee (the argument is consumed) |
| `inout` | exclusive mutable access |

```dlang
peek :: (s: Socket) -> int = s.fd          // borrow: may be called repeatedly
consume :: (sink s: Socket) -> int = s.fd  // sink: consumes the socket
```

Two rules keep borrows sound:

- **A borrow may not escape.** Returning, storing, or `sink`-ing a borrowed parameter is `E_REF_ESCAPES` — a borrow cannot outlive the call it came from.
- **Law of Exclusivity.** Two `inout` arguments in the same call may not alias the same storage (`E_EXCLUSIVITY`), so a mutable borrow is always exclusive.

```dlang
bump2 :: (inout a: int, inout b: int) { }
main :: () -> int {
  var x: int = 1
  bump2(x, x)     // ERROR[E_EXCLUSIVITY]: 'x' aliased by two inout arguments
  return x
}
```

## Arenas — `region` blocks

Single ownership can express trees, but not **cycles or shared back-references** — a doubly-linked list, a graph, an AST with parent pointers. Those go in a **`region`**: a lexical arena. Everything allocated inside is freed as one unit at the block's end, and the objects may point at each other freely, with no per-pointer annotations.

```dlang
Node :: struct { next: Ptr(Node)  prev: Ptr(Node)  v: int }
main :: () -> int {
  var sum: int = 0
  region g {
    val a: Ptr(Node) = New(Node)
    val b: Ptr(Node) = New(Node)
    a.value.next = b     // a -> b
    b.value.prev = a     // b -> a   (a cycle — fine inside a region)
    a.value.v = 30
    b.value.v = 12
    sum = a.value.v + b.value.v
  }                      // the whole graph is freed here, at once
  return sum
}
```

### Region isolation

The arena is *safe*, not just convenient: a pointer allocated in a region **may not escape it**. Storing a region pointer where it would outlive the region — an outer variable, or a field of an outer object — is a compile error, because that pointer would dangle when the region is freed.

```dlang
main :: () -> int {
  var escaped: Ptr(Node) = null
  region g {
    val a: Ptr(Node) = New(Node)
    escaped = a          // ERROR[E_REGION_ESCAPE]: a region-allocated pointer
  }                      //   escapes its region by being stored in 'escaped'
  return escaped.value.v
}
```

## The escape hatch and the honest limits

Raw `Ptr(T)` + `New`/`Undo` (see [Manual Memory](13-manual-memory.md)) remain available for C interop and for the cases the static model does not yet cover. Inside that raw layer you are on your own, exactly as in C — it is the deliberate boundary where the guarantee is your responsibility.

The model is under active development. Known gaps today: control-flow that *escapes* a region (a `return` out of one) is rejected rather than supported; region-escape via a callee that stores the pointer, or via a collection, is not yet caught; `inout` does not yet write back through references; and long-lived heap that is neither a `region` nor an owned handle still relies on the raw layer. These are refinements on top of a working core, not holes in it.

## Techniques and prior art

None of this is invented from scratch. The model is a synthesis of established, named techniques from type theory and from other languages — each solves one part of the use-after-free problem, and together they close it *statically*:

- **Affine types** (a.k.a. move-only / substructural types) — the core of `nocopy`. A value that may be used *at most once* cannot be used after it is consumed, so use-after-move and double-free are the *same* type error. This is the ownership discipline of **Rust**, the linear types of **Austral**, and the resource types of the **Move** language.
- **Move semantics** — consuming a value invalidates its source binding; the compiler tracks this per control-flow path (as **Rust**'s borrow checker does).
- **Mutable Value Semantics (MVS)** — value-semantics-by-default with no user-visible aliasing, from **Hylo** (formerly Val). Because values are independent and references are not first-class, a dangling reference is largely unrepresentable rather than merely detected.
- **Second-class references** and **parameter-passing conventions** (`borrow` / `sink` / `inout`) — also from **Hylo**, and mirrored by **Swift**'s `borrowing` / `consuming` argument modifiers. A borrow is created only at a call boundary and cannot escape it.
- **The Law of Exclusivity** — exclusive access for a mutable (`inout`) borrow, from **Swift** (SE-0176, "Enforce Exclusive Access to Memory").
- **Region-based memory management** — the `region { … }` block is a **Tofte–Talpin** region (`letregion`, 1994; **MLKit**), and the safe-C dialect **Cyclone**. Objects sharing one lexical lifetime are freed as one unit, and the type system guarantees no reference outlives its region.
- **Region isolation / external uniqueness (`iso`)** — a region is entered through a single owning handle so its interior cannot be aliased from outside, from **Project Verona** and **Pony**. This is what makes bulk-free of a cyclic graph sound and powers the `E_REGION_ESCAPE` check.
- **Ability tags** (`nocopy` / `nodrop`) — one-word capabilities on a type, in the style of the **Move** language's `copy` / `drop` / `store` abilities.
- **ASAP destruction with no drop flags** — `deinit` is inserted at the value's static *last use*, from **Mojo**'s ASAP ("As Soon As Possible") destruction and the reuse analysis of **Perceus** (Koka). There are no runtime drop flags; the analysis proves ownership at each exit.
- **Affinity contagion** — a struct containing an affine field is itself affine, as **Rust** propagates non-`Copy`.

The overarching discipline — *reject at compile time what cannot be proven safe, at zero runtime cost* — is the soundness bar set by **Rust**'s borrow checker (formally, **RustBelt**). DLang's contribution is packaging these techniques so the common cases need far fewer annotations, by leaning on value semantics and explicit lexical regions.

## The guarantees, at a glance

| Bug | Before | Now |
|---|---|---|
| use-after-free | compiles → runtime crash | **compile error** (`E_USE_AFTER_MOVE`) |
| double-free | compiles → runtime abort | **compile error** (`E_USE_AFTER_MOVE`) |
| dangling into a freed graph | compiles → segfault | **compile error** (`E_REGION_ESCAPE`) |
| borrow outliving its call | — | **compile error** (`E_REF_ESCAPES`) |
| aliased mutable borrows | — | **compile error** (`E_EXCLUSIVITY`) |
| resource cleanup | manual, easy to forget | **automatic** `deinit`, exactly once |
| runtime cost of the safety | — | **zero** — entirely static |

## Related

- [Manual Memory Management](13-manual-memory.md)
- [Garbage Collection](14-garbage-collection.md)
- [Constructors and Destructors](21-constructors-and-destructors.md)
- [Pointers and References](12-pointers-and-references.md)

[← Index](README.md)
