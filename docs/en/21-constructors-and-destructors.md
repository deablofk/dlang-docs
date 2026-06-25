# Constructors and Destructors

DLang has no magic constructors and no magic destructors, because it has no [classes](20-classes-and-objects.md). There is no method that runs automatically when a value is born, and no method that runs automatically when it dies. Instead, construction is a plain **factory function** you call by name, and destruction is a plain method you schedule with `defer`. Both are ordinary code you can read, and neither hides any control flow.

## Construction: factory functions

A struct literal already gives you a value with every field set. When you need to encapsulate the work of building a valid instance — choosing defaults, initialising an inner dynamic list, talking to an allocator — you write a factory function. The convention is `Tipo.criar`, which returns a fully-formed value of the type.

```dlang
Jogador :: struct {
  nome: string
  vida: int
  inventario: List(string)
}

// Factory: builds and returns a valid Jogador. There is no hidden `new`.
Jogador.criar :: (nome: string) -> Jogador {
  return Jogador{
    nome: nome,
    vida: 100,
    inventario: List(string).init(_alloc)
  }
}
```

Because the factory is just a function, you can have as many as you like with different names (`Jogador.criarVazio`, `Jogador.criarDeArquivo`), each returning the same type. There is no privileged "the constructor" and no overload resolution to reason about — you call the one whose name says what it does.

## Destruction: a plain method plus `defer`

Some values own resources that must be released: a dynamic list holds heap memory, a file handle holds an OS resource. DLang expresses cleanup as an ordinary method — conventionally `Tipo.destruir` — that releases whatever the value owns. Nothing calls it for you; **you schedule it explicitly with `defer`**, which guarantees it runs when the enclosing scope exits, no matter how (normal return, early return, or error).

```dlang
// Destructor: releases everything this value owns.
Jogador.destruir :: () {
  _.inventario.deinit()                 // frees the inner dynamic list
  println("${_.nome} foi limpo da memória")
}
```

## Putting it together

The idiomatic lifecycle pairs the factory and the destructor at the top of the scope, so the cleanup is visible right next to the creation:

```dlang
jogar :: () {
  // 1. Build the data.
  var player = Jogador.criar("Gabriel")

  // 2. Guarantee the destructor runs when this scope ends.
  defer player.destruir()

  // 3. Use the data normally.
  player.inventario.add("espada longa")
  println(player.nome)

  // When `jogar` returns, the deferred player.destruir() runs automatically.
}
```

This is the same pattern you already use for raw memory (`defer _alloc.free(p)`) and dynamic collections (`defer itens.deinit()`), described in [Dynamic Allocation](18-dynamic-allocation.md) and [Manual Memory](13-manual-memory.md). The factory/`defer destruir()` pair is simply that pattern applied to a struct that owns resources.

## Design rationale

Automatic constructors and destructors are convenient precisely because they are invisible — and invisibility is the enemy of a systems language. A hidden constructor can allocate without you seeing it; a hidden destructor can run expensive cleanup at a scope boundary you did not think about. By making construction a named function and destruction an explicit `defer`, DLang keeps the cost and the timing of a value's lifecycle in plain sight. You always know what runs, and you always know exactly when. The `defer` mechanism gives you the safety of guaranteed cleanup — it fires on every exit path — without surrendering the visibility that RAII-style hidden destructors take away.

## Related

- [Structs](17-structs.md)
- [Classes and Objects](20-classes-and-objects.md)
- [Manual Memory](13-manual-memory.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Arrays and Lists](07-arrays-and-lists.md)

[← Index](README.md)
