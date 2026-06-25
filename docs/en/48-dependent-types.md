# Dependent Types

> Status: Limited.

DLang offers a **limited, practical** form of dependent typing: compile-time *values* can parameterize types, and those values participate in type checking. This is the same level Zig reaches. What DLang does **not** have is full dependent types — types indexed by *runtime* values, or types carrying proofs. The dividing line is exactly the compile-time/runtime boundary.

## What exists: values as part of the type

A type parameter can be a compile-time integer, and that integer becomes part of the type's identity.

```dlang
Vetor(T, N: int) :: struct {
  data: [N]T // N is a value, but known at compile time
}
```

`N` is resolved during compilation, so `Vetor(float, 3)` and `Vetor(float, 4)` are genuinely different types. Because `N` is part of the type, the compiler can check that dimensions agree:

```dlang
// N participates in type checking: mismatched dimensions = compile error
somar(N: int) :: (a: Vetor(float, N), b: Vetor(float, N)) -> Vetor(float, N) { ... }

val a: Vetor(float, 3) = ...
val b: Vetor(float, 3) = ...
val c = somar(a, b)        // OK, N = 3 inferred

val d: Vetor(float, 4) = ...
val e = somar(a, d)        // compile error: N=3 vs N=4 do not match
```

The same mechanism makes dimensioned operations like matrix multiplication safe — the function only type-checks when the inner dimensions line up:

```dlang
Matriz(L: int, C: int) :: struct { data: [L][C]float }
multiplicar(L, M, N: int) :: (a: Matriz(L, M), b: Matriz(M, N)) -> Matriz(L, N) { ... }
```

A call where the shared dimension `M` does not match on both operands simply fails to compile.

## What does not exist: types depending on runtime values

A type can never depend on a value that is only known while the program runs.

```dlang
lerN :: () -> int = ...        // value known only at runtime
// var v: Vetor(float, lerN())  // ERROR: N must be compile-time
```

For a size that is genuinely dynamic, you do not reach for the type system — you use a heap-backed container with an explicit allocator:

```dlang
// for dynamic size use List(T) (heap, explicit allocator), not the type
var v: List(float) = List(float).init(_alloc)
```

This keeps a hard, legible line: dimensions in the *type* are always compile-time facts; anything that varies at runtime lives in a *value* like `List`.

## Design rationale

Full dependent types — where a type can mention any runtime value and the compiler reasons about arbitrary value-level propositions — buy enormous expressive power at the cost of a far heavier compiler and much harder ergonomics, which is a poor trade for a systems language. DLang takes the slice of that power that pays for itself: compile-time values parameterising types, reusing the very same generic machinery as `Buffer(T, N: int)` (see [Generics](32-generics.md)). That slice is enough to catch real, common bugs — mismatched vector lengths, incompatible matrix shapes — entirely at compile time and at zero runtime cost, because `N` never exists as a runtime quantity. Drawing the boundary at the compile-time/runtime line also keeps the rule easy to teach: if a size can change while the program runs, it belongs in a `List`, not in a type parameter.

## Related

- [Generics and Parametric Programming](32-generics.md)
- [Arrays and Lists](07-arrays-and-lists.md)
- [Static Typing](29-static-typing.md)
- [Compile-Time Theorem Proving](49-theorem-proving.md)
- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)

[← Index](README.md)
