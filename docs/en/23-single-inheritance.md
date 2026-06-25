# Single Inheritance

> Status: Deliberately absent

DLang has no inheritance. A [struct](17-structs.md) cannot extend another struct, there is no `extends` or base-class relationship, and there is no `super`. This applies to the simplest case — one type inheriting from one parent — and it is a deliberate choice, not a missing feature. Reuse in DLang is achieved through **composition**.

## Why there is no inheritance

Classical inheritance forcibly welds together two things that are actually independent: the **layout of data in memory** and the **behavior** (the methods). When `Cachorro` inherits from `Animal`, it inherits both the fields *and* the methods, and it inherits an "is-a" identity that ties it into a type hierarchy. For a data-oriented language this coupling is a liability. You frequently want to reuse a chunk of data layout without dragging behavior along, or share behavior across types that have nothing to do with each other structurally. Inheritance gives you no way to take one without the other.

Inheritance also makes cost and layout harder to read. A derived type's memory layout depends on a chain of ancestors you may not have in front of you, and a method call may resolve to an override several levels up or down the hierarchy. Both problems get worse the deeper the tree grows. DLang refuses the tree entirely.

## What to use instead: composition

To reuse data, you **embed one struct inside another, explicitly**. The inner struct is a named field; you reach its data through that field. Nothing is hidden, and the layout is exactly what you wrote.

```dlang
Animal :: struct {
  nome: string
  vida: int
}

Animal.respirar :: () {
  println("${_.nome} está respirando")
}

// Cachorro does NOT inherit Animal. It COMPOSES it: Animal is a field.
Cachorro :: struct {
  base: Animal        // embedded data, reached through `.base`
  raca: string
}

// Behavior specific to Cachorro is just a function on Cachorro.
Cachorro.latir :: () {
  println("${_.base.nome} faz au au")
}

usar :: () {
  var rex = Cachorro {
    base: Animal { nome: "Rex", vida: 100 },
    raca: "Vira-lata"
  }

  rex.base.respirar()   // reuse Animal's behavior, explicitly, via the field
  rex.latir()           // Cachorro's own behavior
  println(rex.base.vida)
}
```

The relationship is visible: a `Cachorro` *has an* `Animal`, it is not *an* `Animal`. When you want the shared behavior you call it through the field (`rex.base.respirar()`), which makes the reuse explicit and the data path obvious. If you also want `Cachorro` values to be usable polymorphically wherever an `Animal`-like contract is expected, that is the job of an [interface](25-interfaces.md), not of a base class — composition supplies the data, the interface supplies the substitutability.

## Design rationale

Composition keeps the two halves of "reuse" separate, which is exactly what inheritance fuses. You decide independently which data to embed and which behavior to call, and both decisions are written out in the source. There is no hidden base layout, no override that fires from an ancestor you forgot about, and no fragile-base-class problem where changing a parent silently breaks children. When you need substitutability — the genuinely useful part of inheritance — you reach for structural [interfaces](25-interfaces.md), which give you polymorphism with a visible, bounded cost and without dragging an entire layout hierarchy behind it.

## Related

- [Structs](17-structs.md)
- [Classes and Objects](20-classes-and-objects.md)
- [Multiple Inheritance](24-multiple-inheritance.md)
- [Interfaces and Abstract Classes](25-interfaces.md)
- [Polymorphism](26-polymorphism.md)

[← Index](README.md)
