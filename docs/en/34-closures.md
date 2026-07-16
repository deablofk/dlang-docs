# Closures and Anonymous Functions

An anonymous function is a function literal with no name: exactly the same syntax as a named function, minus the `nome ::` part. A *closure* is such a literal that captures variables from the surrounding scope. DLang's central promise here is that the cost of a closure is always visible: a closure that does not outlive its scope is free, and one that does moves its captured snapshot to the heap, owned and released by the compiler like any other value.

## Three forms of literal

The full form mirrors a named function — a parameter list, a return type, and a body. There is both a block form and an expression form:

```dlang
// 1. full anonymous literal — the same shape as a function, just nameless
val dobro = (x: int) -> int { return x * 2 }
val dobro = (x: int) -> int = x * 2   // expression form, like a named function
```

For the common one-argument case there is a short form that uses the universal placeholder `_` as the implicit argument:

```dlang
// 2. short form with the placeholder
lista.map({ _ * 2 })     // '_' is the implicit argument
lista.filtrar({ _ > 0 })
```

The placeholder `_` is the same one used in the [`for` loop](06-loops.md) and in [pattern matching](37-pattern-matching.md): the language's universal "the unnamed thing". The full [ladder of lambda forms](39-lambda-expressions.md) is documented under lambda expressions.

## Capturing the surrounding scope

A closure reads variables that live outside its own body. The capture is implicit in the code but explicit in cost, as the next section shows:

```dlang
// 3. closure: captures variables from the surrounding scope
calcularDescontos :: () {
  val taxa = 0.1   // local variable
  val aplicar = (preco: float) -> float {
    return preco - (preco * taxa)   // 'taxa' is captured
  }

  println(aplicar(100.0))
}
```

## Capture and memory: the non-escaping case

The common case is a closure that does not escape: it is created, used, and discarded inside the same scope. This costs nothing: the environment lives on the stack, and the captured values are snapshots of the bindings in scope.

```dlang
// non-escaping closure — used and discarded within the scope.
// zero cost: its environment lives on the stack.
lista.map({ _ * taxa })
```

## Capture and memory: the escaping case

A closure *escapes* when it is returned or stored somewhere that outlives the function that created it. That is an ordinary, supported thing to do — the closure is a plain value of function type, its captured environment moves to the heap, and the compiler manages that storage like any other owned value ([Memory Safety](14a-memory-safety.md)). There is no allocator call, no pointer, and no special invocation syntax:

```dlang
// escaping closure: returned beyond the scope, called directly
multiplicador :: (fator: int) -> (int) -> int {
  return (x: int) -> int = x * fator     // captures 'fator' and outlives the frame
}

val triplicar = multiplicador(3)
val t = triplicar(10)                    // 30
```

Consistent with Mutable Value Semantics, a capture is a **by-value copy** — a closure snapshots the bindings it uses, and calling it never mutates the enclosing (or a shared) environment. State that must evolve across calls belongs in a value you can see: a `nocopy` struct with a method, not a hidden closure cell.

## Design rationale

A function literal is a named function without the name — one rule, zero new syntax. The short `{ _ * 2 }` reuses the same placeholder as the `for` loop, so a one-argument lambda stays lean; two or more arguments, or explicit types, fall back to the full form.

The heart of the design is the escape distinction. A non-escaping closure is free — its environment lives on the stack. An escaping one heap-allocates its captured snapshot, and the compiler owns that storage the same way it owns a `string`'s buffer. By-value capture is the closure-shaped face of Mutable Value Semantics: there is no aliased environment to dangle or race on, so closures need none of the lifetime machinery they need in reference-semantics languages.

## Related

- [Function Pointers](33-function-pointers.md)
- [Higher-Order Functions](35-higher-order-functions.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Memory Safety](14a-memory-safety.md)
- [Garbage Collection](14-garbage-collection.md)

[← Index](README.md)
