# Type Inference

DLang infers types, but only *locally* — inside function bodies, for `val` and `var` bindings. Public surfaces are never inferred: function parameters, struct fields, and return types are always written out explicitly. This is the same boundary drawn by Odin, Jai, and Rust, and it keeps every API readable on its own without chasing inference across a codebase.

## Local inference for `val` and `var`

When you bind a value with `val` or `var` and omit the type, the compiler reads it from the initializer.

```dlang
val idade = 25      // inferred int (integer literals default to int)
val nome = "gabriel" // inferred string
val pi = 3.14        // inferred double (decimal literals default to double)
val ativo = true     // inferred boolean
```

A bare integer literal infers `int`; a bare decimal literal infers `double`. These are the defaults — the type the compiler picks when nothing else constrains the literal.

## Annotations refine inference (bidirectional)

Inference is bidirectional: a literal's type is the default only in the absence of context. When you write an explicit annotation, it flows *into* the literal and refines its type.

```dlang
// the annotation still applies when you want to pin the type
val contador: long = 0 // forces long instead of the default int
```

Here `0` would infer `int` on its own, but the `: long` annotation refines it, so the literal is interpreted as a `long`. The annotation and the literal cooperate rather than conflict — context wins over the default. (Note this is *refinement of a literal's type*, not a numeric conversion: there is no implicit widening here, just a literal being read at the requested width. Conversions between already-typed values still require an explicit `cast`; see [Static Typing](29-static-typing.md).)

## Inference through calls and factories

Inference also reads the result type of a call, so constructing a value never forces you to restate its type.

```dlang
val u = Pessoa("Gabriel", 25, true) // inferred Pessoa
val lista = List(int).init(_alloc)  // inferred List(int)
```

And the loop variable in a `for` is inferred from the thing being iterated — something you have already been relying on implicitly:

```dlang
for (nome : nomes) {
  // nome's type is inferred from the element type of nomes
}
```

## Where inference is forbidden on purpose

Three places never allow inference, because they form the public contract of your code:

```dlang
// - function parameters -> always 'name: Type'
// - struct fields        -> always 'field: Type'
// - function return       -> always '-> Type'
somar :: (a, b: int) -> int = a + b
```

A parameter is always `name: Type`, a field is always `field: Type`, and a return is always `-> Type`. Forbidding inference here is a feature: a caller, or a reader of a struct definition, sees the complete shape without having to reconstruct it from a function body somewhere else.

## Design rationale

Local inference removes the noisy, redundant annotations — restating `int` after a literal that is obviously an `int` — while signatures stay explicit so that the contract between pieces of code is always spelled out at the boundary. This is the sweet spot Odin, Jai, and Rust converge on: inference is a *local convenience*, never a *global puzzle*. Because integer literals default to `int` and decimals to `double`, the common case needs no annotation at all, yet the bidirectional rule means an annotation can still pin an unusual width without a cast. And because inference never crosses into parameters, fields, or returns, you can always read an API's types directly from its declaration — there is no inference to chase across files to understand what a function expects or returns.

## Related

- [Primitive Types](01-primitive-types.md)
- [Variables and Scope](04-variables-and-scope.md)
- [Static Typing](29-static-typing.md)
- [Generics and Parametric Programming](32-generics.md)
- [Functions and Procedures](09-functions.md)

[← Index](README.md)
