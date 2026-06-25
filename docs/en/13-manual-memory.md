# Manual Memory Management

DLang never allocates heap memory behind your back. When you want memory that outlives the current stack frame, you ask an *allocator* for it explicitly. The manual allocator is named `_alloc`: you call `_alloc.alloc(T)` to reserve space and `_alloc.free(...)` to return it. The allocator is part of the code you can see, so the cost of every allocation is visible at the call site.

This page covers the manual model, where *you* own the lifetime of the memory. For the hands-off alternative, see [Garbage Collection](14-garbage-collection.md).

## Allocating a typed value

`_alloc.alloc(T)` reserves exactly enough memory to hold a `T` and returns a `Ptr(T)` to it. Because it is a pointer to data, you reach the contents through `.value` (see [Pointers and References](12-pointers-and-references.md)).

```dlang
// for specific struct types
val pessoaPtr: Ptr(Pessoa) = _alloc.alloc(Pessoa)
pessoaPtr.value.nome = "Gabriel" // change a field inside the struct
```

The compiler knows the exact size of `Pessoa`, so it reserves precisely that many bytes on the heap — no more.

## Why `.value` matters for safety

Routing every dereference through `.value` is not just ergonomic, it is a safety strategy. The allocator's `.value` access is a single, centralised point where the compiler can validate the pointer.

```dlang
// By centralising memory access on the .value property, the compiler gains
// a perfect single point for code-safety validation.
// If the pointer is null, the compiler can emit a safe error when .value is
// accessed, preventing the sudden segmentation faults common in C/C++.
```

Instead of a wild dereference crashing the process, a null pointer surfaces as a well-defined error exactly where it is touched.

## Freeing with `defer`

Memory you allocate manually must be returned manually. The idiomatic pattern is to pair every `alloc` with a `defer free`, placed immediately after the allocation. `defer` schedules the free to run when the enclosing function exits, no matter which path it takes.

```dlang
criarInimigo :: () {
  // the compiler reserves the exact size of Pessoa on the heap
  val inimigo: Ptr(Pessoa) = _alloc.alloc(Pessoa)

  // guarantees the dynamic memory is returned to the system at function end
  defer _alloc.free(inimigo)

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

Putting the `defer` right under the `alloc` makes leaks easy to audit: every allocation has its matching free visible one line below it, and `defer` guarantees it runs even on early returns or errors.

## Allocating dynamic containers

Standard-library containers like `List(T)` are not compiler magic — they are ordinary generic structs that take an allocator at construction. They follow the same discipline: `init(_alloc)` to acquire, `deinit()` (run via `defer`) to release.

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).init(_alloc)
  defer itens.deinit()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

The `List` holds onto the allocator you gave it and uses it for any internal growth, so all of its heap traffic flows through the same visible `_alloc`. See [Dynamic Allocation](18-dynamic-allocation.md) for more on growing containers.

## Design rationale

Manual memory is the default because a systems language must offer predictable, zero-overhead control over the heap. Making the allocator an explicit value (`_alloc`) means there is no hidden global allocator and no surprise allocation: you can read a function and know exactly what it touches. Pairing `alloc` with `defer free` turns lifetime management into a local, visible, mechanically-checkable pattern, while `.value` gives the compiler the one checkpoint it needs to keep manual memory safe.

## Related

- [Pointers and References](12-pointers-and-references.md)
- [Garbage Collection](14-garbage-collection.md)
- [Dynamic Allocation](18-dynamic-allocation.md)

[← Index](README.md)
