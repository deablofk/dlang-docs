# Coroutines and Promises

Coroutines and promises in DLang are **standard-library types, not language syntax**. There is no `async`/`await` keyword and no function coloring. The model is library-first: stackful coroutines, promises, and channels are all ordinary `.dlang`, and the compiler exposes exactly one low-level intrinsic — a context switch — that everything else is built on.

This page builds directly on the threading primitives in [Multithreading and Concurrency](41-concurrency.md).

## The intrinsics, via `@intrinsic`

There is no magic compiler namespace. The concurrency module declares three body-less functions and marks them with `@intrinsic("id")`; the compiler recognizes the id and injects the low-level implementation. This is the same annotation system used by atomics (see [Multithreading and Concurrency](41-concurrency.md)) and by macros and reflection (see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)). An ordinary user never writes these — only the concurrency module does.

```dlang
// 1. Context: an OPAQUE struct whose layout (registers + stack pointer +
//    instruction pointer) is filled in by the compiler per platform.
@intrinsic("contexto.tipo")
Contexto :: struct {}

// 2. Initialize 'ctx' so that, when resumed, it runs 'entrada' on 'pilha'.
//    THE STACK IS MEMORY YOU ALLOCATE -> explicit cost.
@intrinsic("contexto.criar")
criarContexto :: (ctx: Ptr(Contexto), pilha: []byte, entrada: () -> ())

// 3. Save the current context into 'de' and resume 'para'. The caller "freezes
//    here" and only returns when someone switches back to 'de'. A fiber switch.
@intrinsic("contexto.trocar")
trocarContexto :: (de: Ptr(Contexto), para: Ptr(Contexto))
```

Crucially, the **call site stays a normal call**: you write `trocarContexto(...)` like any function. Only the *declaration* carries the annotation — moving from a namespace to an annotation never touched user code.

## Coroutines are stackful

Each coroutine has its own stack, and that stack is memory you allocate with an **explicit allocator**. A 64 KB stack is a visible line of code, not a hidden cost. Because the stack is real, a coroutine can yield from anywhere — there is no need to "color" functions as async.

```dlang
Corrotina :: struct {
  ctx: Contexto             // the coroutine's own state
  retorno: Ptr(Contexto)    // where to return on yield
  pilha: []byte             // its stack, allocated explicitly
  terminada: boolean
}

// criar: the stack is allocated WITH AN EXPLICIT ALLOCATOR (visible cost)
Corrotina.criar :: (alloc: Allocator, corpo: () -> ()) -> Ptr(Corrotina) {
  val c: Ptr(Corrotina) = alloc.alloc(Corrotina)
  c.value.pilha = alloc.allocBytes(64 * 1024)   // 64KB stack — you SEE the cost
  c.value.terminada = false
  criarContexto(ref c.value.ctx, c.value.pilha, corpo)
  return c
}
```

Resuming and yielding are just two directions of the same context switch. `retomar` freezes the caller and jumps into the coroutine; `ceder` (yield) freezes the coroutine and returns to whoever resumed it.

```dlang
// retomar: save where I am and jump into the coroutine
Corrotina.retomar :: (de_onde: Ptr(Contexto)) {
  _.retorno = de_onde
  trocarContexto(de_onde, ref _.ctx)   // freeze caller, thaw coroutine
}

// ceder (yield, from inside the coroutine): return to whoever resumed me
Corrotina.ceder :: () {
  trocarContexto(ref _.ctx, _.retorno)  // freeze coroutine, thaw caller
}
```

## Promises are 100% library

A `Promise(T)` adds zero compiler surface. It is just a struct holding a state and a value, resolved by one coroutine or thread and read by another. No syntactic `async`/`await` is involved anywhere.

```dlang
EstadoPromise :: enum { Pendente, Resolvida, Rejeitada }

Promise(T) :: struct {
  estado: EstadoPromise
  valor: T
  erro: any
}

Promise(T).criar :: (alloc: Allocator) -> Ptr(Promise(T)) {
  val p: Ptr(Promise(T)) = alloc.alloc(Promise(T))
  p.value.estado = EstadoPromise.Pendente
  return p
}

// the producer resolves the promise
Promise(T).resolver :: (v: T) {
  _.valor = v
  _.estado = EstadoPromise.Resolvida
}
```

The consumer waits by **cooperatively yielding** until the promise is resolved. This does not block the OS thread: `aguardar` hands control back to the scheduler and resumes later, when the value is ready.

```dlang
// the consumer waits by YIELDING the coroutine until resolved (cooperative,
// does not block the OS thread — it returns control to the scheduler)
Promise(T).aguardar :: (eu: Ptr(Corrotina)) -> T {
  while (_.estado == EstadoPromise.Pendente) {
    eu.value.ceder()
  }
  return _.valor
}
```

## Design rationale

Stackful coroutines plus a single context-switch intrinsic give you everything `async`/`await` gives — suspension, resumption, waiting on a result — without splitting the world into colored and uncolored functions and without growing the compiler. The cost stays explicit: you see the allocator, you see the 64 KB stack, you see the executor (see [Multithreading and Concurrency](41-concurrency.md)) that schedules the work. Promises being plain structs means concurrency composes from data, exactly like the rest of the language.

## Related

- [Multithreading and Concurrency](41-concurrency.md)
- [Async/Await Programming](43-async-await.md)
- [Channels and Message Passing](44-channels.md)
- [Manual Memory Management](13-manual-memory.md)

[← Index](README.md)
