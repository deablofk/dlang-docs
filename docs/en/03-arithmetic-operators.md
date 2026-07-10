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

## Compound assignment

For the common "update a variable using its own value" pattern, DLang provides the conventional compound-assignment operators. `x += e` is exactly shorthand for `x = x + e`, and the same holds for every arithmetic and bitwise operator:

```dlang
var total: int = 0
total += 10   // total = total + 10
total -= 3    // total = total - 3
total *= 2    // total = total * 2
total /= 4    // total = total / 4
total %= 5    // total = total % 5

var flags: int = 0
flags |= 4    // set a bit
flags &= 6    // mask bits
flags ^= 2    // toggle a bit
```

They work on any assignable target — a plain `var`, a struct field, a pointer's `.value`, an index:

```dlang
contador.value.n += 1   // through a pointer
placar[i] += pontos      // through an index
```

The full set is `+= -= *= /= %= &= |= ^=`. (The shift-assign forms `<<=` / `>>=` are not yet available; write `x = x << n` for those.) Like `++`/`--`, compound assignment requires a mutable target.

## Bitwise operators

For working at the bit level, DLang offers the conventional C set. These operate only on the integer types (`byte`, `short`, `int`, `long`) — never on `float`, `double`, or `boolean` — and, like arithmetic, both operands must already be the same integer type:

```dlang
val band: int = 0b1100 & 0b1010   // 0b1000 — and
val bor:  int = 0b1100 | 0b1010   // 0b1110 — or
val bxor: int = 0b1100 ^ 0b1010   // 0b0110 — xor
val bnot: int = ~0                // -1     — not (unary)
val shl:  int = 1 << 4            // 16     — shift left
val shr:  int = 256 >> 2          // 64     — shift right
```

Because DLang's integers are all **signed**, `>>` is an *arithmetic* (sign-extending) shift: `-8 >> 1` is `-4`, not a large positive number. There is no separate logical-shift operator; if you need unsigned semantics, mask the result explicitly.

Precedence follows the familiar C ladder, from loosest to tightest: `||` < `&&` < `|` < `^` < `&` < `== !=` < `< > <= >=` < `<< >>` < `+ -` < `* / %`. As always you can parenthesize for clarity — `(flags & mask) == mask` reads better than relying on the table.

## Integer literal bases

Integer literals may be written in decimal, hexadecimal (`0x`), binary (`0b`), or octal (`0o`). A `_` may be used as a digit separator in any base for readability; it is ignored by the compiler:

```dlang
val mask:  int = 0xFF          // 255
val flags: int = 0b1010_1010   // 170
val perms: int = 0o755         // 493
val big:   long = 0x1_0000_0000 // needs `long` — overflows `int`
```

A literal is typed as `int` by default, but a bare integer literal has no *fixed* width until context gives it one — so it **adapts** to the type it is used with. A literal that does not fit in 32 bits must be annotated (or `cast`) to `long`:

```dlang
val big: long = 0x1_0000_0000   // the literal adopts `long` from the annotation
```

### Literal adaptation in arithmetic

The same adaptation applies inside a binary operation: a bare integer literal takes on the *other* operand's integer type. This means the common cases just work, without a cast on the literal:

```dlang
var n: long = 5
val m: long = n + 1       // the `1` becomes `long`; no cast needed

var b: byte = 12
val masked: byte = b & 0xF   // `0xF` becomes `byte`
```

Only *literals* adapt. Two *typed values* of different widths still require an explicit `cast` — `intVar + longVar` is an error, because neither side is a literal the compiler can retype. This preserves the "no hidden coercion" rule (see [Static Typing](29-static-typing.md)) while removing the noise of casting constants.

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
