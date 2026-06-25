# Lambda Expressions

A lambda is a function literal: the same syntax as a named function, just without the `nome ::`. There is a *ladder* of three forms, from the shortest to the most explicit, so you reach for exactly as much syntax as the situation needs.

## The three forms

```dlang
{ _ * 2 }                               // 1 argument -> implicit placeholder '_'
{ acc, x -> acc + x }                   // N named arguments, types inferred from context
(a: int, b: int) -> int { return a+b }  // full form, explicit types
```

The first form is for the one-argument case and uses the universal placeholder `_`. The second names its arguments and lets their types be inferred from the call context, separating arguments from body with `->`. The third is the full function literal with explicit parameter types and return type.

### Multiline form

When the body is a block, the **last expression of the block** is its return value — no `return` needed:

```dlang
{ x ->
  val y = calcular(x)
  y * 2
}
```

## Trailing lambda

When a lambda is the **last** argument to a function, it leaves the parentheses and is written as a block after the call. If it is the **only** argument, the parentheses disappear entirely; any extra arguments stay inside the parentheses while the lambda moves out:

```dlang
nums.map { _ * 2 }                    // single argument -> no parentheses at all
nums.reduce(0) { acc, x -> acc + x }  // extra args stay in (), the lambda goes outside
```

This keeps a pipeline clean:

```dlang
val resultado = nums
  .filtrar { _ > 0 }
  .map      { _ * 2 }
  .reduce(0) { acc, x -> acc + x }
```

## Functions that take a block look native

The consequence of the trailing-lambda rule is that *any* function whose last parameter is a function reads like a built-in block — with no compiler magic at all. You can write your own control-flow-looking constructs:

```dlang
repetir :: (vezes: int, corpo: () -> ()) {
  var i = 0
  while (i < vezes) { corpo(); i++ }
}

repetir(3) {
  println("hello")
}

comArquivo("dados.txt") { arq ->
  println(arq.ler())
}
```

`repetir(3) { ... }` and `comArquivo("dados.txt") { arq -> ... }` are ordinary function calls that merely *look* like native blocks.

## Note: `for` and `while` stay native

A trailing lambda only *imitates* the appearance of a control block — it does not replace the native loops. `for` and `while` remain compiler constructs because they need `break` and `continue` and benefit from dedicated optimization, which a function call taking a closure cannot provide. Use the trailing lambda to build block-shaped *library* APIs; use the native loops for actual iteration.

## Design rationale

One rule — a lambda is a named function minus its name — produces the whole ladder, and the placeholder `_` reused from the `for` loop makes the common one-argument case as short as it can be. The trailing-lambda rule then lets library authors offer block-shaped APIs without any special compiler support, while the deliberate decision to keep `for`/`while` native preserves `break`/`continue` and the optimizer's grip on real loops.

## Related

- [Function Pointers](33-function-pointers.md)
- [Closures and Anonymous Functions](34-closures.md)
- [Higher-Order Functions](35-higher-order-functions.md)
- [Loops](06-loops.md)

[← Index](README.md)
