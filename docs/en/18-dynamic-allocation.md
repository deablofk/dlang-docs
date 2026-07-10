# Dynamic Allocation

Dynamic allocation reserves memory on the heap at runtime, for data whose size or lifetime is not known at compile time. In DLang there is no hidden `new` and no implicit boxing — but you also do not thread an allocator through every call. Instead, allocation is **ambient**: every heap allocation draws from the *current allocator*, a swappable value held in a per-program context. This is the model popularized by Jai.

## Allocating a single value

To place one value on the heap, call `New(T)`. It returns a `Ptr(T)` — a pointer whose contents you reach through `.value`:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
}

criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = New(Pessoa)
  defer _alloc.free(cast(Ptr(byte), inimigo))

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

`New(T, n)` allocates `n` contiguous values instead of one. `defer _alloc.free(...)` schedules the matching free when the function exits, keeping allocation and release visibly paired. (`New(T)` is the readable spelling of the low-level `_alloc.alloc(T)`; both route through the current allocator.)

## Growable containers

Container types such as `List(T)` and `Map(K, V)` allocate their backing storage dynamically, but they wrap the bookkeeping for you. You do **not** hand them an allocator — they pull from the same ambient context every other allocation uses:

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).empty()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

`List(string).empty()` creates an empty list that grows on the heap as you `add` elements; `Map(K, V).empty()` behaves the same way. Their internal growth flows through whatever allocator is current, so redirecting them is a matter of installing a different allocator — not editing their call sites.

## The current allocator

An `Allocator` is a single procedure plus its private data:

```dlang
Allocator :: struct {
  proc: (Ptr(byte), AllocationType, long, Ptr(byte)) -> Ptr(byte)
  data: Ptr(byte)
}
```

`context()` returns the active allocator. `mallocAllocator()` is the default (libc-backed). You install another for a region of code and restore it afterward:

```dlang
val prev: Allocator = pushAllocator(myAllocator)
// ... every New / string / List / Map allocation here uses myAllocator ...
popAllocator(prev)
```

Because the allocator is ambient, a helper function you call allocates into whatever allocator is active at the call — with no allocator parameter to pass down. That is the key difference from the "pass the allocator explicitly" style: the strategy lives in one place, not scattered through every signature.

## The debug allocator

`debugAllocator` wraps any backing allocator, tracks every live block, reports double / invalid frees as they happen, and lets `debugReport` list leaks. Push it while developing; omit it in release for zero overhead:

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))

val a: Ptr(int) = New(int)
_alloc.free(cast(Ptr(byte), a))
_alloc.free(cast(Ptr(byte), a))   // reported as a double free

debugReport(context().value)      // allocs / frees / leaked / liveBytes / errors
popAllocator(prev)
```

## Writing your own allocator

Any value of type `Allocator` works — a `proc` that handles `AllocationType.ALLOCATE` (return `size` bytes) and `AllocationType.FREE` (release `oldPtr`), plus whatever `data` your allocator needs. That lets you drop in an arena, a pool, or a counting allocator and have the entire program — standard library included — use it, just by pushing it onto the context.

## Design rationale

Ambient allocation keeps the two things a systems programmer wants in tension — control and convenience — both satisfied. Control: every allocation is still explicit (`New`, or a container method that clearly allocates), and you can always see and replace the allocator. Convenience: you do not pollute every function signature with an allocator parameter, and you can change a whole subsystem's memory strategy from one place. Containers like `List` and `Map` need no special compiler support — they are ordinary generic structs that allocate through the same context as everything else.

## Related

- [Manual memory](13-manual-memory.md)
- [Garbage collection](14-garbage-collection.md)
- [Pointers and references](12-pointers-and-references.md)
- [Structs](17-structs.md)
- [Arrays and lists](07-arrays-and-lists.md)

[← Index](README.md)
