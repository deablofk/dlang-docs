# Generics and Parametric Programming

Generics let a single definition work over many types. DLang implements them by **monomorphization** — the compiler stamps out a specialized copy for each concrete instantiation, exactly like Rust and Zig — so generic code is *zero-cost*: a `List(int)` is as fast and as compact as a hand-written integer list. Generic parameters are written in `Name(...)` **before** the `::`, mirroring how you already *use* them at the call site (`List(int)`, `Map(string, int)`).

## Generic structs

A type parameter list goes right after the name, before `::`. This is why a generic struct reads the same way whether you are defining it or instantiating it.

```dlang
// generic struct — the (T) before "::" matches the use site List(int)
List(T) :: struct {
  arrayInterno: Ptr(T)
  tamanho: int
  capacidade: int
}
```

## Methods on generic types

A method on a generic type keeps the type parameters in scope, which is what lets a method mention `T` in its signature:

```dlang
List(T).add :: (item: T) {
  // ...
}

List(T).operator_get :: (indice: int) -> T {
  return _.arrayInterno[indice]
}
```

Multiple parameters are just a comma-separated list, mirroring `Map(string, int)` at the use site:

```dlang
Map(K, V) :: struct {
  // ...
}
```

## Generic functions

Functions follow the identical rule: the generic parameters live in `Name(...)` before `::`.

```dlang
max(T) :: (a, b: T) -> T = if (a > b) a else b
```

You can call with inference, letting the compiler recover `T` from the arguments, or pass the type explicitly to disambiguate:

```dlang
val m = max(10, 20)        // T = int, inferred from the arguments
val x = max(int)(10, 20)   // instantiate max(int), then call
val l = List(int).empty()
```

## Compile-time value parameters

Generic parameters are not limited to types. A parameter can be a compile-time *value*, faithful to the language's "types are compile-time values" stance and connecting directly to fixed arrays `[N]T`:

```dlang
// T is a type, N is an int value known at compile time
Buffer(T, N: int) :: struct {
  data: [N]T // fixed size resolved during compilation
}

val b: Buffer(int, 16) = ... // an internal array of 16 ints, zero cost
```

Because `N` is known at compile time, `Buffer(int, 16)` has its size baked in with no runtime bookkeeping. This is the foundation of DLang's limited dependent types (see [Dependent Types](48-dependent-types.md)).

## Constraints via interfaces (optional)

A generic parameter can be *unconstrained*, in which case it works duck-typed at compile time — any operation you use must simply exist for the concrete type, Zig-style. Or you can attach an interface bound, which documents the contract and moves the error to the call site, Rust-style.

```dlang
// 'Comparable' is an ordinary interface (defines operator_compare, say)
ordenar(T: Comparable) :: (lista: List(T)) {
  // the compiler guarantees every T here implements Comparable
  // -> a clear error at the call site, not deep inside the function
}
```

Both forms are equally zero-cost; the only difference is *where* and *how clearly* a mismatch is reported. Without a bound you get maximum flexibility; with a bound you get a documented contract and a friendlier error.

## Design rationale

Monomorphization is what makes generics free: there is no boxing, no virtual dispatch, and no runtime type information involved — each instantiation compiles to code as specific as if you had written it by hand. Putting the parameters in `Name(...)` before `::` means definition and use share one syntax, so `List(T) :: struct` and `List(int)` are visibly the same shape. Allowing compile-time *value* parameters, not only type parameters, is what lets fixed-size buffers and dimensioned types exist without a runtime cost, and it is the bridge to the language's limited dependent types. Making interface constraints *optional* keeps the common case lightweight while still offering Rust-grade, call-site error messages when you want the contract written down. A pleasant consequence is that `List` and `Map` need no special compiler magic at all — they become ordinary generic structs shipped in the standard library.

## Related

- [Static Typing](29-static-typing.md)
- [Type Inference](31-type-inference.md)
- [Interfaces](25-interfaces.md)
- [Arrays and Lists](07-arrays-and-lists.md)
- [Dependent Types](48-dependent-types.md)
- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)

[← Index](README.md)
