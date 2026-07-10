# Garbage Collection

DLang has **no garbage collector**, and that is a deliberate design decision, not a missing feature. A systems language should make the cost of memory visible and predictable; a background collector that can pause your program at an unpredictable moment is the opposite of that. Memory in DLang is explicit: you allocate with `New(T)` and free with `_alloc.free(...)` (see [Manual Memory Management](13-manual-memory.md)).

What DLang offers *instead* of automatic collection is a way to make manual memory both convenient and checkable: the **context allocator**.

## The swappable context allocator

Every allocation — `New(T)`, and every implicit allocation inside `string`, `List`, and `Map` — draws from the *current allocator*, a value held in a per-program context. The default is a plain libc-`malloc` allocator, but you can install a different one for a region of code with `pushAllocator` / `popAllocator`. This is what replaces "which GC manages this object": you decide *how* memory is managed by choosing the allocator, not by hoping a collector cleans up later.

```dlang
val prev: Allocator = pushAllocator(myAllocator)
// ... every allocation in here uses myAllocator ...
popAllocator(prev)
```

Because the choice lives at the allocator level, a whole subsystem's memory strategy can be changed without touching a single allocation site.

## Catching leaks and double-frees

The convenience a GC usually sells — "you won't leak" — DLang provides as an opt-in *checking* tool rather than a runtime tax. `debugAllocator` wraps any backing allocator, records every live block, and reports double or invalid frees as they happen; `debugReport` lists what is still live (leaked) at the end.

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))

val a: Ptr(int) = New(int)
_alloc.free(cast(Ptr(byte), a))
_alloc.free(cast(Ptr(byte), a))   // -> reported: invalid or double free

debugReport(context().value)      // -> allocs / frees / leaked / errors
popAllocator(prev)
```

You push the debug allocator while developing to catch mistakes, and simply do not push it in a release build — so the checks cost exactly nothing when you ship. This is the "copilot, not a tax" approach: the tool helps you find bugs without imposing a permanent runtime cost.

## Why no collector

Most garbage-collected languages make the GC the air you breathe: every allocation is hidden and managed, and you cannot opt out. DLang inverts that. Allocation is always explicit, and the allocator you install decides the strategy. That keeps the common path free of collector overhead and pauses, while the swappable context and the debug allocator recover most of the ergonomics a GC is prized for — redirecting a subsystem's memory, and finding leaks — without giving up predictability.

## Related

- [Manual Memory Management](13-manual-memory.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Pointers and References](12-pointers-and-references.md)

[← Index](README.md)
