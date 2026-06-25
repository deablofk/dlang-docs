# Arithmetic Operators

DLang provides the familiar set of arithmetic operators for working with numeric types. They follow the conventional C-style surface syntax, so anyone coming from C, Zig, or Scala will read them at a glance. What stays consistent with the rest of the language is that they operate only on values of the same type — there is no hidden coercion between numeric types.

## The binary operators

The five core binary operators are addition, subtraction, multiplication, division, and the remainder (modulo):

```dlang
val a: int = 1 + 1
val b: int = 1 - 1
val c: int = 1 * 1
val d: int = 1 / 1
val e: int = 1 % 1
```

`+`, `-`, `*` behave as expected. `/` is integer division when both operands are integers, and `%` yields the remainder of that division. Because the operands here are both `int`, the result is `int`. If you wanted floating-point division you would use `float` or `double` operands — the language will not silently promote an `int` to a `double` for you (see [Static Typing](29-static-typing.md)).

## Increment and decrement

DLang supports the `++` and `--` operators in both prefix and postfix positions, and the distinction between them is the same as in C. The **postfix** form yields the value *before* the change; the **prefix** form yields the value *after* the change:

```dlang
val f: int = e++   // f gets the old value of e, then e increases
val g: int = ++e   // e increases first, then g gets the new value
val h: int = e--   // h gets the old value of e, then e decreases
val i: int = --e   // e decreases first, then i gets the new value
```

Because these operators mutate the operand, they only make sense on a mutable binding (`var`). Applying them to an immutable `val` is a compile error — see [Variables and Scope](04-variables-and-scope.md) for the mutability rules.

## Operators are expressions

Like the rest of the language, an arithmetic expression *is* a value, and arithmetic operators participate in the expression-oriented design. They are also the canonical example of compile-time operator resolution: for your own types you can give `+` (and friends) meaning by defining `operator_add` and similar methods, which the compiler resolves with zero-cost static dispatch. That mechanism is covered in [Operator Overloading](27-operator-overloading.md).

## Design rationale

Keeping arithmetic on a single type — no implicit promotion — means the cost and precision of every operation is visible in the source. An expression like `a + b` cannot silently widen, lose precision, or change sign behind your back; if you want a wider result you write the `cast` yourself. The prefix/postfix increment distinction is kept because it is a precise, well-understood tool for expressing "use then change" versus "change then use" in a single token. And because the same operators can be overloaded for user types at compile time, the surface stays uniform whether you are adding two `int`s or two `Vetor2D`s.

## Related

- [Primitive Types](01-primitive-types.md)
- [Variables and Scope](04-variables-and-scope.md)
- [Static Typing](29-static-typing.md)
- [Operator Overloading](27-operator-overloading.md)

[← Index](README.md)
