# Constructors and Destructors

DLang has no magic constructors — construction is a plain **factory function** you call by name, with no hidden control flow. Destruction, on the other hand, *is* automatic, but in a very specific, visible way: a type that owns something declares a **`deinit`** method, and the compiler calls it **exactly once, at the value's last use**. You never schedule cleanup and you cannot forget it — and because the release point is the *last use*, not a hidden scope boundary, you can read it off the source.

## Construction: factory functions

A struct literal already gives you a value with every field set. When you need to encapsulate the work of building a valid instance — choosing defaults, initialising an inner list — you write a factory function. The convention is `Tipo.new` (or a more specific name), returning a fully-formed value:

```dlang
Jogador :: nocopy struct {
  nome: string
  vida: int
  inventario: List(string)
}

// Factory: builds and returns a valid Jogador. There is no hidden `new`.
Jogador.new :: (nome: string) -> Jogador {
  return Jogador {
    nome: nome,
    vida: 100,
    inventario: List(string).empty()
  }
}
```

Because the factory is just a function, you can have as many as you like with different names (`Jogador.newEmpty`, `Jogador.fromFile`), each returning the same type. There is no privileged "the constructor" and no overload resolution to reason about — you call the one whose name says what it does. (The struct above is `nocopy` because it contains a `List` — a struct with an owning field is itself an owner, by contagion.)

For initializing a caller's slot *in place* — the pattern C solves with an out-pointer — use a `set` parameter instead of a return; see [Parameter Passing](10-parameter-passing.md).

## Destruction: `deinit`, automatic and ASAP

A `nocopy` type that owns a resource declares `deinit`. The compiler inserts the call at the value's **static last use** — as soon as the value is provably dead, on every control-flow path, exactly once. There are no drop flags and no runtime bookkeeping; the analysis is entirely static ([Memory Safety](14a-memory-safety.md)).

```dlang
Jogador.deinit :: () {
  println("${_.nome} foi limpo da memória")
  // owned fields (like _.inventario) are dropped automatically after this body
}

jogar :: () {
  var player: Jogador = Jogador.new("Gabriel")
  player.inventario.add("espada longa")
  println(player.nome)          // last use — deinit runs right here
  expensiveThingUnrelatedToPlayer()
}
```

Three properties are worth internalizing:

- **Exactly once, every path.** Early `return`, `break`, fall-through — the compiler proves one release per path. Double-free is not a runtime bug class; a shape that would cause one is `E_USE_AFTER_MOVE` at compile time.
- **ASAP, not scope-end.** The value dies at its last *use*, so memory and resources are returned as early as the program allows.
- **Ownership composes.** A `deinit` body releases what the *struct itself* holds raw (an fd, a C resource); owned **fields** (a `List`, a `ByteBuf`, another owner) are dropped recursively without you writing anything.

If ownership is transferred — the value is moved into a `sink` parameter, stored into a container, or returned — the destructor responsibility moves with it; the old binding is dead (`E_USE_AFTER_MOVE` if touched) and no double release can occur.

## What about `defer`?

`defer statement` still exists and still runs at every function exit — but it is no longer how values are destroyed. Use it for effects that are *not* ownership: logging a completion, flushing at end of a phase, test teardown. If you find yourself writing `defer x.release()`, the type should be a `nocopy` owner with a `deinit` instead — then the compiler does it, correctly, on every path.

## Design rationale

The old objection to automatic destructors — "invisible code running at invisible times" — is answered differently than C++ answers it. Construction stays a named function: no hidden allocation, no implicit conversions, you see every cost. Destruction is automatic but *deterministic and readable*: `deinit` is ordinary code you wrote, and it runs at the value's last use, a point you can find by reading the function. What DLang removes is not visibility but *manual scheduling* — the one part humans reliably get wrong (the forgotten free, the double free on an early return). The compiler is simply better at placing the call than a `defer` you had to remember to write.

## Related

- [Structs](17-structs.md)
- [Memory Safety](14a-memory-safety.md)
- [Manual Memory — the Builtin floor](13-manual-memory.md)
- [Dynamic Allocation](18-dynamic-allocation.md)
- [Parameter Passing](10-parameter-passing.md)

[← Index](README.md)
