# Metaprogramming and Reflection

DLang's compile-time power flows through **one unified system** instead of a scattered bag of special features. Everything the compiler does on your behalf is expressed as either an *annotation* or a *directive* — the very same mechanism that `@intrinsic` already uses for concurrency (see [Multithreading and Concurrency](41-concurrency.md)).

## Annotations (`@`) and directives (`#`)

The two halves of the system are easy to keep apart by where they go and what they do:

- **`@nome(args)` — an annotation.** Metadata attached to a *declaration* (function, struct, field, parameter). It is *declarative*: it does nothing on its own, it just labels the declaration so the compiler and reflection can read it later.
- **`#nome(args)` — a directive.** An *action* performed at compile time, at the *use site*. It is *imperative*, and it includes invoking macros (see [Macros and Code Expansion](46-macros.md)).

Built-in annotations: `@intrinsic`, `@inline`, `@naoInline`, `@comptime`, `@macro`, `@externo("C")`, `@reflete`, `@anotacao`, `@depreciado("msg")`.

Built-in directives: `#rodar`, `#se`, `#assert`, `#<macro>`.

## Types are compile-time values

A type is an ordinary value that exists at compile time, so it can be stored, compared, and computed with — the same fact that powers generics (`T: type`, `N: int`).

```dlang
val t: type = int
val ehNumerico: boolean = (t == int || t == float)
```

## Running code in the compiler: `@comptime` + `#rodar`

Annotate a function `@comptime` to say it *may* run during compilation, then force a particular call to run there with the `#rodar` directive. The result is baked into the binary at zero runtime cost.

```dlang
@comptime                                  // the function MAY run at compile time
fatorial :: (n: int) -> int = if (n <= 1) 1 else n * fatorial(n - 1)

const val TABELA: int = #rodar fatorial(10) // 3628800 burned into the binary, 0 runtime cost
```

The `#se` directive selects code at compile time — conditional compilation, resolved before the program runs:

```dlang
#se (PLATAFORMA == "linux") {              // chosen at compile time
  abrirArquivo :: (caminho: string) -> int = syscallLinux(caminho)
}
```

## Compile-time reflection: always available

`infoDe(T)` returns a `TipoInfo` describing a type — its name, its fields (each with a name, type, and annotations), and so on. This is available for any type, with no opt-in, because it is consumed entirely at compile time and leaves nothing behind at runtime.

```dlang
imprimirCampos :: (T: type) {
  for (campo : infoDe(T).campos) {
    println("${campo.nome}: ${campo.tipo}")
  }
}
imprimirCampos(Pessoa)                      // nome: string / idade: int / ativo: boolean
```

## Runtime reflection: opt-in with `@reflete`

By default there is **no RTTI** — type information does not exist at runtime, so it costs nothing (data-oriented, zero weight). When you genuinely need to inspect types during execution, annotate the type with `@reflete` and the compiler embeds its `TipoInfo` into the binary.

```dlang
// Without @reflete, type info simply isn't present at runtime -> zero cost.
@reflete
Pessoa :: struct { nome: string, idade: int, ativo: boolean }
```

## User annotations with `@anotacao`

You can declare your own annotations. An annotation is itself a body-less declaration marked `@anotacao`; afterwards you can attach it to declarations, and macros or `@comptime` functions read it back through reflection.

```dlang
@anotacao
json :: (nome: string)                      // declares the 'json' annotation

Config :: struct {
  @json("max_conn") maxConexoes: int        // uses the annotation on a field
  @json("host")     host: string
}
```

A macro or `@comptime` function reads these annotations via reflection and generates, for example, a serializer — with no RTTI and no runtime cost. See [Macros and Code Expansion](46-macros.md) for the generation side.

## Design rationale

Folding every compile-time capability into two constructs — declarative annotations and imperative directives — means there is one mental model to learn instead of a dozen ad-hoc features, and that model is the same one used for intrinsics and macros. Making reflection compile-time-first with opt-in RTTI keeps the data-oriented promise intact: you pay for runtime type information only when you ask for it by name with `@reflete`.

## Related

- [Macros and Code Expansion](46-macros.md)
- [Runtime Compilation](47-runtime-compilation.md)
- [Generics and Parametric Programming](32-generics.md)
- [Multithreading and Concurrency](41-concurrency.md)

[← Index](README.md)
