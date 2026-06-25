# Polymorphism

Polymorphism — writing code that works uniformly across many types — exists in DLang, but it is split cleanly into two mechanisms with very different costs, both of which are visible to the programmer. There is **runtime polymorphism** through [interfaces](25-interfaces.md), resolved with a fat pointer, and **compile-time polymorphism** through [operator overloading](27-operator-overloading.md) and [generics](32-generics.md), resolved entirely before the program runs. There is deliberately no inheritance-based polymorphism and no virtual-method dispatch (see [Virtual Methods](28-virtual-methods.md)).

## Runtime polymorphism via interfaces

When you need a value whose concrete type is only known at runtime to behave according to a shared contract, you use an interface. A function that takes an interface parameter accepts any type that satisfies the contract, and calls the contract's methods through a fat pointer.

```dlang
Desenhavel :: interface {
  desenhar :: ()
}

// `objeto` may be a Circulo, a Quadrado, anything that satisfies Desenhavel.
// The concrete type is chosen at runtime; the call goes through the fat pointer.
renderizarTela :: (objeto: Desenhavel) {
  objeto.desenhar()
}
```

This is the only form of polymorphism in DLang that has a runtime dispatch step, and even that step is just a single indirect call through the function pointer half of the fat pointer — close to the cost of a plain call, with no hierarchy walk. The full mechanism is described in [Interfaces and Abstract Classes](25-interfaces.md).

## Compile-time polymorphism via operator overloading

Operators are polymorphic too: `+` means one thing for `int` and another for `Vetor2D`, and `[]` works on both arrays and user-defined collections. This is **syntactic polymorphism**, and it is resolved entirely at compile time (static dispatch). The compiler sees the operator, looks up the corresponding reserved method on the operand's type, and emits a direct call to it.

```dlang
val v1 = Vetor2D { x: 1.0, y: 2.0 }
val v2 = Vetor2D { x: 3.0, y: 4.0 }
val soma = v1 + v2        // compiler rewrites to v1.operator_add(v2)
```

Because the resolution happens before the program runs, there is zero runtime cost — the call is as fast as any plain function call. The details and the full list of overloadable operators are in [Operator Overloading](27-operator-overloading.md).

## Compile-time polymorphism via generics

A third form lets one piece of code work over many types by parameterising on the type itself. A generic `max` works for any comparable type; a generic `List(T)` works for any element type. The compiler instantiates a specialised version for each type used, so there is no boxing and no dispatch — the generated code is as if you had written it by hand for that type. See [Generics](32-generics.md).

```dlang
max(T) :: (a, b: T) -> T = if (a > b) a else b
val m = max(10, 20)       // T = int inferred; specialised at compile time
```

## Choosing a mechanism

| You need… | Use | Cost |
| --- | --- | --- |
| Behavior chosen at **runtime** from a shared contract | [Interfaces](25-interfaces.md) | One indirect call (fat pointer) |
| A symbol like `+` or `[]` to work on your type | [Operator overloading](27-operator-overloading.md) | Zero — static dispatch |
| One algorithm to work over many types | [Generics](32-generics.md) | Zero — specialised per type |

The guiding rule is that you pay for dynamic dispatch only when you genuinely need a runtime decision, and you ask for it explicitly by typing a parameter as an interface. Everything else is resolved at compile time.

## Design rationale

Splitting polymorphism by cost is what keeps DLang predictable. In an OO language, a method call may be static, virtual, or interface-dispatched, and the syntax does not tell you which — so you cannot read the cost off the page. Here the mechanism is always legible: an interface-typed parameter means a fat-pointer call, an operator or a generic means the work was done at compile time. You get the full expressive range of polymorphism, but you never pay for dynamic dispatch by accident.

## Related

- [Interfaces and Abstract Classes](25-interfaces.md)
- [Operator Overloading](27-operator-overloading.md)
- [Virtual Methods](28-virtual-methods.md)
- [Generics](32-generics.md)
- [Function Pointers](33-function-pointers.md)

[← Index](README.md)
