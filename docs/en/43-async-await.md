# Async/Await Programming

> Status: Absent as syntax.

DLang has no `async` keyword and no `await` keyword. Asynchronous programming is fully supported, but it is achieved entirely through the library-first concurrency model — stackful coroutines, promises, channels, and an explicit executor — rather than through dedicated syntax.

## There is no `async`/`await`

In many languages, `async` marks a function as suspendable and `await` suspends it until a result is ready. DLang deliberately omits both. The same outcomes are expressed with ordinary library calls already described elsewhere:

- **Suspension and resumption** come from stackful coroutines: `Corrotina.retomar` and `Corrotina.ceder` (yield). See [Coroutines and Promises](42-coroutines-and-promises.md).
- **Waiting for a result** is `Promise(T).aguardar`, which cooperatively yields until the promise resolves — the exact behavior an `await` expression provides, but as a plain method call.
- **Scheduling** is an explicit `Executor`, the "allocator of concurrency." See [Multithreading and Concurrency](41-concurrency.md).
- **Communication** between concurrent tasks is done with `Canal(T)`. See [Channels and Message Passing](44-channels.md).

A "task that awaits a value" is simply a coroutine that calls `aguardar` on a promise:

```dlang
// no 'async' on the function, no 'await' expression — just library calls
buscarUsuario :: (eu: Ptr(Corrotina), p: Ptr(Promise(string))) {
  val nome = p.value.aguardar(eu)   // cooperatively yields until resolved
  println("got: ${nome}")
}
```

## Why it is absent

The async/await keyword pair is left out for three reinforcing reasons:

1. **It avoids function coloring.** With `async`/`await`, a function's color (sync vs. async) leaks into every caller and forces a parallel "colored" copy of much of the ecosystem. Because DLang coroutines are stackful, any function can yield from anywhere; there is no color to propagate.
2. **It keeps the compiler tiny.** The entire concurrency story rests on one context-switch intrinsic plus a few atomics (see [Coroutines and Promises](42-coroutines-and-promises.md)). Adding `async`/`await` would mean a state-machine transform and new type rules baked into the compiler, for behavior the library already delivers.
3. **It keeps cost explicit.** With the library model you can see the allocator, the coroutine's 64 KB stack, and the executor that schedules it. A keyword that conjures hidden state machines and an implicit runtime would hide exactly the costs a systems language must keep visible.

## Design rationale

Async/await is convenient syntax for an idea — cooperative suspension waiting on a result — that DLang already expresses with values: coroutines, promises, channels, and an explicit executor. Choosing the library form keeps functions uncolored, the compiler small, and every cost on the page. The feature is "absent as syntax" precisely *because* the capability is fully present as a library.

## Related

- [Coroutines and Promises](42-coroutines-and-promises.md)
- [Multithreading and Concurrency](41-concurrency.md)
- [Channels and Message Passing](44-channels.md)

[← Index](README.md)
