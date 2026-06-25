# Operator Overloading

DLang lets you give operators like `+` and `[]` a meaning for your own types. This is **syntactic polymorphism**: the operator is just sugar for a specially-named method, and the compiler resolves it **entirely at compile time** (static dispatch). The result has zero runtime cost — overloaded operators run at exactly the same speed as the hand-written function calls they expand into.

## Overloading an arithmetic operator

You overload an operator by defining the reserved method that corresponds to it. For `+`, that method is `operator_add`. It takes the right-hand operand and returns the result; `_` is the left-hand operand (self).

```dlang
Vetor2D :: struct {
  x, y: float
}

// Overloads `+` for Vetor2D.
Vetor2D.operator_add :: (outro: Vetor2D) -> Vetor2D {
  return Vetor2D {
    x: _.x + outro.x,
    y: _.y + outro.y
  }
}
```

Now `+` works on `Vetor2D` values, and the compiler translates the symbol into a direct call to the reserved method:

```dlang
val v1 = Vetor2D { x: 1.0, y: 2.0 }
val v2 = Vetor2D { x: 3.0, y: 4.0 }
val resultadoVetor = v1 + v2     // compiler rewrites to v1.operator_add(v2)
```

## Overloading the index operators `[]`

The subscript operators are overloaded with `operator_get` (read) and `operator_set` (write). These are what make standard-library collection types like `List` and `Map` behave like built-in arrays — the bracket syntax is not magic baked into the compiler, it is these two methods.

```dlang
List.operator_get :: (indice: int) -> T {
  return _.arrayInterno[indice]
}

List.operator_set :: (indice: int, valor: T) {
  _.arrayInterno[indice] = valor
}
```

With those defined, brackets read and write through the methods:

```dlang
var nomes: List(string) = List(string).init(_alloc)
nomes[0] = "Gabriel"             // rewrites to nomes.operator_set(0, "Gabriel")
val primeiro = nomes[0]          // rewrites to nomes.operator_get(0)
```

This is why `List` and `Map` are ordinary generic structs in the standard library rather than compiler built-ins: operator overloading gives a user-defined type the same indexing syntax the language already uses for native arrays.

## How resolution works: static dispatch

For operator overloading the polymorphism is resolved **entirely at compile time**. When the compiler sees a `+` or a `[]`, it intercepts the symbol and looks up the corresponding reserved method (`operator_add`, `operator_get`, `operator_set`, …) on the operand's type. It then emits a direct jump to that function's compiled code — the same machine-level call it would emit if you had written `v1.operator_add(v2)` yourself.

There is no runtime lookup, no dispatch table, and no boxing. The overloaded operator runs at exactly the same speed as a pure procedural function call. This is the opposite end of the cost spectrum from interface dispatch: interfaces decide *which* implementation at runtime (a fat-pointer call), while operators are fully decided at compile time and cost nothing extra.

## Design rationale

Operator overloading earns its place because it makes mathematical and collection-like types read naturally — `v1 + v2`, `nomes[0]` — without ever introducing a hidden runtime cost. By resolving the symbol to a named method at compile time, DLang keeps the convenience while staying honest about performance: the sugar is purely syntactic, the dispatch is purely static, and you can always see the function it expands into. It also unifies the language with its own standard library, since the same mechanism that lets you write `Vetor2D + Vetor2D` is what lets `List` and `Map` offer `[]` without compiler privilege.

## Related

- [Polymorphism](26-polymorphism.md)
- [Structs](17-structs.md)
- [Arrays and Lists](07-arrays-and-lists.md)
- [Maps and Dictionaries](08-maps-and-dictionaries.md)
- [Generics](32-generics.md)

[← Index](README.md)
