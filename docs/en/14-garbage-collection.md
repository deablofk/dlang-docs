# Garbage Collection

DLang gives you a second allocator for when you would rather not track lifetimes by hand: `_gcAlloc`. It has the same shape as the manual allocator — `_gcAlloc.alloc(T)` returns a `Ptr(T)` — but the memory it hands out is managed for you. There is no matching `free`, and no `defer` is required. The garbage collector watches the pointer and reclaims the object when nothing references it any more.

Crucially, garbage collection is *opt-in per allocation*. The language has no hidden global GC: memory becomes garbage-collected only because you asked for it with `_gcAlloc` instead of [`_alloc`](13-manual-memory.md). Both styles coexist in the same program.

## Allocating with the GC

You use `_gcAlloc` exactly like the manual allocator, then access the result through `.value` (see [Pointers and References](12-pointers-and-references.md)).

```dlang
// allocating using the garbage collector's allocator
val p: Ptr(Pessoa) = _gcAlloc.alloc(Pessoa)
p.value.nome = "Bruno"

// no 'defer _gcAlloc.free(p)' needed.
// the GC tracks 'p' and erases it from the heap when the function ends.
```

The only visible difference from manual allocation is the missing `defer free`. The `Ptr(Pessoa)` behaves identically: same `.value` access, same null-checked safety checkpoint.

## How collection works

DLang's collector combines two mechanisms. The primary one is **reference counting** in the style of Swift and Wren: every GC-allocated object carries an internal counter that tracks how many references point at it. When the count reaches zero, the object is freed promptly.

Reference counting alone cannot reclaim *reference cycles* — objects that point at each other but are unreachable from the rest of the program. To handle these, a **background sweep** runs periodically, scanning for orphaned objects and clearing them all at once.

```dlang
// Reference counting in the Swift/Wren style: each object keeps an internal
// counter. In addition, tracking runs in the background from time to time,
// looking for orphaned objects and cleaning them all up in one pass.
```

This hybrid keeps the common case cheap and deterministic (a counter increment/decrement) while still guaranteeing that cyclic garbage eventually goes away.

## Choosing between `_alloc` and `_gcAlloc`

Both allocators produce the same `Ptr(T)` type, so the choice is purely about who owns the lifetime:

- Reach for [`_alloc`](13-manual-memory.md) when you want deterministic, zero-overhead control and are happy to write `defer free`. This is the default for hot paths and tight resource budgets.
- Reach for `_gcAlloc` when the ownership graph is complicated or lifetimes are hard to pin down, and the convenience of automatic reclamation outweighs the counter overhead.

Because the decision lives at the call site, a single program can use manual memory for its performance-critical core and the GC for its messier, less hot data, with both kinds of pointer interoperating freely.

## Design rationale

Most garbage-collected languages make the GC the air you breathe: every allocation is hidden and managed, and you cannot opt out. DLang inverts that. Allocation is always explicit, and *which* allocator you name decides the lifetime model. Keeping `_gcAlloc` symmetric with `_alloc` — same `alloc`, same `Ptr(T)`, same `.value` — means the two strategies are interchangeable at the type level, so you pay for garbage collection only exactly where you write `_gcAlloc`, and nowhere else.

## Related

- [Pointers and References](12-pointers-and-references.md)
- [Manual Memory Management](13-manual-memory.md)
- [Dynamic Allocation](18-dynamic-allocation.md)

[← Index](README.md)
