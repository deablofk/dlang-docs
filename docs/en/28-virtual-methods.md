# Virtual Methods

> Status: Deliberately absent

DLang has no virtual methods. There is no `virtual` keyword, no `override`, no vtable, and no mechanism by which a method call silently dispatches to an overridden implementation chosen by an object's dynamic type. Because the language has no [classes](20-classes-and-objects.md) and no [inheritance](23-single-inheritance.md), there is no hierarchy for a virtual method to dispatch across in the first place. This absence is a direct consequence of being a data-oriented systems language.

## Why there are no virtual methods

A virtual method is the runtime-dispatch heart of object-oriented programming: each object carries a hidden pointer to a vtable, and a call like `obj.metodo()` follows that pointer to find the right implementation for the object's actual type. This buys you polymorphism, but it imposes costs a systems language does not want to pay silently:

- **A hidden per-object pointer.** Every object of a polymorphic class carries a vtable pointer, inflating its size and disturbing the tight, predictable layout that data-oriented code depends on. An array of such objects is no longer a clean array of data.
- **An indirect call you cannot see.** `obj.metodo()` looks identical to a plain method call but secretly performs a pointer indirection, which the CPU cannot predict as well as a direct call and which the compiler usually cannot inline. The cost is invisible in the syntax.
- **Coupling to inheritance.** Virtual dispatch only makes sense inside a class hierarchy, and DLang has rejected that hierarchy for the reasons given under [Single Inheritance](23-single-inheritance.md) and [Classes and Objects](20-classes-and-objects.md).

In short, a virtual method hides both a memory cost and a dispatch cost behind ordinary-looking syntax. DLang's whole stance is that such costs should be visible and opt-in.

## What to use instead

DLang offers two replacements, each making its cost legible.

**When you need runtime dispatch, use an [interface](25-interfaces.md).** This is the explicit, opt-in version of a virtual method. You declare the contract, a struct implements it, and a function that takes the interface dispatches through a fat pointer:

```dlang
Desenhavel :: interface {
  desenhar :: ()
}

Circulo :: struct { raio: int }

Circulo as Desenhavel.desenhar :: () {
  println("círculo de raio ${_.raio}")
}

// Runtime dispatch happens HERE, and it is visible: the parameter is typed as
// the interface, so you know `desenhar` goes through the fat pointer.
renderizarTela :: (objeto: Desenhavel) {
  objeto.desenhar()
}
```

The difference from a virtual method is honesty. The dispatch cost appears exactly where a parameter is typed as an interface — never hidden inside an innocent-looking `obj.metodo()` on a concrete type. The fat pointer carries the function pointer alongside the data only while the value is used through the interface; the struct itself stays a clean, vtable-free block of data.

**When you do not need runtime dispatch, use a plain method.** A `Tipo.metodo` call on a concrete type is always a direct, statically-resolved call with no indirection — the common case pays nothing.

## Design rationale

Removing virtual methods is the natural endpoint of removing classes and inheritance. The useful capability they provided — choosing behavior at runtime based on a value's type — survives as the interface, but with two crucial differences: the data stays free of any embedded vtable pointer, and the dispatch cost is announced by the type of the parameter rather than buried in a call that looks ordinary. You get runtime polymorphism precisely when you ask for it, you pay one visible indirect call when you use it, and you pay nothing the rest of the time.

## Related

- [Interfaces and Abstract Classes](25-interfaces.md)
- [Polymorphism](26-polymorphism.md)
- [Classes and Objects](20-classes-and-objects.md)
- [Single Inheritance](23-single-inheritance.md)
- [Function Pointers](33-function-pointers.md)

[← Index](README.md)
