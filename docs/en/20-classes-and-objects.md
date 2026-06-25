# Classes and Objects

> Status: Deliberately absent

DLang is not an object-oriented language. There is no `class` keyword, no objects in the OOP sense, no inheritance, no vtables, and no virtual dispatch. This is not an omission waiting to be filled — it is a deliberate design stance for a data-oriented systems language.

## Why there are no classes

The class is the central abstraction of object-oriented programming, and it bundles three separate things into one construct: the **layout of data in memory**, the **behavior** (methods) that operates on that data, and an **identity** that ties instances to a type hierarchy. For a language whose whole purpose is to make memory layout and runtime cost obvious, fusing these concerns is exactly the wrong move. A class hides where the data lives, how big it is, and what it costs to call a method on it — all the things a systems programmer needs to see.

DLang keeps these concerns separate. **Data is described by a `struct`**, which is a plain, transparent record of fields with a predictable layout. **Behavior is plain functions** attached to a type by syntax sugar — `Tipo.metodo :: (...)` with `_` as the implicit self — which compile down to ordinary function calls with no hidden dispatch table. There is no third thing called an "object"; there are values of a struct type, and there are functions that take them.

## What to use instead

When you would reach for a class, you describe the data with a [struct](17-structs.md) and attach behavior as methods:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
  ativo: boolean
}

// Behavior is syntax sugar over data. This is NOT a method bound to an object,
// and it does NOT go through a vtable. `_` is the placeholder for self.
Pessoa.falar :: (mensagem: string) {
  println("${_.nome} diz: ${mensagem}")
}

val usuario: Pessoa = Pessoa("Gabriel", 25, true)
usuario.falar("olá")          // resolves to a direct, static function call
println(usuario.nome)         // fields are read directly, no accessor ceremony
```

The dot in `usuario.falar(...)` looks like a method call from an OO language, but the compiler simply rewrites it into a normal function applied to `usuario`. There is no dynamic dispatch unless you explicitly opt in through an [interface](25-interfaces.md), and even then the cost is a single indirect call through a fat pointer — never a class hierarchy walk.

## How the OO toolbox maps to DLang

| Object-oriented idea | DLang replacement |
| --- | --- |
| Class (data + methods) | [`struct`](17-structs.md) + `Tipo.metodo` functions |
| Constructor | [Factory function](21-constructors-and-destructors.md) `Tipo.criar :: (...)` |
| Inheritance | [Composition](23-single-inheritance.md) — embed one struct in another |
| Interface / abstract class | [`interface`](25-interfaces.md) (structural, fat pointer) |
| Runtime polymorphism | [Interfaces](26-polymorphism.md) and operator overloading |
| Encapsulation (`private`) | [None](22-encapsulation.md) — data is transparent by design |

## Design rationale

Removing classes is what makes the rest of the language honest. Once data and behavior are decoupled, you can lay out arrays of structs for cache-friendly iteration, you can see every allocation, and you can reason about the cost of every call by reading it. Reuse happens through explicit composition rather than implicit inheritance, and polymorphism — when you genuinely need it — is an opt-in structural interface with a visible, bounded cost. The class did not disappear because it was hard to implement; it disappeared because the data-oriented model is simpler and more predictable without it.

## Related

- [Structs](17-structs.md)
- [Constructors and Destructors](21-constructors-and-destructors.md)
- [Encapsulation and Access Modifiers](22-encapsulation.md)
- [Single Inheritance](23-single-inheritance.md)
- [Interfaces and Abstract Classes](25-interfaces.md)
- [Polymorphism](26-polymorphism.md)

[← Index](README.md)
