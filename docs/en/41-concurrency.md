# Multithreading and Concurrency

DLang's concurrency is **data-race free by construction**. A data race needs two
threads with *aliased mutable access* to one datum. Under Mutable Value Semantics
there is no aliasing — a value handed to another thread is **copied or moved,
never shared** — so the ingredient a race requires is simply absent. This is
Hylo's concurrency model, and DLang inherits it; the compiler's job is to turn
that from an accident of how closures capture into a **checked** guarantee. The
full specification is SPEC §23.

The primitives are ordinary standard-library code (`std/concurrency/*.dlang`)
over real pthreads. Nothing is hidden: there is no background runtime and no
global scheduler.

## OS threads — `Thread`

`Thread.start` runs a closure on a fresh OS thread and returns a handle;
`join` waits for it, `detach` lets it run unowned.

```dlang
inline import("std/concurrency/thread")

work :: () -> () = { println("running on another thread") }

main :: () -> int {
  val t: Thread = Thread.start(work)
  t.join()                     // wait for it to finish
  return 0
}
```

The body parameter is declared `sending` (see below), which is what subjects its
captures to the safety check.

## What may cross a thread — the send-check

A closure handed to a thread captures **by value**. Whether a capture may cross
the boundary is decided at compile time, on every build:

- **Copyable, deinit-free values** (`int`, a genuinely-copyable view) are sent by
  **snapshot** — each thread gets its own independent copy.
- An **owned affine value** (a local, or a `sink`/`sending` parameter) is sent by
  **move**: the thread takes ownership and the outer scope relinquishes it. A
  later use in the outer scope is `E_USE_AFTER_MOVE`.
- A **borrowed affine value** (a `borrow`/`inout` parameter) or a **projection**
  is **not sendable** — you cannot move what you do not own, and a by-value
  capture would alias the caller's buffer: `E_NOT_SENDABLE`.

```dlang
spawnList :: (xs: List(int)) -> () {     // xs is a BORROW
  worker :: () -> () = { println(xs.size()) }
  val t = Thread.start(worker)           // E_NOT_SENDABLE — 'xs' is borrowed
  t.join()
}
```

To move an owned value into the thread, own it (a local, or take it `sink`):

```dlang
consume :: (sink xs: List(int)) -> () {
  worker :: () -> () = { println(xs.size()) }   // xs MOVED into the thread
  val t = Thread.start(worker)
  t.join()
  // using xs here would be E_USE_AFTER_MOVE — the thread owns it now
}
```

The moved-in owner is reclaimed by the thread body when it finishes — no leak,
allocator-balanced.

## The general boundary — `sending` parameters

The send-check is **not special to `Thread.start`**. Any API that takes a closure
onto another thread opts in by declaring a **`sending`** parameter, and every
argument passed to it gets the same treatment (Sendable captures, owned captures
moved in). `Thread.start` and `Task.start` themselves are just APIs that declare
`sending body` — the compiler has no hardcoded knowledge of them.

```dlang
// a user-defined thread API — 'work' gets the send-check at every call site
runAsync :: (sending work: () -> int) -> Task(int) {
  return spawn work()
}
```

`sending` transfers ownership like `sink` (passed by value, consumed at the call);
it only adds the thread-crossing check.

## Shared mutable state — `Mutex(T)`

MVS makes casual shared mutable state impossible, so `Mutex(T)` is the *one*
sanctioned place it lives. It is an atomically reference-counted owning handle
over a lock-protected `T`. `clone()` makes another handle to the **same** guarded
value; move a clone into each worker; the last handle to drop frees everything.

```dlang
inline import("std/concurrency/task")     // bare Task for `spawn`
val mutex = import("std/concurrency/mutex")

bump :: (sink m: mutex.Mutex(int), n: int) -> int {
  var i: int = 0
  while (i < n) { m.update((x: int) -> int = x + 1)  i = i + 1 }
  return n              // spawn needs a value-producing body
}

shared :: () -> int {
  val counter: mutex.Mutex(int) = mutex.Mutex(int).of(0)
  val c1: mutex.Mutex(int) = counter.clone()      // a second handle
  val t: Task(int) = spawn bump(c1, 1000)         // c1 moved into the worker
  val here: int = bump(counter.clone(), 1000)
  await t
  return counter.get()                            // 2000
}
```

`update(f)` locks, replaces the value with `f(value)`, and unlocks — the lock is
the exclusivity token, so the Law of Exclusivity extends *across* threads through
it. `get()` reads a copy under the lock.

## Lock-free counters — `Atomic`

`Atomic` is an owning handle over a heap 4-byte cell driven by the hardware's
sequentially-consistent atomic instructions. It is the refcount primitive under
`Shared`/`Mutex`/`Channel`, and a standalone counter in its own right.

```dlang
val atom = import("std/concurrency/atomic")

var a: atom.Atomic = atom.Atomic.of(0)
val old: int = a.fetchAdd(1)     // returns the value BEFORE the add
val now: int = a.subFetch(1)     // returns the value AFTER the subtract
println(a.load())
```

The compiler auto-links `libatomic` whenever a program uses these operations — no
flag required.

## Reference-counted sharing — `Shared(T)`

`Shared(T)` is an **Arc**: an atomically reference-counted handle for sharing an
immutable value across threads. `clone()` is a lock-free refcount bump; the last
drop frees.

```dlang
inline import("std/concurrency/task")     // bare Task for `spawn`
val shared = import("std/concurrency/shared")

val cfg: shared.Shared(int) = shared.Shared(int).of(42)
val c1: shared.Shared(int) = cfg.clone()
val t: Task(int) = spawn readConfig(c1)   // c1 moved into the worker
println(cfg.get())                         // 42
await t
```

Use `Shared` for shared *immutable* state; use `Mutex` when the shared value must
be mutated.

## Importing the concurrency modules

Two rules cover every case:

- **`spawn` needs `task` inline** — `inline import("std/concurrency/task")`. The
  `spawn` keyword expands to `Task(T).start(…)`, which names `Task` bare, so the
  `task` module must be inline-imported (this also gives you `Thread`).
- **Import everything else by binding prefix** —
  `val ch = import("std/concurrency/channel")`, `val mutex = import(…)`, etc.
  Those modules share internal `thread`/`atomic` dependencies that would collide
  in the flat namespace under `inline import`.

```dlang
inline import("std/concurrency/task")        // Task, spawn/await, Thread
val mutex   = import("std/concurrency/mutex")
val channel = import("std/concurrency/channel")
```

## Related

- [Structured Concurrency — Tasks and Futures](42-coroutines-and-promises.md)
- [spawn / await](43-async-await.md)
- [Channels and Message Passing](44-channels.md)
- [Memory Safety](14a-memory-safety.md)

[← Index](README.md)
