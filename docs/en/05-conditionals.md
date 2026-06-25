# Conditionals

DLang keeps a C-style surface — conditions go in parentheses and bodies use mandatory braces — but is expression-oriented like Scala: both `if` and `match` can be used as statements *or* as expressions that produce a value. This single design choice removes the need for a separate ternary operator and makes branching code read cleanly.

## `if` as a statement

In statement position, `if` works exactly as you expect. The condition is parenthesized and the body is braced:

```dlang
// simple conditional, not associated with a value
if (c) {
  a()
}

// if / else
if (c) {
  a()
} else {
  b()
}
```

You can chain `else if` to test several conditions in sequence. Braces are always required, even for a single statement — there is no brace-less body form.

## `if` as an expression (the ternary)

Because `if` is also an expression, you can bind its result directly. When used this way it is the language's ternary: it must have an `else` branch, because an expression must always produce a value.

```dlang
// inline: both branches present -> ok
val x = if (c) a else b

// no else while used as a value -> compile error
val y = if (c) a
```

The first line reads "x is a if c, otherwise b." The second line is rejected by the compiler: without an `else`, the expression has no value to yield when `c` is false. The rule is simple and worth internalizing — **an `if` used as a value must be exhaustive.**

## `match`

`match` is DLang's pattern-and-value dispatch construct, the equivalent of a `switch` but far more capable. Each arm uses `->` to map a pattern to a result, and `else` is the default catch-all.

```dlang
match (statusCode) {
  200 -> println("OK")
  404 -> println("Not Found")
  500 -> println("Internal error")
  else -> println("Unknown")
}
```

### `match` as an expression

Consistent with `if`, `match` is also an expression and can be bound to a value:

```dlang
val texto: string = match (statusCode) {
  200 -> "OK"
  404 -> "Not found"
  else -> "Unknown"
}
```

### Multiple values per arm

An arm can list several values separated by commas; it fires if the subject matches any of them:

```dlang
match (codigo) {
  200, 201, 204 -> "Success"
  400, 404 -> "Client error"
  else -> "Other"
}
```

### Ranges

Using `..` you can match an inclusive range of values. This reuses the same range notation that later serves slices:

```dlang
match (nota) {
  0..59 -> "Failed"
  60..100 -> "Passed"
  else -> "Invalid grade"
}
```

### Guards with binding

An arm can bind the subject to a name and then filter it with a parenthesized guard condition — `n if (...)`. This is consistent with the parenthesized conditions of `if` and `while`:

```dlang
match (pessoa.idade) {
  n if (n < 18) -> "minor"
  n if (n < 65) -> "adult"
  else -> "senior"
}
```

### Block arms

An arm's body can be a full block. As everywhere in the language, the last expression of the block is its value:

```dlang
match (x) {
  1 -> {
    val y = calcular()
    println(y)
    y * 2
  }
  else -> 0
}
```

### Matching enums

`match` pairs naturally with enums, letting you branch on each variant by name:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("file vanished")
  Erro.PermissaoNegada -> println("access denied")
  else -> println("ok")
}
```

This page covers matching on values, ranges, multiple values, guards, and enum variants. Looking *inside* a structure — destructuring a struct, tuple, or enum-with-data in the arm itself — is **pattern matching**, covered separately in [Pattern Matching](37-pattern-matching.md).

## Design rationale

Making `if` and `match` expressions eliminates a whole category of boilerplate: there is no ternary operator to learn, no temporary `var` that gets assigned in each branch, and conditional initialization reads as a single binding. Requiring `else` when an `if` is used as a value is the price of soundness — the compiler refuses to let an expression silently lack a result. `match` then generalizes the same idea: ranges, multi-value arms, and guards let one construct express what would otherwise be a tangle of nested `if`s, while keeping the surface syntax C-familiar and the bodies explicitly braced.

## Related

- [Variables and Scope](04-variables-and-scope.md)
- [Loops and Iteration](06-loops.md)
- [Enumerations](16-enumerations.md)
- [Pattern Matching](37-pattern-matching.md)

[← Index](README.md)
