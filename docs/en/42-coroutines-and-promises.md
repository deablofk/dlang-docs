# Structured Concurrency — Tasks and Futures

DLang has **no stackful coroutines and no `Promise` type**. Its answer to
"compute a value on another thread and collect it later" is `Task(T)`, a
**structured** future: it is an owning handle whose lifetime is tied to a scope,
and it cannot outlive the scope that created it. This is the same MVS discipline
the rest of the language uses, applied to concurrency (SPEC §23.4).

This page describes the `Task(T)` type; the `spawn`/`await` surface that drives it
is in [spawn / await](43-async-await.md).

## `Task(T)` — a joinable future

A `Task(T)` represents a worker computing a `T`. It is a `nocopy` owning handle
with a `deinit` that **joins** the worker — so a task is *synchronized by
construction*:

- `await t` joins the worker and **moves** its `T` result out.
- If a task is never awaited, its `deinit` still joins the worker at scope exit
  (the result is computed and then dropped). A task can never be silently
  abandoned while its thread runs on.

```dlang
inline import("std/concurrency/task")

sumTo :: (n: int) -> int {
  var s: int = 0
  var i: int = 1
  while (i <= n) { s = s + i  i = i + 1 }
  return s
}

main :: () -> int {
  val a: Task(int) = spawn sumTo(100)   // runs on a worker
  val b: Task(int) = spawn sumTo(10)
  println(await a + await b)            // 5050 + 55, computed concurrently
  return 0
}
```

## Why structured (no detached futures)

Because `Task(T)` is affine and its `deinit` joins, the worker is guaranteed to
finish within the scope that spawned it. There is no way to leak a running thread
or to read a result before it is ready — the type system enforces the join. This
is what "structured concurrency" means: concurrency nests like scopes do.

```dlang
withResults :: () -> int {
  val t: Task(int) = spawn sumTo(1000)
  // ... other work, concurrent with the task ...
  return await t          // guaranteed joined here
}                         // (had we not awaited, deinit would join at this brace)
```

## Affine results move cleanly

A task can produce an owned value — the result is **moved** out of the worker on
`await`, never copied or shared:

```dlang
buildList :: (n: int) -> List(int) {
  var xs: List(int) = List(int).empty()
  var i: int = 0
  while (i < n) { xs.add(i)  i = i + 1 }
  return xs
}

main :: () -> int {
  val t: Task(List(int)) = spawn buildList(6)
  var xs: List(int) = await t      // the List is MOVED out of the worker
  println(xs.size())               // 6
  return 0
}
```

## Design rationale

- **No function coloring.** `spawn`/`await` are ordinary expressions, not a
  contagious `async` modifier. Any function can be spawned; nothing in a
  signature has to change.
- **No hidden runtime.** A `Task` is one OS thread (real pthreads), created when
  you `spawn` and joined when you `await` or when the handle drops. There is no
  scheduler running behind your back.
- **Safety for free.** Because a spawned closure goes through the same
  [send-check and move-in](41-concurrency.md) as any thread body, a task cannot
  capture a borrowed owner or share mutable state by accident.

## Related

- [spawn / await](43-async-await.md)
- [Multithreading and Concurrency](41-concurrency.md)
- [Channels and Message Passing](44-channels.md)

[← Index](README.md)
