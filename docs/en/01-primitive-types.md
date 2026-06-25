# Primitive Types

DLang ships with a small, fixed set of scalar primitive types. They map directly onto machine representations, so there are no hidden boxes, no implicit metadata, and no allocation involved in declaring one. A primitive value lives exactly where you put it — on the stack, inside a struct, or in an array slot — which is what you want from a data-oriented systems language.

## The built-in scalars

Every primitive is declared with an explicit type annotation. The compiler will infer types in many places (see [Type Inference](31-type-inference.md)), but the primitives themselves are the irreducible building blocks of the type system.

```dlang
val a: byte
val b: short
val c: int
val d: long
val f: float
val g: double
val h: boolean
val i: char
```

The numeric integer types form a size ladder: `byte`, `short`, `int`, and `long` are progressively wider signed integers. `float` and `double` are the single- and double-precision IEEE-754 floating-point types. `boolean` holds `true` or `false`, and `char` represents a single character.

## Defaults and width

When you write a bare integer literal with inference, the compiler picks `int`; a bare decimal literal is inferred as `double`. If you need a different width you annotate it explicitly:

```dlang
val idade = 25        // inferred int
val pi = 3.14         // inferred double
val contador: long = 0 // forces long instead of int
```

This matters because DLang performs **no implicit numeric conversion**. A `byte` does not silently widen into an `int`, and an `int` does not silently become a `long`. Every cross-type numeric move is written out with `cast(T, x)`. That rule is covered in depth in [Static Typing](29-static-typing.md), but it starts here: the width you declare is the width you get.

## Design rationale

A systems language earns its keep by being predictable about memory and cost. Keeping the primitive set small and machine-mapped means the layout of any aggregate built from these types is obvious by inspection — there is no padding surprise hiding behind an abstract "number" type. Refusing implicit conversions removes an entire class of silent precision and sign bugs that plague C, and pushes every lossy or widening move into a visible `cast`. The result is that reading a type annotation tells you the exact size and representation of the data, with zero runtime ceremony.

## Related

- [Text Literals](02-text-literals.md)
- [Arithmetic Operators](03-arithmetic-operators.md)
- [Variables and Scope](04-variables-and-scope.md)
- [Static Typing](29-static-typing.md)
- [Type Inference](31-type-inference.md)

[← Index](README.md)
