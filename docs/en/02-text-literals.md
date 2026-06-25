# Text Literals

Text in DLang is represented by the `String` type. The language gives you several literal forms for writing strings directly in source — from plain quoted text, through escape sequences and Unicode, to multi-line blocks and interpolated templates. All of them produce ordinary `String` values; they are surface conveniences, not different types.

## Plain strings and escapes

The simplest literal is text between double quotes. Inside it you can use backslash escape sequences, the most common being `\n` for a newline:

```dlang
val a: String = "Simple text"
val b: String = "Simple text with line break\n"
```

## Unicode escapes

To embed a character by its Unicode code point, use the `\u` escape followed by the hexadecimal value. For example `A` is the code point for the letter `A`:

```dlang
val c: String = "Simple text with unicode: A"
```

This is the portable way to write characters that may be awkward to type directly, while keeping the source file in plain ASCII if you wish.

## Triple-quoted blocks

For text that spans multiple lines, use a **triple-quoted block** delimited by `"""`. Everything between the opening and closing triple quotes is taken literally, including line breaks, so you do not have to pepper the string with `\n`:

```dlang
val d: String = """Text Block with multiple lines"""
```

Triple-quoted blocks are ideal for embedded documents, SQL, templates, or any literal where the layout is part of the content.

## Interpolation

A literal can embed the value of an expression using `${...}`. The expression inside the braces is evaluated and its result is spliced into the string at that position:

```dlang
val e: String = "Formatted string: ${a}"
```

Here `${a}` is replaced by the contents of the `a` variable. Any expression is allowed inside the braces, not just a bare name. This `${}` syntax is deliberately the same shape that reappears in macros as the `$` splice operator (see [Macros](46-macros.md)) and in pattern interpolation — one visual idea reused across the language.

## Design rationale

Offering distinct literal forms keeps each common case ergonomic without inventing new types: a quoted literal, a Unicode escape, a triple-quoted block, and an interpolated template all yield the same `String`. Interpolation in particular removes the noise of manual concatenation while staying explicit about exactly where a value is injected. Reusing the `${}` shape for string interpolation, and `$` for AST splicing in macros, means a single mental model — "this marks the hole where a value goes" — covers both runtime text and compile-time code generation.

## Related

- [Primitive Types](01-primitive-types.md)
- [Variables and Scope](04-variables-and-scope.md)
- [Macros](46-macros.md)

[← Index](README.md)
