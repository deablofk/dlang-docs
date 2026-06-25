# Maps and Dictionaries

A map associates keys with values. DLang offers two complementary tools: a **fixed map literal** baked directly into the language, and a **dynamic `Map(K, V)`** that lives in the standard library. The split mirrors the philosophy used for arrays and lists — the compiler knows about the small, statically-sized form, while growth-over-time is a library type you opt into with an explicit allocator.

## Fixed maps

A fixed map is written `{N}[K: V]`, where `N` is the element count, `K` the key type and `V` the value type. The shape deliberately rhymes with tuples and multi-return functions: braces wrap the contents, and the `[K: V]` part reads as "indexed by `K`, yielding `V`".

```dlang
var keyValueMap: {2}[string: int] = {
  "maça": 50,
  "banana": 30
}
```

Because the size is part of the type, the map is laid out inline with zero heap allocation — it behaves like a small, value-typed table that lives wherever you declare it (stack, struct field, global). This makes it ideal for compile-time-known lookup tables.

### Reading and writing

Access uses square brackets, just like an array, but indexed by the key type instead of an integer:

```dlang
keyValueMap["maça"] = 20
val preco: int = keyValueMap["banana"]
```

Since the capacity is fixed, you cannot add brand-new keys beyond `N` — the bracket form updates existing entries. When you need to grow, reach for the dynamic `Map`.

### Iteration

Iterating a fixed map yields each entry as a `(key, value)` pair. The `for` loop destructures that pair directly into two names:

```dlang
for (chave, valor : keyValueMap) {
  println("Item: ${chave} | valor: ${valor}")
}
```

This is the same destructuring machinery used everywhere else in the language — the loop is simply iterating tuples, where each element is the packed `(chave, valor)` view of an entry. See [Tuples and destructuring](38-tuples-and-destructuring.md).

## Dynamic maps

When the set of keys is not known ahead of time, use `Map(K, V)`. It is a normal generic struct from the standard library — **not** a compiler builtin — and therefore follows the same explicit-allocator discipline as `List`. You construct it by handing it an allocator, and it grows on demand.

```dlang
var mapa: Map(string, int) = Map(string, int).init(_alloc)

mapa.put("banana", 30)
```

`put` inserts a new key or overwrites an existing one, growing the underlying storage when the key is absent. Because all of this is library code, there is no hidden behavior: the allocator you pass is exactly where the memory comes from. Use `_alloc` for the default manual allocator, or `_gcAlloc` if you want the garbage collector to manage its lifetime.

Like any allocator-backed type, a dynamic map should be released when you are done with it (typically via `defer mapa.deinit()`), in keeping with the patterns shown in [Dynamic allocation](18-dynamic-allocation.md).

## Design rationale

Splitting maps into a fixed literal plus a library type keeps the language small while honoring **explicit > implicit**. The fixed form is genuinely zero-cost: its size is in the type, so the compiler can lay it out inline and even fold lookups at compile time. The dynamic form never allocates behind your back — you can always point to the `_alloc` (or `_gcAlloc`) that owns its memory. And because `Map(K, V)` is an ordinary generic struct, it requires no special compiler magic: it is built from the same generics, operator overloading (`operator_get` / `operator_set`), and allocator conventions every other container uses.

## Related

- [Arrays and lists](07-arrays-and-lists.md)
- [Tuples and destructuring](38-tuples-and-destructuring.md)
- [Dynamic allocation](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Loops](06-loops.md)

[← Index](README.md)
