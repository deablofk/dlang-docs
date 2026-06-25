# Pointers and References

A pointer is a value that holds the memory address of another value. In DLang pointers are an ordinary, first-class type written `Ptr(T)` — the same parenthesised notation used by `List(T)` and `cast(T, x)`. There is no special `*` or `&` punctuation: you take a reference with the `ref` keyword and you read or write the pointee through a single property, `.value`.

This design is deliberate. Centralising every memory access on `.value` gives the compiler one perfect checkpoint to insert safety validation (such as null checks), which is the main mechanism DLang uses to avoid the sudden segmentation faults that plague C and C++.

## Taking a reference

You obtain a pointer to an existing variable with `ref`. The result is typed `Ptr(T)` where `T` is the type of the thing you pointed at.

```dlang
val score: int = 99

// equivalent to the old C syntax *int = &score
val ponteiroScore: Ptr(int) = ref score
```

`ref score` does not copy `score`; it produces its address. `ponteiroScore` now refers to the same storage cell.

## Reading and writing through `.value`

Every `Ptr` has a `.value` property. This is the only way to dereference — to read or mutate the thing the pointer points at.

```dlang
// to change the pointed-at value, use .value; every Ptr has .value
ponteiroScore.value = 10
println(ponteiroScore.value) // 10
```

Because access is funnelled through `.value`, the compiler always knows exactly where a dereference happens. If a pointer were null, the compiler can emit a safe, well-defined error at the `.value` access instead of letting the program crash with an unpredictable segfault.

## Rebinding versus mutating

The single most important distinction with pointers is between *changing which cell a pointer refers to* and *changing the contents of the cell it currently refers to*. DLang makes this completely unambiguous: bare assignment rebinds the pointer, while assignment through `.value` mutates the pointee.

```dlang
var a: int = 10
var b: int = 20

val ptrA: Ptr(int) = ref a
val ptrB: Ptr(int) = ref b

// rebinding: ptrA now holds the same address as ptrB
ptrA = ptrB      // both point at 'b'

// mutating: writes through the pointer into the original cell
ptrA.value = 50  // changes the value in the 'drawer' it points at
```

After `ptrA = ptrB`, the two pointers are aliases of the same storage. The subsequent `ptrA.value = 50` therefore writes `50` into whatever cell both now reference. Reading the bare pointer name compares or copies addresses; reaching for `.value` always touches the underlying data.

## Pointers to structs

`.value` chains naturally into field access, so a pointer to a struct lets you mutate fields in place:

```dlang
val pessoaPtr: Ptr(Pessoa) = _alloc.alloc(Pessoa)
pessoaPtr.value.nome = "Gabriel" // change a field inside the struct
```

Here `_alloc.alloc(Pessoa)` returns a `Ptr(Pessoa)` pointing at freshly reserved memory. See [Manual Memory Management](13-manual-memory.md) for how that allocation is paired with `defer _alloc.free(...)`.

## Function pointers are different

A pointer to a function is *not* a `Ptr(T)` and is *not* dereferenced with `.value`. A function value already carries its callable type `(int, int) -> int`, so you call it directly. Only pointers to *data* use `.value`. This topic is covered in Function Pointers.

## Design rationale

DLang treats pointers as plain data, consistent with its data-oriented philosophy: no hidden indirection, no implicit dereferencing. The `ref` keyword makes address-taking visible, and `.value` makes dereferencing visible. By forcing every read and write through one property, the language gets a single, cheap place to validate safety — turning the most dangerous operation in systems programming into a checkpoint the compiler controls. Rebinding versus mutating, which is silent and error-prone in C, becomes two visibly different operations.

## Related

- [Manual Memory Management](13-manual-memory.md)
- [Garbage Collection](14-garbage-collection.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Structs](17-structs.md)

[← Index](README.md)
