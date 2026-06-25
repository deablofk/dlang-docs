# Static Typing

DLang is statically typed: every value has a type that is known and fixed at compile time, and the compiler rejects any program that tries to use a value as a type it does not have. There is no runtime type coercion happening behind your back. Just as importantly, DLang performs **no implicit numeric conversion** — unlike C, a narrower integer never silently widens into a wider one. Every change of type is written out explicitly with `cast(T, value)`.

## Types are checked, not coerced

Assigning a value of the wrong type is a compile error, not a silent conversion or a runtime cast.

```dlang
val idade: int = 25
idade = "vinte" // compile error: string is not int
```

The check happens before the program ever runs. A `string` and an `int` are different types, and no amount of context makes one acceptable where the other is required.

## No implicit numeric conversion

This is the rule that most distinguishes DLang from C. Even when a conversion is *widening* and lossless — `int` into `long`, for instance — DLang will not perform it for you.

```dlang
// no implicit numeric conversion (unlike C)
val pequeno: int = 10
val grande: long = pequeno            // ERROR: int does not become long on its own
val grande: long = cast(long, pequeno) // OK: explicit conversion
```

The reason is consistency and visibility. If the compiler silently widened `int` to `long` here, it would also be tempting to silently narrow `long` to `int` somewhere else — and *that* loses data and sign information, which is exactly the class of bug that haunts C. Rather than carve out a "safe subset" of implicit conversions and ask you to memorise its edges, DLang makes the rule uniform: numbers never change type by themselves.

## Casting with `cast(T, value)`

All conversions use the same `cast(T, value)` form. The parenthesised notation is deliberate: it rhymes with `Ptr(T)`, `List(T)`, and the generic instantiations elsewhere in the language, so "applying a type" always looks the same.

```dlang
// conversion uses cast(T, value) — consistent with Ptr(T)/List(T) notation
val n: int = cast(int, 3.9)   // truncates to 3
val f: float = cast(float, n)
```

Because the cast is explicit, a reader always sees where a lossy or representation-changing operation occurs. Truncating `3.9` to `3` is a decision you wrote down, not something that happened to you.

Pointer casts follow the same rule — reinterpreting one pointer type as another is also spelled with `cast`:

```dlang
// pointer casts are explicit too
val bruto: Ptr(byte) = cast(Ptr(byte), pessoaPtr)
```

## `as` is reserved

DLang deliberately keeps `as` out of the casting story. `as` is reserved for declaring that a type implements an interface (see [Interfaces](25-interfaces.md)), so it never competes with `cast`. One keyword, one meaning: `cast` converts values, `as` wires up contracts.

## Design rationale

Static typing in a systems language earns its keep by making cost and representation predictable. Because no conversion happens implicitly, the type written in a declaration is the exact machine representation you get, with no hidden widening, narrowing, or boxing. Funnelling every conversion through `cast(T, value)` turns each one into a visible, auditable point in the source — you can read a function and know precisely where data changes width or sign. This is the same impulse behind reading memory only through `.value` and allocating only through a visible allocator: the dangerous operations are never invisible. The payoff is that whole categories of C bugs — silent truncation, unexpected sign extension, accidental promotion in arithmetic — simply cannot occur without you having written the `cast` that causes them.

## Related

- [Primitive Types](01-primitive-types.md)
- [Dynamic Typing](30-dynamic-typing.md)
- [Type Inference](31-type-inference.md)
- [Generics and Parametric Programming](32-generics.md)
- [Interfaces](25-interfaces.md)

[← Index](README.md)
