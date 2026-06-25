# Pattern Matching

The [`match` construct](05-conditionals.md) already handles *values*: literals, ranges, guards, and simple enums. Pattern matching extends it with the ability to look **inside** the structure of a value — to destructure structs, tuples, and enums-with-data right in the arm. It reuses the same `match` and `->` you already know.

## 1. Struct destructuring — the pattern mirrors the literal

A struct pattern looks just like a struct literal. A field written with a value must *match* that value; a field written with a name only *captures* it as a variable; fields you do not list are simply ignored (a partial pattern).

```dlang
match (pessoa) {
  Pessoa { nome: "Gabriel", idade } -> println("Gabriel is ${idade}")  // fixes nome, captures idade
  Pessoa { nome, idade }            -> println("${nome}, ${idade}")    // captures both
  Pessoa { idade } if (idade < 18)  -> println("minor: ${idade}")      // partial + guard
}
```

- a field with a value (`nome: "Gabriel"`) -> must match
- a field with a name only (`idade`) -> captured as a variable
- unlisted fields -> ignored (partial pattern)

## 2. Wildcard and binding

Inside a pattern, `_` means "there is a field here, ignore it" — the same "unnamed thing" idea as the lambda placeholder. To bind the **whole** value while also destructuring it, use `@`:

```dlang
match (pessoa) {
  Pessoa { nome: _, idade } -> idade    // '_' = "a field here, ignore it"
  p @ Pessoa { idade }      -> usar(p)  // '@' binds the WHOLE value to 'p' AND destructures
}
```

Note the catch-all arm of a `match` is still `else`, never `_`. The `_` ignores a *slot*; `else` is the default *arm*.

## 3. Tuple patterns

Tuples match positionally. This is covered in depth under [Tuples and Destructuring](38-tuples-and-destructuring.md):

```dlang
match (coord) {           // coord: (int, int), e.g. from buscarCoordenadas()
  (0, 0) -> "origin"
  (x, 0) -> "on the X axis"
  (0, y) -> "on the Y axis"
  (x, y) -> "point (${x}, ${y})"
}
```

## 4. Nesting — patterns compose recursively

A pattern can contain another pattern, all the way down:

```dlang
match (retangulo) {
  Retangulo { canto: Ponto { x: 0, y: 0 } } -> "anchored at the origin"
  Retangulo { canto: Ponto { x, y } }       -> "anchored at ${x},${y}"
}
```

## 5. Tagged-union enums — where match shines

This is the feature that makes pattern matching central to the language. An enum variant may carry data: a tag plus a payload.

```dlang
Forma :: enum {
  Ponto,                                     // no data
  Circulo(raio: float),
  Retangulo(largura: float, altura: float)   // 2 fields
}

// construct
val f: Forma = Forma.Circulo(raio: 10.0)
```

In memory this is a **tag plus the largest payload** — a compact, zero-cost, data-oriented layout. This is what replaces class hierarchies in DLang. The key safety property is that you can **only** extract the payload through a `match`, which makes the access safe by construction:

```dlang
// extracting data is ONLY possible via match -> safe by construction
val area: float = match (f) {
  Forma.Ponto                         -> 0.0
  Forma.Circulo { raio }              -> 3.14159 * raio * raio
  Forma.Retangulo { largura, altura } -> largura * altura
}
```

### Compiler guarantees

- **Exhaustiveness.** Every variant must be covered, or there must be an `else`. Adding a new variant to the enum without handling it becomes a compile error — the compiler points you at every match that now falls short.
- **Safe access.** You cannot read `.raio` from a `Retangulo`. The only path to a payload is through a `match` that has bound it, so an out-of-variant field access cannot be written.

## Syntax note: `:` is the field separator

Both struct **literals** and struct **patterns** use `:` as the field separator (`campo: valor`). This is consistent across the language and is the canonical form for naming a field's value.

## Design rationale

Tagged-union enums plus exhaustive, safe-by-construction matching give DLang a compact, data-oriented alternative to class hierarchies and virtual dispatch. The compiler turns "did you handle every case?" into a build error rather than a runtime surprise, and it makes reading the wrong variant's field unrepresentable rather than merely discouraged.

## Related

- [Conditionals](05-conditionals.md)
- [Enumerations](16-enumerations.md)
- [Tuples and Destructuring](38-tuples-and-destructuring.md)
- [Structs](17-structs.md)

[← Index](README.md)
