# Macros and Code Expansion

A macro is a function that runs **inside the compiler**, takes *code* (an AST) as input, and returns *code* as output. It is marked with the `@macro` annotation at its definition and invoked with `#` at its use site. The defining distinction from compile-time evaluation is sharp: `@comptime` evaluates **values**, while `@macro` transforms **code** (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)).

## Building code: `quote` and `$`

Inside a macro you build new code with `quote { ... }`, which produces an AST, and you splice an existing piece of code into it with `$x`. The `$` deliberately mirrors the `${}` of the string interpolation the language already uses — in both cases `$` means "drop this value in here."

```dlang
@macro
debug :: (expr: Codigo) -> Codigo {
  // generate code that prints the EXPRESSION and its VALUE
  return quote {
    println("${ texto($expr) } = ${ $expr }")   // texto() = the textual form of the AST
  }
}

calcular :: () {
  val x = 10
  #debug(x * 2)        // expands at compile time to: println("x * 2 = ", x * 2)
}
```

The macro receives the *unevaluated* expression `x * 2` as a `Codigo` value. It can render it as text (`texto`) and also splice it back as live code, producing a print statement that shows both the source and the result.

## Generating declarations from annotations

Because a macro runs in the compiler, it can read reflection (`infoDe`) and the annotations attached to a type (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)), then emit whole declarations. Here a macro generates a `serializarJson` method for any struct by walking its fields and reading their `@json` annotations.

```dlang
@macro
derivarJson :: (T: type) -> Codigo {
  var corpo = quote { }
  for (campo : infoDe(T).campos) {
    val chave = campo.anotacao(json).nome       // reads the "max_conn" from @json("max_conn")
    corpo = quote {
      $corpo
      escrever($chave, _.${campo.nome})
    }
  }
  return quote {
    ${T}.serializarJson :: () -> string {
      $corpo
    }
  }
}

#derivarJson(Config)   // one line generates the whole method at compile time, 0 runtime cost
```

The loop accumulates code by re-quoting: each iteration splices the previous `$corpo` and adds one more `escrever` line. The final `quote` wraps the accumulated body in a method declaration attached to the type `T`.

## Hygiene and the design boundary

Macros are **hygienic**: names introduced inside a macro do not leak into the caller, and they do not accidentally capture the caller's variables. They operate on a **typed AST**, not on raw text, so the compiler understands what they produce. And they can **only generate code** — a macro cannot touch files, read input, or perform arbitrary I/O in the compiler.

This is the precise opposite of C's text macros: where a C macro is blind textual substitution that can produce nonsense, a DLang macro is a typed, hygienic, side-effect-free code transformation. Keeping macros to pure code generation keeps compilation deterministic and safe.

## Design rationale

Splitting compile-time work into "evaluate a value" (`@comptime`) and "transform code" (`@macro`) gives each job a clean tool while reusing one annotation/directive system (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)). Building code with `quote`/`$` reuses the interpolation intuition you already have, and restricting macros to hygienic, typed, I/O-free transformations keeps the metaprogramming powerful without making the compiler unpredictable.

## Related

- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)
- [Runtime Compilation](47-runtime-compilation.md)
- [Generics and Parametric Programming](32-generics.md)

[← Index](README.md)
