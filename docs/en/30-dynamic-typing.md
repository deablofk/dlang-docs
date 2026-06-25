# Dynamic Typing

DLang is a statically typed language, and almost everything you would reach for in a dynamic language is expressible with static types, generics, and interfaces. Dynamic typing exists only as a narrow, **explicit opt-in**: the `any` type. You ask for it by name; it never happens by default.

## The `any` type

`any` is a *fat pointer* — it stores a value together with a runtime tag identifying that value's concrete type. This is the very same mechanism DLang uses for interfaces (a data pointer plus a type/method pointer), so `any` reuses machinery that already exists rather than bolting on a separate dynamic runtime.

```dlang
// 'any' holds any value plus its runtime type tag
val caixa: any = 42
```

Here `caixa` carries both the integer `42` and a tag that says "this is an `int`". The static type of `caixa` is just `any`; the concrete type lives at runtime.

## Recovering the concrete type with `match`

You cannot use the value inside an `any` directly — there is no way to read it as an `int` until you have *proven* it is one. Recovery is done with `match`, binding the value to a name in the branch whose type matches the tag.

```dlang
match (caixa) {
  n: int    -> println("integer: ${n}")
  s: string -> println("text: ${s}")
  else      -> println("unknown type ${caixa}")
}
```

Each arm names a type (`n: int`, `s: string`); the matching arm binds the unwrapped value with its proper static type, so inside that branch `n` really is an `int`. This is the same `match` construct used for [Pattern Matching](37-pattern-matching.md) and enum dispatch — dynamic recovery is not a new feature, just `match` applied to the runtime tag. The `else` arm is the catch-all for any type not listed.

## Use sparingly

The design intent is explicit in the language's philosophy: `any` should be rare. If a problem can be modelled with generics, an interface, or a tagged union (an enum carrying data), those static tools are zero-cost and checked at compile time, whereas `any` pushes a type check to runtime and pays for the tag. `any` earns its place only where heterogeneity is genuinely dynamic — for example a value coming from reflection or a generic container that must hold truly unrelated types. DLang's `any` is close in spirit to Odin's `any`: a pragmatic escape hatch, not a programming style.

## Design rationale

A data-oriented systems language wants the cost of every operation visible in the source, so dynamic typing cannot be the default — it would scatter hidden runtime tags and type checks throughout otherwise static code. By making `any` an explicit type that reuses the interface fat-pointer mechanism, DLang keeps the dynamic case honest: you can see exactly where a value became dynamic (the `any` annotation) and exactly where it is made concrete again (the `match`). Nothing is boxed or tagged unless you wrote `any`, and the only path back to a usable value is a `match` that the compiler can keep exhaustive. The result is that the language supports dynamism where it is truly needed without letting it leak into the 99% of code that is better off fully static.

## Related

- [Static Typing](29-static-typing.md)
- [Type Inference](31-type-inference.md)
- [Pattern Matching](37-pattern-matching.md)
- [Interfaces](25-interfaces.md)
- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)

[← Index](README.md)
