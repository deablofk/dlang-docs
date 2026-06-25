# Multiple Inheritance

> Status: Deliberately absent

DLang has no multiple inheritance. Since the language has no [single inheritance](23-single-inheritance.md) at all, inheriting from several parents is doubly out of the question. This is the most clear-cut absence in the whole object-oriented chapter, and the reasoning is worth stating plainly because multiple inheritance is the canonical example of a feature that costs far more than it gives.

## Why there is no multiple inheritance

Multiple inheritance inherits every problem of single inheritance and multiplies them. The coupling of data layout and behavior, the fragile base class, the hard-to-read method resolution — each of these gets worse when a type has more than one parent. On top of that, multiple inheritance introduces its own signature pathology: the **diamond problem**.

The diamond problem arises when a type inherits from two parents that themselves share a common ancestor:

```
        A
       / \
      B   C
       \ /
        D
```

If both `B` and `C` inherit a field or method from `A` and then `D` inherits from both `B` and `C`, the language must answer impossible-to-make-clean questions: does `D` contain one copy of `A`'s data or two? If `B` and `C` each override a method from `A` differently, which override does `D` get? Every language that has tried to support this — C++ with virtual inheritance, Python with its MRO algorithm — has had to bolt on intricate, surprising rules to disambiguate, and programmers still get bitten. The feature manufactures ambiguity and then asks you to memorise the tie-breaking rules.

DLang sidesteps all of it by not having inheritance to begin with.

## What to use instead

Two needs hide behind "I want to inherit from several types": reusing several pieces of data, and satisfying several contracts. DLang handles them with two clean, orthogonal tools.

**To combine data from several sources, compose several fields.** There is no ambiguity because each embedded struct is reached through its own named field — two copies of `A` would simply be two differently-named fields, and you choose which one you mean.

```dlang
Posicao :: struct { x: float, y: float }
Saude   :: struct { vida: int, maxVida: int }

// Inimigo composes both. No diamond, no ambiguity: each part has its own name.
Inimigo :: struct {
  posicao: Posicao
  saude: Saude
  nome: string
}

mover :: (e: Inimigo) {
  println("${e.nome} em ${e.posicao.x}, ${e.posicao.y}")
}
```

**To satisfy several contracts, implement several interfaces.** A single struct can implement any number of [interfaces](25-interfaces.md), because an interface is a structural contract about which methods exist, not a parent whose data and identity you absorb. There is no diamond here either: implementing two interfaces that both demand a method named `desenhar` just means you provide one `desenhar` that satisfies both.

```dlang
Desenhavel :: interface { desenhar :: () }
Serializavel :: interface { serializar :: () -> string }

Circulo :: struct { raio: int }

Circulo as Desenhavel.desenhar :: () {
  println("círculo de raio ${_.raio}")
}

Circulo as Serializavel.serializar :: () -> string {
  return "Circulo(${_.raio})"
}
// Circulo now satisfies BOTH contracts, with zero ambiguity.
```

## Design rationale

The diamond problem is not an implementation detail to be engineered around — it is evidence that "inherit from many parents" is an under-specified idea. By separating the two real needs into composition (for data) and interfaces (for contracts), DLang gives you everything multiple inheritance was supposed to provide, with none of the ambiguity. Combining data is explicit and unambiguous because every part has a name; combining contracts is unambiguous because an interface adds no data and no identity, only a checked requirement that certain methods exist.

## Related

- [Single Inheritance](23-single-inheritance.md)
- [Structs](17-structs.md)
- [Interfaces and Abstract Classes](25-interfaces.md)
- [Polymorphism](26-polymorphism.md)
- [Classes and Objects](20-classes-and-objects.md)

[← Index](README.md)
