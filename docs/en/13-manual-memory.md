# Manual Memory Management

DLang never allocates heap memory behind your back. When you want memory that outlives the current stack frame, you ask for it explicitly with `New(T)`, and you return it explicitly with `_alloc.free(...)`. There is no garbage collector: lifetimes are yours to manage.

What makes this ergonomic rather than tedious is that allocation is **ambient** — every allocation draws from the *current allocator*, a swappable value held in a per-program context. You don't thread an allocator through every function; you set it once (or accept the default) and everything downstream uses it. This is the model popularized by Jai, and it is covered in full in [Dynamic Allocation](18-dynamic-allocation.md).

## Allocating a typed value

`New(T)` reserves exactly enough memory to hold a `T` and returns a `Ptr(T)` to it. Because it is a pointer to data, you reach the contents through `.value` (see [Pointers and References](12-pointers-and-references.md)).

```dlang
val pessoaPtr: Ptr(Pessoa) = New(Pessoa)
pessoaPtr.value.nome = "Gabriel"   // change a field inside the struct
```

The compiler knows the exact size of `Pessoa`, so it reserves precisely that many bytes — no more. For a block of `n` values, use `New(T, n)`, which returns a `Ptr(T)` to `n` contiguous slots you index with `p[i]`.

Under the hood `New(T)` is the high-level spelling of the low-level primitive `_alloc.alloc(T)`; both allocate through the current allocator, so they are interchangeable. `New` reads better in ordinary code.

## Freeing with `defer`

Memory you allocate must be returned. The idiomatic pattern is to pair every allocation with a `defer _alloc.free(...)`, placed immediately after it. `defer` schedules the free to run when the enclosing function exits, no matter which path it takes.

```dlang
criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = New(Pessoa)
  defer _alloc.free(cast(Ptr(byte), inimigo))   // returned at function end

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

Putting the `defer` right under the allocation makes leaks easy to audit: every allocation has its matching free visible one line below it, and `defer` guarantees it runs even on early returns or errors. Freeing is *explicit* — the language never frees for you, but it also never stops you from choosing exactly when a lifetime ends.

## Where the memory comes from

`New` does not hard-wire libc `malloc`. It calls whatever allocator is currently installed in the context. By default that is the malloc-backed allocator, so the example above behaves like a classic `malloc`/`free`. But you can swap the allocator for a region of code — for example to a **debug allocator** that tracks every live block and reports double-frees and leaks while you develop:

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))
// ... allocations here are tracked ...
debugReport(context().value)   // allocs / frees / leaked / errors
popAllocator(prev)
```

Every allocation between the push and pop — including implicit ones inside `string`, `List`, and `Map` — flows through the installed allocator. See [Dynamic Allocation](18-dynamic-allocation.md) for the full allocator API.

## Design rationale

Manual memory is the default because a systems language must offer predictable, zero-overhead control over the heap. Routing allocation through a visible, swappable allocator means there is no surprise allocation *and* no ceremony: you read `New(T)` and know a heap allocation happens, and you can redirect all of it — yours and the standard library's — by installing a different allocator, without rewriting a single call. Pairing allocation with `defer free` turns lifetime management into a local, visible pattern; and routing dereferences through `.value` keeps every memory access explicit.

## Related

- [Pointers and References](12-pointers-and-references.md)
- [Garbage Collection](14-garbage-collection.md)
- [Dynamic Allocation](18-dynamic-allocation.md)

[← Index](README.md)
