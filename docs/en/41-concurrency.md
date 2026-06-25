# Multithreading and Concurrency

DLang treats concurrency the same way it treats memory: as something the *library* provides, not something the compiler hides. OS threads, mutexes, and the scheduler are all ordinary `.dlang` code. The only thing the compiler contributes is the handful of operations that cannot be written in the language itself — atomic instructions and memory barriers — because those map directly to hardware.

This page covers the threading and scheduling primitives. The cooperative half of the story — coroutines, promises, channels — builds on top of these and lives in [Coroutines and Promises](42-coroutines-and-promises.md) and [Channels and Message Passing](44-channels.md).

## The only compiler intrinsics: atomics

A `compare-and-swap`, an atomic add, and a memory fence cannot be expressed with normal statements — they correspond to specific CPU instructions. DLang exposes them through the same `@intrinsic` annotation used everywhere else: a body-less declaration carries the annotation, and the compiler injects the implementation. The call site is a perfectly normal function call.

```dlang
@intrinsic("atomic.cas")        // compare-and-swap
atomicoCAS :: (alvo: Ptr(int), esperado: int, novo: int) -> boolean

@intrinsic("atomic.add")
atomicoSomar :: (alvo: Ptr(int), delta: int) -> int

@intrinsic("atomic.fence")
barreiraMemoria :: ()
```

Note that there is no magic `atomic` namespace. These are three ordinary declarations that happen to be marked `@intrinsic` — the same mechanism the concurrency module uses for context switching (see [Coroutines and Promises](42-coroutines-and-promises.md)) and that metaprogramming uses for compiler hooks (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)).

## OS threads are a struct

A `Thread` is a standard-library struct wrapping an opaque OS handle. Its methods are written in DLang; the body reaches the real OS thread through FFI (`@externo`). Creating a thread takes an explicit allocator and the function to run.

```dlang
Thread :: struct {
  handle: Ptr(byte)             // opaque OS handle
}

Thread.criar :: (alloc: Allocator, corpo: () -> ()) -> Ptr(Thread) { ... }
Thread.aguardar :: () { ... }   // join: wait for the thread to finish

trabalho :: () { println("running on another thread") }

usoThread :: () {
  val t = Thread.criar(_alloc, trabalho)
  defer t.value.aguardar()
}
```

`aguardar` is the join: pairing it with `defer` guarantees the spawning function waits for its thread before returning.

## Mutex: pure library on top of an atomic

Because the atomic CAS is available as an ordinary call, a mutex needs no compiler support at all. It is a struct holding a single integer, locked by spinning on `atomicoCAS` and unlocked by clearing the flag.

```dlang
Mutex :: struct { travado: int }

Mutex.travar :: () {
  while (!atomicoCAS(ref _.travado, 0, 1)) {
    // busy: yield (coroutine) or spin (thread)
  }
}
Mutex.destravar :: () { _.travado = 0 }
```

Use it with `defer` so the lock is released on every exit path — including early returns and errors:

```dlang
depositar :: (m: Ptr(Mutex), saldo: Ptr(int)) {
  m.value.travar()
  defer m.value.destravar()
  saldo.value = saldo.value + 100
}
```

## The Executor: the "allocator of concurrency"

Just as nothing allocates heap without a visible `Allocator`, nothing schedules coroutines without a visible `Executor`. The executor owns the work queue and the pool of OS threads; you pass `_exec` around on purpose, exactly as you pass `_alloc`. There is **no hidden global runtime** — unlike Go, DLang never starts a scheduler behind your back.

```dlang
Executor :: struct {
  fila: List(Ptr(Corrotina))
  threads: List(Ptr(Thread))
}

Executor.criar :: (alloc: Allocator, numThreads: int) -> Ptr(Executor) { ... }
Executor.agendar :: (c: Ptr(Corrotina)) { _.fila.add(c) }   // enqueue work
Executor.rodar :: () { ... }   // distribute coroutines across the threads

usoExecutor :: () {
  val exec = Executor.criar(_alloc, 4)        // 4 OS threads
  defer exec.value.rodar()

  exec.value.agendar(Corrotina.criar(_alloc, { println("task 1") }))
  exec.value.agendar(Corrotina.criar(_alloc, { println("task 2") }))
}
```

The executor multiplexes many cheap cooperative coroutines onto a small number of OS threads. The coroutines themselves are explained in [Coroutines and Promises](42-coroutines-and-promises.md).

## Design rationale

A systems language must not bury concurrency under an invisible runtime. By keeping `Thread`, `Mutex`, and `Executor` as ordinary library code and reducing the compiler's role to three atomic intrinsics, DLang keeps the implementation auditable and the cost visible. The executor mirrors the allocator: making the scheduler an explicit value means you always know what is scheduling your work and on how many threads, with no global magic to reason around.

## Related

- [Coroutines and Promises](42-coroutines-and-promises.md)
- [Async/Await Programming](43-async-await.md)
- [Channels and Message Passing](44-channels.md)
- [Manual Memory Management](13-manual-memory.md)

[← Index](README.md)
