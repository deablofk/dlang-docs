# Functions and Procedures

In DLang a function is just a compile-time constant bound with `::`. There is no separate `def` or `func` keyword — you name the value and bind it to a function literal, exactly as you would bind a type or any other compile-time constant. This is the Jai-style "everything is a declaration" model, and it is what lets functions, types, and namespaces all share one uniform syntax.

## The basic form

A function declaration names the function, lists its parameters in parentheses, gives a return type after `->`, and supplies a body in braces:

```dlang
somar :: (a, b: int) -> int {
  val resultado: int = a + b
  return resultado
}
```

Two details are worth calling out. First, the `::` binds `somar` as a compile-time constant — the function identity is fixed at compile time, which is what enables monomorphization and static dispatch elsewhere in the language. Second, parameters that share a type can be grouped: `(a, b: int)` declares both `a` and `b` as `int`, rather than forcing you to repeat the annotation.

## Single-line (expression) form

DLang is expression-oriented in the Scala sense, so when a function body is a single expression you can drop the braces and the `return` and write the body after `=`:

```dlang
somar :: (a, b: int) -> int = a + b
```

This is not a different kind of function — it is the same declaration with the body written as an expression. The `=` form and the `{ ... }` form are interchangeable; choose whichever reads better. The expression form shines for small, pure helpers, while the block form suits multi-statement logic.

## Procedures

A "procedure" in DLang is simply a function whose return type is omitted (it returns nothing). You write it exactly like any other function, just without the `-> T`:

```dlang
saudar :: (nome: string) {
  println("Olá, ${nome}")
}
```

There is no special keyword distinguishing procedures from functions; the absence of a return type is the whole story. This keeps the model minimal — a procedure is just the degenerate case of a function with no result.

## Default parameter values

A parameter can declare a default value with `=`. If the caller omits that argument, the default is used:

```dlang
somar :: (a, b: int = 0) -> int = a + b
```

Here `b` defaults to `0`, so `somar(5)` is equivalent to `somar(5, 0)`. Defaults make optional behavior explicit at the definition site rather than requiring overloads. How defaults interact with positional and named arguments at the call site is covered in [Parameter passing](10-parameter-passing.md).

## Design rationale

Binding functions with `::` rather than a dedicated keyword is a deliberate unification: a function is a value known at compile time, no different in kind from a constant or a type. That single rule pays off everywhere — function pointers, generics, and namespaces all reuse it without new syntax. The expression form (`= expr`) keeps small functions terse and honest about being pure mappings from inputs to an output, while the block form scales up to real logic. And because there is no hidden machinery — no implicit `this`, no overload resolution beyond defaults and generics — a function call compiles to a direct, predictable jump.

## Related

- [Parameter passing](10-parameter-passing.md)
- [Multiple return values](11-multiple-returns.md)
- [Function pointers](33-function-pointers.md)
- [Lambda expressions](39-lambda-expressions.md)
- [Generics](32-generics.md)
- [Modules and namespaces](19-modules-and-namespaces.md)

[← Index](README.md)
