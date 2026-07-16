# Arrays and Native Lists

DLang distinguishes two kinds of sequential collection, and the distinction is deliberate and visible. A **fixed-size array** is a compiler-level type whose length is part of its type and known at compile time. A **dynamic list** is an ordinary standard-library type, `List(T)`, that grows at runtime, drawing its memory from the current allocator. Neither hides a heap allocation from you.

## Fixed-size arrays

A fixed array has the type `[N]T`, where `N` is the compile-time length and `T` is the element type. Its storage is exactly `N` elements laid out contiguously — no header, no capacity field, no indirection. You index it with `[i]`:

```dlang
var nomes: [2]string = ["0", 2]   // size 2, zero-filled then assigned
nomes[0] = "a"
nomes[1] = "b"
```

Because the length is part of the type, the compiler knows the exact size of the array at every use, which makes it a zero-cost building block. Fixed arrays are also what make the language's compile-time-sized generics work: a `Buffer(T, N)` whose field is `[N]T` resolves its storage entirely at compile time (see [Generics](32-generics.md)).

You can let the compiler infer the length from the literal. An array literal written without an explicit count takes the length of the literal — `[]string` with two elements is the same as `[2]string` (you may also see this written `[_]string`, using the placeholder for "infer the count"):

```dlang
val nomes: []string = ["gabriel", "bruno"]   // implicitly [2]string
```

## Dynamic lists

When the number of elements is not known until runtime, you reach for `List(T)`. Crucially, `List(T)` is **not** compiler magic — it is a normal generic struct provided by the standard library, implemented on the Builtin floor the same way you could write your own owner ([Manual Memory](13-manual-memory.md)). What makes it dynamic is that it **owns** a growable buffer — and ownership is the whole story of how you pass it around (below).

```dlang
var lista: List(int) = List(int).empty()
lista.add(10)
```

`List(int).empty()` constructs an empty list; `lista.add(10)` appends, growing the backing buffer (by doubling) when needed. The buffer is freed automatically at the list's last use — its `deinit` runs exactly once, inserted by the compiler ([Memory Safety](14a-memory-safety.md)).

Indexing a `List(T)` with `[i]` works just like an array, but that is not built-in syntax either: the list implements the `operator_get` and `operator_set` methods, and the compiler resolves `lista[i]` to those at compile time. See [Operator Overloading](27-operator-overloading.md).

## Lists are owners: moves, copies

`List(T)` is a **`nocopy` (affine) owner**: it has exactly one owner at a time, and assigning or returning it **moves** it rather than copying. Using the old binding after a move is a compile error — the checker is protecting you from two owners freeing one buffer.

```dlang
var xs: List(int) = List(int).empty()
xs.add(1)
val ys: List(int) = xs        // MOVE — ownership transfers to ys
val n: int = xs.size()        // ERROR[E_USE_AFTER_MOVE]
val zs: List(int) = ys.copy() // explicit element-by-element copy: now two owners
```

Passing a list to a function follows the parameter conventions ([Parameter Passing](10-parameter-passing.md)): a plain parameter borrows it read-only, `inout` lets the callee mutate and write back, `sink` consumes it.

## Touching elements in place: `.at(i)` projections

`.get(i)` returns a *copy* of an element and `xs[i] = v` replaces one — but to mutate a struct element (or its nested owners) **in place**, project it with `.at(i)`:

```dlang
xs.at(i).hp = 99                  // auto-deref: writes the field inside the list
xs.at(i).inventory.add("potion")  // nested owners mutate in place too

inout e = xs.at(i)                // hold the projection for a few statements
e.hp = e.hp - 10
e.shield = 0
// while e is live, xs is locked (using it is E_EXCLUSIVITY):
// a grow could reallocate the buffer and dangle the projection
```

A projection cannot be stored, returned, or bound with `val`/`var` (`E_REF_ESCAPES`); to keep an element, move it out with `xs.removeAt(i)`. The full projection story — including declaring `yields` accessors on your own types — is in [Memory Safety](14a-memory-safety.md#projections--yields-auto-deref-and-inout-bindings).

## Design rationale

Splitting fixed arrays from dynamic lists keeps cost honest. A `[N]T` array is a primitive, compile-time-sized layout with no overhead, perfect for data whose size you know. A `List(T)` is a library type that has to allocate to grow, and the language keeps that cost visible without making you manage it: creation is explicit, growth is amortized, release is automatic at last use. Move-only ownership is the honest cost model for a buffer-owning type — a silent deep copy would hide O(n) work, and a silent shallow copy would be a double-free factory. Keeping `List` in the standard library rather than the compiler proves the language's core claim: rich collections are just generic structs plus a few operator methods, not privileged built-ins.

## Related

- [Loops and Iteration](06-loops.md)
- [Maps and Dictionaries](08-maps-and-dictionaries.md)
- [Memory Safety](14a-memory-safety.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Parameter Passing](10-parameter-passing.md)
- [Generics](32-generics.md)
- [Operator Overloading](27-operator-overloading.md)

[← Index](README.md)
