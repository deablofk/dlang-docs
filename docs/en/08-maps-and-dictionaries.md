# Maps and Dictionaries

A map associates keys with values. DLang offers two complementary tools: a **fixed map literal** baked directly into the language, and a **dynamic `Map(K, V)`** that lives in the standard library. The split mirrors the philosophy used for arrays and lists — the compiler knows about the small, statically-sized form, while growth-over-time is a library type that draws from the current (ambient) allocator.

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

Since the capacity is fixed, you cannot add brand-new keys beyond `N` — the bracket form updates existing entries. Lookup is a linear scan that compares keys with `==` (so `string` keys, enum keys, and integer keys all work); if the key is not present, reading yields a zero value. When you need to grow, reach for the dynamic `Map`.

### Iteration

Iterating a fixed map yields each entry as a `(key, value)` pair. The `for` loop destructures that pair directly into two names:

```dlang
for (chave, valor : keyValueMap) {
  println("Item: ${chave} | valor: ${valor}")
}
```

This is the same destructuring machinery used everywhere else in the language — the loop is simply iterating tuples, where each element is the packed `(chave, valor)` view of an entry. See [Tuples and destructuring](38-tuples-and-destructuring.md).

## Dynamic maps

When the set of keys is not known ahead of time, use `Map(K, V)`. It is a normal generic struct from the standard library — **not** a compiler builtin — built from the same generics and operator overloading every other container uses.

```dlang
var mapa: Map(string, int) = Map(string, int).empty()

mapa.set("banana", 30)              // insert or overwrite
val preco: int = mapa.get("banana") // read back
```

`.set(k, v)` inserts a new key or overwrites an existing one, growing the underlying storage when the key is absent; `.get(k)` reads it back (lookup is a linear scan keyed by `==`). Other methods include `.contains(k)`, `.remove(k)`, `.size()`, `.keyAt(i)` / `.valueAt(i)`, and `operator_get` / `operator_set` so `mapa["k"]` and `mapa["k"] = v` work too.

The memory a `Map` grows into comes from the **current allocator** — DLang's ambient, swappable memory context (see [Dynamic allocation](18-dynamic-allocation.md)), not an allocator you thread in by hand.

## Design rationale

Splitting maps into a fixed literal plus a library type keeps the language small. The fixed form is genuinely zero-cost: its size is in the type, so the compiler lays it out inline (on the stack, in a struct field, or in a global) with no heap allocation. The dynamic form draws its storage from the current allocator, so its memory model is the same swappable context every other container uses — and because `Map(K, V)` is an ordinary generic struct, it needs no special compiler magic: it is built from the same generics and operator overloading (`operator_get` / `operator_set`) as everything else.

## Related

- [Arrays and lists](07-arrays-and-lists.md)
- [Tuples and destructuring](38-tuples-and-destructuring.md)
- [Dynamic allocation](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Loops](06-loops.md)

[← Index](README.md)
