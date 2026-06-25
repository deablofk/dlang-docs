# Higher-Order Functions

A higher-order function is one that takes a function as an argument or returns one. In DLang these are not compiler magic — they are ordinary [generic](32-generics.md) methods on `List(T)`, written with the same [function-pointer types](33-function-pointers.md) and [lambdas](39-lambda-expressions.md) you already have. The three workhorses are `map`, `filtrar`, and `reduce`.

## map, filtrar, reduce

`map` transforms each element and produces a new `List`. Note that it does not invent an allocator: it reuses the one the source list already carries (`_.alloc`), so the result lives in the same arena as its source.

```dlang
// map: defined with generics, reuses the allocator the List itself holds
List(T).map(R) :: (transform: (T) -> R) -> List(R) {
  var saida = List(R).init(_.alloc)   // no new allocator: inherits the source list's
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
  var saida = List(T).init(_.alloc)
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
var nums = List(int).init(_alloc)
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

A higher-order function can also *return* a function. Since the returned function captures local state and outlives its scope, this is an escaping closure and therefore needs an explicit allocator — faithful to the rule from [closures](34-closures.md):

```dlang
// HOF that returns a function: an escaping closure -> explicit allocator
// returns a function that remembers 'fator'
multiplicador :: (fator: int) -> Ptr((int) -> int) {
  return _alloc.closure({ _ * fator })   // captures 'fator' and outlives -> allocates
}

val triplicar = multiplicador(3)
triplicar.value(10)   // 30 (called via .value, it is a pointer to an allocated closure)
```

## Design rationale

These functions stay in the standard library as plain generic methods, which means the language core has nothing special to know about them. By inheriting the source list's allocator they keep memory ownership obvious, and by having `reduce` allocate nothing they make the cheap aggregation cheap.

There is one cost worth registering: a pipeline like `filtrar().map()` creates an **intermediate List at each stage** — each stage allocates. That is precisely the problem the parked lazy-iterator design would solve later by fusing the stages into a single loop. See [Lazy Evaluation](36-lazy-evaluation.md) for that future, parked optimization.

## Related

- [Function Pointers](33-function-pointers.md)
- [Closures and Anonymous Functions](34-closures.md)
- [Lazy Evaluation](36-lazy-evaluation.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Generics](32-generics.md)

[← Index](README.md)
