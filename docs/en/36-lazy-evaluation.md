# Lazy Evaluation

> Status: Partial (only `lazy val` is implemented).

Lazy evaluation in DLang has two faces. One is implemented and is the only active laziness mechanism in the language: `lazy val`. The other — lazy iterators over collections — is a design that has been deliberately *parked* and is documented here only as a future-reference note. Collections stay fully eager.

## Face 1 — `lazy val` (supported)

A `lazy val` is not computed at its declaration. Its initializing expression runs on the **first access**, and from then on the result is cached (memoized): subsequent reads just return the stored value.

```dlang
lazy val config = carregarConfig()   // carregarConfig() does NOT run here

usar :: () {
  println(config.tema)     // <- carregarConfig() runs NOW (first access)
  println(config.idioma)   // <- already cached: does not re-run, just reads
}
```

### Cost

The value lives on the stack alongside an internal "already-computed?" flag. On the first access the expression runs, the result is stored, and the flag is set. Every later access checks the flag and reads the cached value. There is no heap allocation and no garbage collector involved — laziness here is a stack-resident value plus a boolean.

This makes `lazy val` the right tool for an expensive value you might not need on every path: you pay for it once, only if and when it is actually read.

## Face 2 — lazy iterators (parked / not implemented)

> Status: Partial — this face is a parked design note, not active behavior.

`List`, `Map`, and arrays remain **100% eager**. Nothing in this section is active; it is kept only as a record of the design for a possible future reopening.

### How the eager-vs-lazy distinction would work

The difference between eager and lazy is *not* a keyword. It is whether the method **contains the loop** or not.

An **eager** method — the current behavior of `List` — runs the `for` immediately and materializes a result:

```dlang
// EAGER (current List behavior): the 'for' runs now and materializes
List(T).map(R) :: (f: (T) -> R) -> List(R) {
  var saida = List(R).empty()
  for (item : _) saida.add(f(item))   // <- work happens HERE, now
  return saida
}
```

A **lazy** method would have no loop at all. It would merely wrap the source and the function in a small struct, deferring all work to a `proximo()` ("next") call that pulls one element at a time:

```dlang
// LAZY (parked): map has NO loop. It only wraps source + function in a struct.
Iter(T) :: interface {
  proximo :: () -> (T, boolean)   // (value, hasNext)
}

Iter(T).map(R) :: (f: (T) -> R) -> Iter(R) {
  return MapIter(R) { fonte: _, f: f }   // <- zero work, just stores
}

MapIter(T, R).proximo :: () -> (R, boolean) {
  val (item, temMais) = _.fonte.proximo()   // pulls ONE element from the source
  if (!temMais) return (zero(R), false)
  return (f(item), true)                      // transforms just THAT one
}
```

How it would be used: `.iter()` enters lazy mode, the intermediate stages only *compose*, and `.collect()` materializes once, with a single allocation:

```dlang
val resultado = nums
  .iter()                // enter lazy mode — zero cost, nothing allocated
  .filtrar { _ > 0 }     // only COMPOSES
  .map      { _ * 2 }    // likewise
  .collect()             // HERE everything is materialized, once
```

### Why it is parked

1. **No explicit laziness marker.** The only signal that a chain is lazy would be its return type (`Iter` vs `List`) — far too implicit for a language whose principle is "explicit over implicit".
2. **The "zero cost" depends on the optimizer.** Fusing the `proximo()` chain into a single loop relies on monomorphization plus inlining. Without mature inlining there is real per-element call overhead — a debt that lives in the compiler backend, not in the surface design.

To reopen this later would require an explicit `Lazy(T)` marker in the return type *and* a mature inliner. It would never be the default, and it would never touch the eager `List`/`Map` API.

## Design rationale

`lazy val` earns its place because its cost is fully visible and stack-resident: one expression, computed at most once, cached behind a flag, no heap. Lazy iterators were held back precisely because they would hide both their laziness (behind a return type) and their performance guarantee (behind an optimizer pass) — two implicit costs the language refuses to ship by default.

## Related

- [Higher-Order Functions](35-higher-order-functions.md)
- [Arrays and Lists](07-arrays-and-lists.md)
- [Variables and Scope](04-variables-and-scope.md)
- [Generics](32-generics.md)

[← Index](README.md)
