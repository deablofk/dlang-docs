# Interfaces and Abstract Classes

DLang has no classes and no inheritance, but it does have **contracts**. An `interface` declares a set of method signatures with no bodies; a struct that provides matching methods satisfies the interface and can be used wherever the interface is expected. This is how DLang delivers runtime polymorphism — substitutability — without a class hierarchy. There is no separate notion of an "abstract class," because an interface already plays that role: it is the pure contract, with the data left entirely to the implementing struct.

## Declaring an interface

An interface lists the methods an implementer must provide. The bodies are absent on purpose — the interface is the *requirement*, not the implementation.

```dlang
// Requires a `desenhar` method taking no arguments and returning nothing.
Desenhavel :: interface {
  desenhar :: ()
}
```

## Implementing an interface

A struct implements the interface by providing the required methods. The implementation uses the `as` form to declare which contract this method satisfies, and the usual `_` placeholder for self. The compiler checks that every method the interface demands is present and matches the signature — a missing or mismatched method is a compile-time error pointing at exactly what is wrong.

```dlang
Circulo :: struct {
  raio: int
}

// `Circulo as Desenhavel.desenhar` says: this is Circulo's implementation of the
// `desenhar` method required by the Desenhavel contract.
Circulo as Desenhavel.desenhar :: () {
  println("Desenhando um círculo com raio ${_.raio}")
}
```

The match is **structural**: `Circulo` satisfies `Desenhavel` because it provides the methods the contract names, not because it was declared to "extend" anything. A single struct can satisfy any number of interfaces this way, with no diamond ambiguity (see [Multiple Inheritance](24-multiple-inheritance.md)).

## Using an interface for polymorphism

A function that takes an interface type can accept any value whose type satisfies that contract. Inside the function the compiler knows the required methods exist and lets you call them safely.

```dlang
renderizarTela :: (objeto: Desenhavel) {
  // The compiler guarantees `objeto` has `.desenhar`.
  objeto.desenhar()
}

executar :: () {
  val c = Circulo { raio: 10 }
  renderizarTela(c)        // works: Circulo satisfies Desenhavel
}
```

## How it works: fat pointers

When you pass a concrete value where an interface is expected, the compiler builds an **interface fat pointer**: a pair consisting of a pointer to the struct's data and a pointer to the function that implements the contract for that type. A call like `objeto.desenhar()` then becomes a single indirect call through the function pointer in the fat pointer.

This is the key to the design. There is no class hierarchy to walk, no vtable to inherit, and no per-object overhead beyond the two-word fat pointer that exists only while the value is being used through the interface. The indirect call costs essentially the same as a [function pointer](33-function-pointers.md) call, so interface-based polymorphism runs close to the speed of a plain function call — exactly the property a systems language needs from its one runtime-polymorphism mechanism.

## Design rationale

An interface is the honest, minimal form of an abstract class: it carries the contract and nothing else, so it never drags data layout or identity along with it. Because satisfaction is structural and checked at compile time, you get the substitutability you wanted from inheritance — pass a `Circulo` where a `Desenhavel` is expected — without coupling types into a tree. And because the runtime representation is a transparent fat pointer rather than a hidden vtable, the cost is visible and bounded: one indirect call, two words of pointer, no surprises.

## Related

- [Structs](17-structs.md)
- [Polymorphism](26-polymorphism.md)
- [Single Inheritance](23-single-inheritance.md)
- [Multiple Inheritance](24-multiple-inheritance.md)
- [Function Pointers](33-function-pointers.md)
- [Generics](32-generics.md)

[← Index](README.md)
