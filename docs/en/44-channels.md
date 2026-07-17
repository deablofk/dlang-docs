# Channels and Message Passing

A `Channel(T)` gives CSP-style (Go-style) communication: threads coordinate by
**moving values** across the channel instead of sharing memory. `send` moves a
`T` out of the producer; `recv` moves it into the consumer — no shared mutable
state, just ownership handed across the thread boundary (SPEC §23.5). Affine
element types (e.g. `Channel(List(int))`) move cleanly, since nothing is ever
aliased.

A channel is an atomically reference-counted owning handle: `make()` creates it,
`clone()` makes another handle to the same channel, and the last handle to drop
frees it.

## Send and receive

```dlang
val channel = import("std/concurrency/channel")
inline import("std/concurrency/task")

produce :: (sink tx: channel.Channel(int), n: int) -> int {
  var i: int = 1
  while (i <= n) { tx.send(i)  i = i + 1 }
  return n
}

main :: () -> int {
  val ch: channel.Channel(int) = channel.Channel(int).make()
  val tx: channel.Channel(int) = ch.clone()
  val t: Task(int) = spawn produce(tx, 100)    // tx moved into the worker
  var sum: int = 0
  var i: int = 0
  while (i < 100) { sum = sum + ch.recv()  i = i + 1 }   // recv MOVES each value out
  await t
  println(sum)                                  // 5050
  return 0
}
```

`recv()` blocks on a condition variable until an item is available, then moves it
out. Plain `recv()` assumes the consumer knows how many items to expect — it would
block forever on a closed, empty channel. For channels that get closed, use the
close-aware forms below.

## Closing a channel

`close()` signals end-of-stream and wakes every blocked receiver. A `send` on a
closed channel drops its value and enqueues nothing.

Because an affine `T` has no "zero" to return for the empty case, the close-aware
receives return a **`ChanItem(T)`** — a move-safe owning-optional that either
holds the dequeued item or is empty because the channel is closed:

```dlang
consume :: (sink rx: channel.Channel(int)) -> int {
  var total: int = 0
  var live: boolean = true
  while (live) {
    var it: channel.ChanItem(int) = rx.recvOrClosed()   // blocks until item or closed
    if (it.present()) {
      total = total + it.take()      // MOVE the item out
    } else {
      live = false                   // channel closed and drained
    }
  }
  return total
}
```

- `recvOrClosed()` blocks until an item is available **or** the channel is closed
  and drained.
- `tryRecv()` is the non-blocking form (returns immediately; `isClosed()`
  distinguishes "closed" from "empty right now").
- `it.present()` → `it.take()` moves the item out; otherwise the channel is
  finished.

The producer closes when done:

```dlang
producer :: (sink tx: channel.Channel(int), n: int) -> int {
  var i: int = 1
  while (i <= n) { tx.send(i)  i = i + 1 }
  tx.close()
  return n
}
```

## Selecting across channels

`selectRecv2(a, b)` blocks until either of two channels has an item (or both are
closed and drained). It is a true blocking select — the selector registers one
shared waiter with both channels and sleeps on it, rather than spinning. It takes
its handles by `sink`, so pass clones to keep selecting:

```dlang
var sel: channel.Selected(int) = channel.Channel(int).selectRecv2(ca.clone(), cb.clone())
if (sel.which == -1) {
  // both channels closed and drained
} else {
  use(sel.which, sel.item.take())   // which = 0 (a) or 1 (b)
}
```

For a **dynamic** number of channels, `SelectSet(T)` is the N-way generalization:
build it once, then `recv()` in a loop.

```dlang
var set: channel.SelectSet(int) = channel.SelectSet(int).of()
set.add(a.clone()); set.add(b.clone()); set.add(c.clone())
var live: boolean = true
while (live) {
  var r: channel.Selected(int) = set.recv()
  if (r.which == -1) { live = false }        // all channels closed
  else { use(r.which, r.item.take()) }        // which = 0-based add order
}
```

`SelectSet` owns one shared waiter and subscribes each channel once, so the loop
allocates no per-call condvar; `deinit` unsubscribes and drops the clones.

## Related

- [Multithreading and Concurrency](41-concurrency.md)
- [Structured Concurrency — Tasks and Futures](42-coroutines-and-promises.md)
- [spawn / await](43-async-await.md)

[← Index](README.md)
