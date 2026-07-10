# Variables and Scope

DLang draws a sharp, deliberate line between three kinds of bindings: mutable variables, immutable runtime values, and true compile-time constants. The keyword you choose communicates intent to both the reader and the compiler, and that intent is enforced. This is the language's "explicit over implicit" philosophy applied to the most basic act in programming — naming a value.

## The three bindings

```dlang
// variable: may be reassigned
var a: int = 0

// immutable value: bound once at runtime, never reassigned
val b: int = 0

// constant: a true compile-time constant
const val c: int = 0
```

A `var` is a mutable binding. You can reassign it, and operators like `++` may change it in place. Use `var` only when the value genuinely needs to change over time, such as a loop counter.

A `val` is an immutable runtime binding. Its value is computed when control reaches the declaration, but once assigned it can never be reassigned. The data may still be produced by ordinary runtime work (a function call, a computation) — what is fixed is the *binding*, not the moment of computation. This is the form you should reach for by default.

A `const val` is a stronger promise: the value is a true constant known at **compile time**. It is the right choice for fixed parameters of your program — mathematical constants, version numbers, fixed sizes — and it ties into the compile-time machinery of the language, where constants and types are bound with `::` and computed before the program ever runs.

## `::` versus `val`

It is worth contrasting these runtime bindings with the `::` form you will see throughout the documentation. `::` binds **compile-time constants** — functions, types, namespaces — names that are fully resolved by the compiler. `val` and `var`, by contrast, name **runtime** data. So `somar :: (...)` defines a function (a compile-time entity), while `val resultado = somar(2, 3)` binds a runtime value. Keeping these in separate syntax makes it immediately clear, when reading code, whether a name refers to something fixed at build time or something that lives during execution.

## Top-level bindings

All three forms may also appear at **file scope**, outside any function. A top-level `const val` (or plain `val`) is a compile-time constant with no runtime storage — each use inlines its value. A top-level `var` is a genuine **global variable**: it has real storage that persists for the whole program and is shared across functions.

```dlang
var requestCount: int = 0        // a global, shared mutable counter

bump :: () { requestCount += 1 }
```

A global `var` is zero-initialized by default (a constant scalar initializer like `= 5` is honored). A non-constant initializer is **not** run at program start, so if a global needs computed setup, initialize it lazily on first use rather than in the declaration.

## Scope

Bindings are lexically scoped to the block in which they are declared, delimited by mandatory braces. A name introduced inside a block is visible from its declaration to the end of that block and not beyond. Because the language is expression-oriented, blocks themselves can produce values (see [Conditionals](05-conditionals.md)), but the visibility rule is the same classic lexical one: inner scopes can see outer names, outer scopes cannot see inner names.

## Design rationale

Most languages default to mutability and make immutability the special case; DLang nudges you the other way by making `val` the natural default and `var` a conscious choice. That reduces accidental mutation bugs and makes data flow easier to follow. Splitting `val` from `const val` separates "I will not reassign this" from "this is a compile-time constant," which matters in a systems language where the difference decides whether a value occupies runtime storage or is baked into the binary. And keeping `::` reserved for compile-time bindings means the reader never has to guess which world a name belongs to.

## Related

- [Primitive Types](01-primitive-types.md)
- [Arithmetic Operators](03-arithmetic-operators.md)
- [Conditionals](05-conditionals.md)
- [Functions and Procedures](09-functions.md)
- [Type Inference](31-type-inference.md)

[← Index](README.md)
