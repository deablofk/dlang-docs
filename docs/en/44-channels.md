# Channels and Message Passing

A channel in DLang is a generic standard-library struct — **zero compiler involvement**. It gives you CSP-style (Go-style) communication: coroutines and threads coordinate by passing *messages* instead of sharing memory. A channel is built entirely from pieces you have already seen: a `Mutex`, a buffer list, and cooperation with the `Executor` (see [Multithreading and Concurrency](41-concurrency.md)).

## The channel struct

`Canal(T)` is a generic struct over a buffer, a capacity, a lock, and a closed flag. A capacity of `0` means an unbuffered rendezvous channel; a positive capacity means a buffered channel.

```dlang
Canal(T) :: struct {
  buffer: List(T)
  capacidade: int     // 0 = unbuffered (rendezvous); >0 = buffered
  trava: Mutex
  fechado: boolean
}

Canal(T).criar :: (alloc: Allocator, capacidade: int) -> Ptr(Canal(T)) { ... }
```

## Sending and receiving

Both ends coordinate through the same cooperative mechanism: when an operation cannot proceed, it **yields the coroutine** instead of blocking the OS thread, handing control back to the scheduler. `enviar` yields while the buffer is full; `receber` yields while it is empty (and the channel is still open).

```dlang
// enviar: blocks by YIELDING the coroutine if the buffer is full
Canal(T).enviar :: (eu: Ptr(Corrotina), valor: T) {
  _.trava.travar()
  defer _.trava.destravar()
  while (_.buffer.tamanho >= _.capacidade) eu.value.ceder()
  _.buffer.add(valor)
}

// receber: returns (value, ok). ok=false once the channel is closed and drained.
Canal(T).receber :: (eu: Ptr(Corrotina)) -> (T, boolean) {
  _.trava.travar()
  defer _.trava.destravar()
  while (_.buffer.tamanho == 0 && !_.fechado) eu.value.ceder()
  if (_.buffer.tamanho == 0) return (zero(T), false)   // closed and empty
  return (_.buffer.removerPrimeiro(), true)
}

Canal(T).fechar :: () { _.fechado = true }
```

The `(value, ok)` return is an ordinary tuple (see [Tuples and Destructuring](38-tuples-and-destructuring.md)): `ok` is `false` exactly when the channel is both closed and empty, which is the signal for a consumer to stop.

## Producer / consumer

A producer schedules a coroutine that sends a few values and then closes the channel; a consumer schedules another that reads until the channel closes, destructuring the `(v, ok)` tuple each time. `euMesmo()` is a std-lib helper returning the current coroutine.

```dlang
exemploCanal :: (exec: Ptr(Executor)) {
  val canal = Canal(int).criar(_alloc, 8)

  // producer
  exec.value.agendar(Corrotina.criar(_alloc, {
    var i = 0
    while (i < 5) { canal.value.enviar(euMesmo(), i); i++ }
    canal.value.fechar()
  }))

  // consumer: reads until the channel closes, destructuring the (v, ok) tuple
  exec.value.agendar(Corrotina.criar(_alloc, {
    while (true) {
      val (v, ok) = canal.value.receber(euMesmo())
      if (!ok) break
      println("received: ${v}")
    }
  }))
}
```

## `select` is a library function, not syntax

Waiting on several channels at once — Go's `select` — is **not** a compiler construct in DLang. It is a standard-library function (or macro; see [Macros and Code Expansion](46-macros.md)). This is consistent with the language's rule that *behavior is sugar over data*: control over multiple channels is expressed by ordinary library code, not by a new keyword.

## Design rationale

Channels give you safe coordination without manual lock juggling, yet they require nothing from the compiler: `Canal(T)` is a generic struct layered over a `Mutex` and the executor's cooperative scheduling. Keeping even `select` in the library, rather than the grammar, holds the line that DLang's surface stays small and its concurrency stays auditable — every send, receive, and wait is plain code you can read.

## Related

- [Coroutines and Promises](42-coroutines-and-promises.md)
- [Multithreading and Concurrency](41-concurrency.md)
- [Async/Await Programming](43-async-await.md)
- [Tuples and Destructuring](38-tuples-and-destructuring.md)

[← Index](README.md)
