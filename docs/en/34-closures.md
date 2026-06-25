# Closures and Anonymous Functions

An anonymous function is a function literal with no name: exactly the same syntax as a named function, minus the `nome ::` part. A *closure* is such a literal that captures variables from the surrounding scope. DLang's central promise here is that the cost of a closure is always visible: a closure that does not outlive its scope is free, and one that does requires an explicit allocator.

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

The common case is a closure that does not escape: it is created, used, and discarded inside the same scope. This costs nothing. It lives on the stack and captures its variables *by reference*; no allocator is involved.

```dlang
// non-escaping closure — used and discarded within the scope.
// zero cost: lives on the stack, captures by reference, no allocator.
lista.map({ _ * taxa })
```

## Capture and memory: the escaping case

A closure *escapes* when it is returned or stored somewhere that outlives the function that created it. At that point its captured state can no longer live on the stack, so — exactly like any other data that must survive a function — it needs an explicit allocator. You request the allocation with `_alloc.closure({ ... })`, which returns a `Ptr` to the closure, and you call it through `.value`:

```dlang
// escaping closure: returned/stored beyond the scope.
// it needs an explicit allocator, like any data that outlives the function.
fazContador :: () -> Ptr((() -> int)) {
  var n = 0
  // captures 'n' and outlives the function -> explicit, clear allocation
  return _alloc.closure({ n = n + 1; return n })
}
```

The returned value is a `Ptr((...) -> ...)`, so it is invoked through `.value`, just like any heap-allocated pointer.

## Design rationale

A function literal is a named function without the name — one rule, zero new syntax. The short `{ _ * 2 }` reuses the same placeholder as the `for` loop, so a one-argument lambda stays lean; two or more arguments, or explicit types, fall back to the full form.

The heart of the design is the escape distinction. A non-escaping closure is free (stack); an escaping one takes an explicit allocator. The language never allocates heap *hidden* behind a closure — the sin of many garbage-collected languages. You see the `_alloc` and you know the cost. If you would rather hand the lifetime to the garbage collector, `_gcAlloc` works here too.

## Related

- [Function Pointers](33-function-pointers.md)
- [Higher-Order Functions](35-higher-order-functions.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Manual Memory Management](13-manual-memory.md)
- [Garbage Collection](14-garbage-collection.md)

[← Index](README.md)
