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

When the number of elements is not known until runtime, you reach for `List(T)`. Crucially, `List(T)` is **not** compiler magic — it is a normal generic struct provided by the standard library, the same kind of type you could write yourself. What makes it dynamic is that it owns a growable buffer, and growing that buffer means allocating memory. DLang never allocates implicitly, so you hand the list an allocator when you create it:

```dlang
var lista: List(int) = List(int).empty()   // _alloc = default allocator
lista.add(10)
```

`List(int).empty()` constructs an empty list. Its backing storage grows from the **current allocator** — DLang's ambient, swappable memory context — so you never thread an allocator through by hand; installing a different allocator redirects the list's memory too. `lista.add(10)` appends an element, growing the backing buffer if needed. The allocator model is covered in [Dynamic Allocation](18-dynamic-allocation.md) and [Manual Memory](13-manual-memory.md).

Indexing a `List(T)` with `[i]` works just like an array, but that is not built-in syntax either: the list implements the `operator_get` and `operator_set` methods, and the compiler resolves `lista[i]` to those at compile time. See [Operator Overloading](27-operator-overloading.md).

## Design rationale

Splitting fixed arrays from dynamic lists keeps cost honest. A `[N]T` array is a primitive, compile-time-sized layout with no overhead, perfect for data whose size you know. A `List(T)` is a library type that has to allocate to grow, and by forcing you to pass an allocator the language makes that cost impossible to miss — there is no hidden heap allocation behind an innocent-looking append. Keeping `List` in the standard library rather than the compiler proves the language's core claim: rich collections are just generic structs over an allocator and a few operator methods, not privileged built-ins.

## Related

- [Loops and Iteration](06-loops.md)
- [Maps and Dictionaries](08-maps-and-dictionaries.md)
- [Manual Memory](13-manual-memory.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Operator Overloading](27-operator-overloading.md)

[← Index](README.md)
