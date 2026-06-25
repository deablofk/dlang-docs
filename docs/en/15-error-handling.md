# Error Handling

DLang has no exceptions in the throw-and-unwind sense. Errors are ordinary values returned alongside the result. A fallible function is marked with `throws` in its signature, and by convention the error is always the *last* value it returns; a `null` error means "everything went fine". This keeps error handling explicit and data-oriented — an error is just data flowing back through a return, never a hidden control-flow jump out of the function.

There are two ways to consume a fallible call: manual checking, and a `try`/`catch` block that is pure syntactic sugar over that manual check.

## Declaring errors

Errors are typically modelled as an [enum](16-enumerations.md), so the set of failure modes is a closed, named list the compiler can reason about.

```dlang
// definition of the errors
Erro :: enum {
  ArquivoNaoEncontrado,
  PermissaoNegada
}
```

## A function that can fail

The `throws` keyword in the return signature marks a function as fallible. Because the error is the last value, the natural reading of `-> throws (string, Erro)` is "returns a string on success, with `Erro` as its error channel". On success you return the value plus `null`; on failure you return a placeholder value plus the error.

```dlang
// function returning an error
// the error is always the last value because of 'throws'
lerArquivo :: (caminho: string) -> throws (string, Erro) {
  if (caminho == "") {
    return "", Erro.ArquivoNaoEncontrado
  }

  return "file contents here", null
}
```

The pair `(string, Erro)` is exactly a tuple — the same mechanism described in [Multiple Returns](11-multiple-returns.md) and [Tuples and Destructuring](38-tuples-and-destructuring.md). Error handling reuses that machinery rather than inventing a new one.

## Form 1: manual checking

The most direct style destructures the returned tuple into a value and an error, then tests the error against `null`. This is ideal when you want to handle one failure in isolation, right where it happens.

```dlang
// Form 1: Manual checking (useful for handling isolated errors)
val conteudo, err = lerArquivo("config.txt")

if (err != null) {
  println("Could not read the file: ${err}")
  return
}
println(conteudo)
```

Nothing is hidden here: the error is a normal variable, the `if` is a normal conditional, and control flow is fully visible. The cost is verbosity when you chain several fallible calls in a row.

## Form 2: the `try`/`catch` block

When you want to chain many operations without an `if` after each one, the `try`/`catch` block provides sugar over the manual pattern. The compiler knows each called function has `throws`, so inside `try` it automatically extracts the success value into your variable and invisibly generates the error check behind the scenes. If any call returns a non-null error, execution jumps straight to `catch`.

```dlang
// Form 2: the hybrid Try-Catch block (syntactic sugar)
// Useful for chaining several operations without polluting code with 'ifs'
try {
  // The compiler knows the function has 'throws'.
  // It extracts the success value directly into 'config'
  // and generates the error check invisibly behind the scenes.
  val config = lerArquivo("config.txt")
  val extra  = lerArquivo("theme.txt")

  // If any call above returns a non-null Erro,
  // execution jumps immediately to the catch block.
  println("Settings loaded successfully!")
  println(config)

} catch (err) {
  // The 'err' variable is injected automatically here by the compiler
  println("An error interrupted the try block: ${err}")
}
```

Notice that `val config = lerArquivo("config.txt")` inside `try` binds the *success* value directly, not the `(value, error)` tuple — the `try` desugaring peels off the error for you and short-circuits to `catch` on the first non-null one. The `err` parameter of `catch` is injected by the compiler.

Because Form 2 compiles down to exactly the Form 1 pattern, the two are semantically identical; `try`/`catch` is just the ergonomic choice when several fallible steps must happen in sequence.

## Matching on the error

Since `Erro` is an enum, a recovered error pairs naturally with [`match`](05-conditionals.md) to branch on the specific failure:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("the file vanished")
  Erro.PermissaoNegada      -> println("access denied")
  else -> println("ok")
}
```

## Design rationale

Errors-as-values keeps DLang honest: a function's signature tells the whole truth about how it can fail, and the `throws`/last-value convention makes the error channel unmistakable without inventing a separate type discipline. By building on tuples and enums — features the language already has for [multiple returns](11-multiple-returns.md) and [enumerations](16-enumerations.md) — error handling adds no new runtime machinery and no hidden stack unwinding. The `try`/`catch` block then layers convenience on top *as sugar only*, so you get readable chaining without ever giving up the guarantee that control flow is explicit and inspectable.

## Related

- [Enumerations](16-enumerations.md)
- [Multiple Returns](11-multiple-returns.md)
- [Tuples and Destructuring](38-tuples-and-destructuring.md)

[← Index](README.md)
