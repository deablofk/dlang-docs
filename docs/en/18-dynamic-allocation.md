# Dynamic Allocation

Dynamic allocation reserves heap memory at runtime, for data whose size is not known at compile time. In DLang you never call an allocator for this — **you create an owning value**, and the value's type does the allocating, growing, and freeing. `List(T)`, `Map(K, V)`, `string`, `ByteBuf`, and `Pool(T)` are the standard owners; your own `nocopy` + `deinit` types join them. The compiler destroys every owner at its last use, so dynamic memory has the same lifecycle discipline as everything else — no `new`, no `free`, no leak.

## Growable containers

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).empty()
  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
  println("${itens.size()} itens")    // last use — the list's buffer is freed here
}
```

`List(string).empty()` starts empty and grows by doubling as you `add`; `Map(K, V).empty()` behaves the same way. Both are ordinary generic structs in the standard library — not compiler magic — implemented on the Builtin floor ([Manual Memory](13-manual-memory.md)) and exposed to you as safe owning values.

Because containers are **`nocopy` owners**, handing one around follows move semantics:

```dlang
var xs: List(int) = List(int).empty()
xs.add(1)
val ys: List(int) = xs        // MOVE — xs is consumed (using it again is E_USE_AFTER_MOVE)
val zs: List(int) = ys.copy() // explicit deep copy when you really want two
```

## Strings

`string` is a dynamically allocated, immutable value with compiler-managed ownership. Build strings the obvious way — concatenation, interpolation, accumulation in a loop — and the compiler frees every dead intermediate on the spot:

```dlang
var relatorio: string = ""
for (item : itens) {
  relatorio = relatorio + "- ${item}\n"   // each dead intermediate is freed immediately
}
```

## Byte buffers

Binary data lives in a `ByteBuf` — the owning, growable byte buffer: `ByteBuf.new(cap)` (then `.zeros(n)` for an initialized scratch area), big-endian writers (`.u8` … `.u64`), `.appendStr(s)`, readers (`.byteAt`, `.i32at`, `.i64at`), and `.addr(i)` when a raw address must cross into C as an opaque `long`. It is the standard scratch for FFI out-structs — and like every owner, it dies at last use.

## Entity stores

When many dynamically allocated things reference each other and die independently — game entities, graph nodes — allocate them in a **`Pool(T)`** and link them with copyable `Handle` values ([Memory Safety](14a-memory-safety.md#graphs-and-shared-identity--poolt--handle-or-indices)). The pool is the single owner of all its slots; a killed slot's handle goes detectably stale instead of dangling.

## Constructing into place — `set`

Where C would pass a pointer for the callee to fill, DLang passes a **`set`** parameter: the callee must initialize the caller's slot on every path, checked by definite assignment. This is how "allocate the result where it must live" works without a pointer:

```dlang
Vector :: struct { x: int  y: int }

makeUniform :: (set out: Vector, scale: int) {
  out = Vector { x: scale, y: scale }   // every path must assign `out`
}

var v: Vector          // deliberately uninitialized — the callee constructs it
makeUniform(v, 3)      // v is fully initialized here
```

## Writing your own owner

A type that owns a dynamic allocation is a `nocopy` struct with a `deinit`; its methods (and only they) may use the raw floor vocabulary to allocate and grow. See [Manual Memory](13-manual-memory.md) for a complete worked example — a growable `IntStack` implemented exactly the way `List` is.

## Where the memory comes from

Underneath the owners sits the runtime allocator (`std/mem/allocator.dlang`) — an implementation detail of the Builtin floor. Ordinary code cannot (and need not) swap it: memory *strategy* in DLang is expressed by choosing owners — a `Pool` for slot reuse, a `ByteBuf` for contiguous bytes, `withCapacity(n)` to pre-size a list — not by installing a different allocator behind the program's back.

## Design rationale

Classic manual allocation scatters `malloc`/`free` pairs across a codebase and makes every call site a potential leak. Classic GC hides allocation entirely. DLang's owners are the middle path with neither cost: allocation is visible (`List(T).empty()`, `ByteBuf.new(n)` — you can read where the heap is used), release is automatic and deterministic (the owner's last use), and the unsafe machinery that implements growth lives behind the boundary law in a handful of audited types. Dynamic memory becomes a *typing* concern — pick the right owner — instead of a bookkeeping concern.

## Related

- [Memory Safety](14a-memory-safety.md)
- [Manual Memory — the Builtin floor](13-manual-memory.md)
- [Garbage Collection](14-garbage-collection.md)
- [Arrays and Lists](07-arrays-and-lists.md)
- [Maps and Dictionaries](08-maps-and-dictionaries.md)

[← Index](README.md)
