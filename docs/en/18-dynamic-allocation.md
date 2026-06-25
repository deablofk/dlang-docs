# Dynamic Allocation

Dynamic allocation reserves memory on the heap at runtime, for data whose size or lifetime is not known at compile time. In DLang every heap allocation goes through an **explicit allocator** — there is no hidden `new`, no implicit boxing. You can always point to the allocator that produced a piece of memory, and you are responsible for giving it back. The `defer` statement makes that cleanup reliable.

## Allocating a single struct

To place one struct on the heap, call `alloc(Tipo)` on an allocator. The default manual allocator is `_alloc`. It returns a `Ptr(Tipo)` — a pointer whose value you reach through `.value`:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
}

criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = _alloc.alloc(Pessoa)
  defer _alloc.free(inimigo)

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

The compiler reserves exactly `Pessoa`'s size on the heap. The `defer _alloc.free(inimigo)` schedules the matching free to run when the function exits, no matter how it exits — this is the idiom that keeps allocation and deallocation visibly paired at the same place in the code. Field access goes through `.value` (for example `inimigo.value.nome`), which is the single, centralized point where the compiler can insert a null-pointer safety check before you touch the data. See [Manual memory](13-manual-memory.md) for the full pointer and allocator model.

## Allocating a growable container

Container types such as `List(T)` allocate their backing storage dynamically too, but they wrap the bookkeeping for you. You initialize one by handing it an allocator with `.init(_alloc)`, and release it with `.deinit()`:

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).init(_alloc)
  defer itens.deinit()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

`List(string).init(_alloc)` creates an empty list that will grow on the heap as you `add` elements, drawing all of its memory from `_alloc`. The paired `defer itens.deinit()` returns that memory when the function ends. The same `init(allocator)` / `defer deinit()` rhythm applies to other library containers like `Map(K, V)`.

## Choosing an allocator

The allocator is a parameter, not a global default baked into the language. Passing `_alloc` means you manage the lifetime yourself with `free`/`deinit`. If you would rather let the garbage collector track the object, allocate with `_gcAlloc` instead and omit the `defer free` — the GC reclaims it when it becomes unreachable. That choice is covered in [Garbage collection](14-garbage-collection.md). Either way the decision is explicit at the allocation site.

## Design rationale

Routing every heap allocation through a visible allocator is the core of DLang's memory philosophy: the language never allocates behind your back, so the cost of any piece of data is always traceable to an `_alloc` or `_gcAlloc` you can see. Pairing each allocation with a `defer free` (or `defer deinit`) keeps acquisition and release next to each other, which is far harder to get wrong than tracking them across distant `return` paths. Centralizing pointer access on `.value` gives the compiler one well-defined place to enforce null safety, heading off the segmentation faults that plague C and C++. And because containers like `List` and `Map` are ordinary library structs that take an allocator, they need no special compiler support — they follow the exact same explicit-allocator discipline as a hand-rolled `alloc`.

## Related

- [Manual memory](13-manual-memory.md)
- [Garbage collection](14-garbage-collection.md)
- [Pointers and references](12-pointers-and-references.md)
- [Structs](17-structs.md)
- [Arrays and lists](07-arrays-and-lists.md)
- [Constructors and destructors](21-constructors-and-destructors.md)

[← Index](README.md)
