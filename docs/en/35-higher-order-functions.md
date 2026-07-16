# Higher-Order Functions

A higher-order function is one that takes a function as an argument or returns one. In DLang these are not compiler magic — they are ordinary [generic](32-generics.md) methods on `List(T)`, written with the same [function-pointer types](33-function-pointers.md) and [lambdas](39-lambda-expressions.md) you already have. The three workhorses are `map`, `filtrar`, and `reduce`.

## map, filtrar, reduce

`map` transforms each element and produces a new `List`. It does not take an allocator parameter: the new list grows from the current allocator, the same ambient context every allocation uses (see [Dynamic Allocation](18-dynamic-allocation.md)).

```dlang
// map: defined with generics; the new list grows from the current allocator
List(T).map(R) :: (transform: (T) -> R) -> List(R) {
  var saida = List(R).empty()   // grows from the current allocator (ambient context)
  for (item : _) {
    saida.add(transform(item))
  }
  return saida
}
```

`filtrar` keeps only the elements that satisfy a predicate and returns a subset — again into a freshly allocated `List`:

```dlang
// filtrar: same input shape, returns a subset
List(T).filtrar :: (pred: (T) -> boolean) -> List(T) {
  var saida = List(T).empty()
  for (item : _) {
    if (pred(item)) saida.add(item)
  }
  return saida
}
```

`reduce` (also called *fold*) collapses the whole list into a single value. Crucially, it allocates **nothing** — it only threads an accumulator through the loop:

```dlang
// reduce/fold: aggregates everything into one value — allocates nothing
List(T).reduce(R) :: (inicial: R, op: (R, T) -> R) -> R {
  var acc = inicial
  for (item : _) acc = op(acc, item)
  return acc
}
```

So `map` and `filtrar` are *eager* — they run the loop now and materialize a new `List` — while `reduce` produces a scalar and allocates nothing.

## The ladder of lambda forms

Calling these functions shows the three lambda forms as a ladder of verbosity, from shortest to most explicit:

```dlang
var nums = List(int).empty()
// ... nums populated

// 1 argument -> placeholder '_'
val dobrados = nums.map({ _ * 2 })
val positivos = nums.filtrar({ _ > 0 })

// n arguments -> named, types inferred from context, separated by '->'
val soma = nums.reduce(0, { acc, x -> acc + x })

// full form when you want explicit types
val soma2 = nums.reduce(0, (acc: int, x: int) -> int { return acc + x })
```

## Pipelines

Because each of `map` and `filtrar` returns a `List`, calls chain into a pipeline that reads top to bottom:

```dlang
// pipeline, read top to bottom
val resultado = nums
  .filtrar({ _ > 0 })
  .map({ _ * 2 })
  .reduce(0, { acc, x -> acc + x })
```

## Returning a function

A higher-order function can also *return* a function. The returned closure captures what it needs **by value** and its environment moves to the heap, managed by the compiler like any other owned storage — no allocator, no pointer, no special call syntax ([Closures](34-closures.md)):

```dlang
// HOF that returns a function that remembers 'fator'
multiplicador :: (fator: int) -> (int) -> int {
  return (x: int) -> int = x * fator
}

val triplicar = multiplicador(3)
triplicar(10)   // 30 — an ordinary function value, called directly
```

## Design rationale

These functions stay in the standard library as plain generic methods, which means the language core has nothing special to know about them. Stages that build a new `List` return an owning value that dies at its last use like any other, and `reduce` allocates nothing, keeping aggregation cheap.

There is one cost worth registering: a pipeline like `filtrar().map()` creates an **intermediate List at each stage** — each stage allocates. That is precisely the problem the parked lazy-iterator design would solve later by fusing the stages into a single loop. See [Lazy Evaluation](36-lazy-evaluation.md) for that future, parked optimization.

## Related

- [Function Pointers](33-function-pointers.md)
- [Closures and Anonymous Functions](34-closures.md)
- [Lazy Evaluation](36-lazy-evaluation.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Generics](32-generics.md)

[← Index](README.md)
