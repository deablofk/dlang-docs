# Runtime Compilation

> Status: Absent.

Compiling code at runtime — JIT compilation, `eval`, or generating machine code while the program runs — is **not a feature of DLang**. The core language is AOT (ahead-of-time): a program is fully compiled before it runs.

## Why the core is AOT only

Two reasons make runtime compilation a poor fit for a systems language:

1. **Binary size and predictable cost.** Embedding a compiler in the final binary contradicts the goal of a small executable with predictable, visible cost. A systems language should not ship a code generator inside every program.
2. **Most "code generation" belongs at compile time.** The cases people reach for runtime compilation to solve are handled *earlier* — at compile time — by `@comptime`, `#rodar`, and macros (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md) and [Macros and Code Expansion](46-macros.md)). That work has zero runtime cost.

## Do not confuse compile-time with runtime

It is worth being precise about the two categories, because they sound similar but are opposites:

- **`#rodar` / `@comptime`** run in the **compiler** (compile time). These are fully **supported** — they are how DLang generates code and folds constants ahead of time.
- **JIT / `eval(string)`** compile at **runtime**. These are **not native** to the language.

The presence of strong compile-time evaluation is exactly what removes the need for a runtime compiler in the common case.

## A possible future escape hatch

If a program genuinely needs runtime compilation, the path is an **opt-in standard-library module** that embeds the compiler and exposes something explicit — for example a `Compilador.compilar(fonte)` that returns a function pointer generated at runtime. This would be a heavyweight, clearly-marked library, **never** part of the core, and the vast majority of programs would never touch it.

```dlang
exemploHipotetico :: () {
  // val fn = Compilador.compilar("somar :: (a,b:int)->int = a+b")  // via lib, not core
  // fn.value()
}
```

## Design rationale

Keeping the core strictly AOT preserves the two properties a systems language sells: small binaries and predictable cost. Because DLang already runs arbitrary code in the compiler through `@comptime`, `#rodar`, and macros, "generate code from data" is solved before the program ever starts — at no runtime cost. Runtime compilation is therefore left out of the core on purpose, available, if ever needed, only as an explicit, heavyweight library.

## Related

- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)
- [Macros and Code Expansion](46-macros.md)

[← Index](README.md)
