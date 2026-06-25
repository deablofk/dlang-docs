# Multiple Return Values

A function in DLang can return more than one value. The return type is written as a parenthesized list of types, and the function returns a comma-separated list of values. Under the hood there is no special "multiple return" machinery — a multi-return is simply a function that returns a **tuple**, and tuples are the language's anonymous, positional aggregate.

## Declaring and returning

You declare multiple results by writing the return type as `(T1, T2, ...)`:

```dlang
buscarCoordenadas :: () -> (int, int) = {
  return 10, 10
}
```

The `return 10, 10` builds a two-element tuple `(10, 10)` and hands it back. The bare comma form is shorthand: `return 10, 10` means exactly `return (10, 10)`, because inside a `return` the keyword already delimits the expression, so the parentheses are optional. The same is true on the binding side, as we will see below.

## Consuming multiple returns

The natural way to consume a multi-return is to **destructure** it at the call site, binding each component to its own name:

```dlang
val (cx, cy) = buscarCoordenadas()
```

Here `cx` becomes `10` and `cy` becomes `10`. Because the keyword `val` already delimits the binding, the parentheses are again optional — `val cx, cy = buscarCoordenadas()` means the same thing. If you only care about some of the results, the placeholder `_` discards a slot:

```dlang
val (_, cy) = buscarCoordenadas()   // keep only the second value
```

## Returns are just tuples

It is worth internalizing that a multi-return is not a special feature layered onto functions — it *is* a tuple return. This is why the same `(int, int)` type that appears in a return signature also appears as a plain tuple type for variables, and why the same destructuring syntax works in both places. The error-handling convention in the language relies on exactly this: a fallible function returns `(value, error)`, and the caller destructures both halves. See [Error handling](15-error-handling.md) for that pattern, and [Tuples and destructuring](38-tuples-and-destructuring.md) for the full rules on tuples.

Pattern matching also operates on returned tuples directly, letting you branch on the shape of the result:

```dlang
match (buscarCoordenadas()) {
  (0, 0) -> "origem"
  (x, 0) -> "no eixo X"
  (x, y) -> "ponto (${x}, ${y})"
}
```

## Design rationale

Folding multiple returns into the tuple concept means there is one idea to learn instead of two. The compiler does not need a bespoke calling convention for "functions with several outputs" — it returns a tuple, a value type that lives on the stack at zero cost, with no allocator and no hidden heap. Destructuring at the call site keeps the data flow explicit: every returned value is named (or deliberately discarded with `_`), so nothing is silently dropped. And because tuples, destructuring, and pattern matching are one unified mechanism, multi-return composes cleanly with `match`, with `for (chave, valor : ...)` iteration, and with the `(value, error)` error convention.

## Related

- [Tuples and destructuring](38-tuples-and-destructuring.md)
- [Functions and procedures](09-functions.md)
- [Error handling](15-error-handling.md)
- [Pattern matching](37-pattern-matching.md)
- [Parameter passing](10-parameter-passing.md)

[← Index](README.md)
