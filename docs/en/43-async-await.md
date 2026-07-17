# spawn / await

DLang expresses asynchronous work with two **contextual keywords**, `spawn` and
`await`, over the `Task(T)` type ([Structured Concurrency](42-coroutines-and-promises.md)).
They are not a colored `async`/`await` in the Rust/JS sense: there is no
suspendable function color, no executor to install, and no function-signature
change. `spawn e` runs `e` on a worker thread; `await t` joins and takes the
result.

Both are *contextual* — an ordinary identifier named `spawn` or `await` still
parses as itself. They only act as keywords when followed by an expression.

## `spawn e` — run on a worker

`spawn e` evaluates `e` on a fresh worker and yields a `Task(T)`, where `T` is the
type of `e`. The element type is **inferred**, so no annotation is required:

```dlang
inline import("std/concurrency/task")

val a = spawn sumTo(100)      // a : Task(int)  — inferred
val b: Task(int) = spawn sumTo(10)   // annotation optional
```

`spawn` is an ordinary prefix expression, so it works in **any position**, not
just a binding:

```dlang
// as the receiver of await — run and immediately wait
val n: int = await spawn compute(x)

// as a call argument
useTask(spawn sumTo(5))

// returned directly
makeTask :: () -> Task(int) = spawn sumTo(50)
```

Under the hood the compiler expands `spawn e` to `Task(T).start(() -> T = e)`; you
never write that by hand.

## `await t` — join and take the result

`await t` joins `t`'s worker and **moves** the computed `T` out. It is written as
a prefix expression:

```dlang
val total: int = await a + await b     // both joined, results summed
```

Awaiting is the point where the worker's result becomes available; before that,
the task is simply running. A task that is never awaited is still joined when its
handle drops (structured concurrency — see chapter 42).

## Captures are checked and moved in

Because `spawn e` becomes a thread body, `e`'s captures go through the same
[send-check and move-in](41-concurrency.md) as any thread closure:

```dlang
listSum :: (sink xs: List(int)) -> int {
  var s: int = 0
  for (x : xs) { s = s + x }
  return s
}

main :: () -> int {
  var xs: List(int) = List(int).empty()
  xs.add(3); xs.add(4); xs.add(5)
  val s: int = await spawn listSum(xs)   // xs is MOVED into the worker
  // xs may not be used here — E_USE_AFTER_MOVE
  println(s)                             // 12
  return 0
}
```

A copyable capture is snapshotted; an owned affine capture is moved in; a borrowed
affine capture is `E_NOT_SENDABLE`. See [Multithreading](41-concurrency.md) for
the full rules.

## Why not a colored `async`/`await`?

- **No function coloring.** `spawn`/`await` are expressions, so a spawned function
  is an ordinary function — its signature does not change and callers are not
  forced to become async too.
- **No executor.** A `Task` is backed by one real OS thread; there is no runtime
  to configure or start.
- **Structured by default.** `await` (or the task handle dropping) always joins,
  so a worker cannot outlive its scope.

## Related

- [Structured Concurrency — Tasks and Futures](42-coroutines-and-promises.md)
- [Multithreading and Concurrency](41-concurrency.md)
- [Channels and Message Passing](44-channels.md)

[← Index](README.md)
