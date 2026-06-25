# Custom Data Structures

A struct is DLang's fundamental tool for grouping related data under one named type. It is a plain aggregate of fields — a description of memory layout — with no inheritance, no vtables, and no hidden machinery. Behavior can be attached to a struct, but as you will see, that behavior is pure syntax sugar over functions, not object orientation.

## Defining a struct

You bind a struct type with `::`, listing each field with a `name: Type` annotation:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
  ativo: boolean
}
```

This declares `Pessoa` as a type with three fields laid out in memory in the order written. There is nothing more to it — a struct is exactly its fields. Field types are always annotated explicitly; inference is not permitted in a struct definition, just as it is not in a function signature.

## Methods are sugar over functions

You can attach a method to a struct using the `Tipo.metodo :: (...)` form. Inside the method, the placeholder `_` stands in for the instance being operated on — the equivalent of `this` or `self` in other languages, but without any of the object-oriented baggage:

```dlang
Pessoa.falar :: (mensagem: string) {
  println("${_.nome} diz: ${mensagem}")
}
```

This is important: `Pessoa.falar` is just a function that happens to take a `Pessoa` (bound to `_`) plus a `mensagem`. There is no vtable, no dynamic dispatch, no inheritance. The dot syntax is a convenience for grouping a function with the type it works on, and calls are resolved statically — `usuario.falar("oi")` compiles to a direct call, exactly as fast as a free function.

## Constructing and accessing

A struct value is created by calling the type name with its field values in order:

```dlang
val usuario: Pessoa = Pessoa("Gabriel", 25, true)
```

This produces a `Pessoa` with `nome = "Gabriel"`, `idade = 25`, `ativo = true`. The value lives wherever you declare it — on the stack here — with no heap allocation involved. Fields are read and written through the dot:

```dlang
println(usuario.nome)
```

You can also construct with explicit field names using brace syntax (`Pessoa { nome: "Gabriel", idade: 25, ativo: true }`), which is the form used in pattern matching and is handy when you want field names visible at the construction site.

## Design rationale

A struct is just a layout of data, and that is exactly the point: keeping data and behavior separate is the heart of the data-oriented model. There is no class, no inheritance, and no `private` — hiding fields would add complexity for the compiler and barriers for performance without buying much in a systems language. When you want to reuse data, you compose: place one struct inside another explicitly, rather than inheriting. When you want shared behavior across types, you use a structural interface (a fat pointer), not a base class. Methods exist purely as ergonomic sugar — `Tipo.metodo` with `_` as the instance — so that the call site reads naturally while the generated code remains a plain, statically-dispatched function call with zero overhead.

## Related

- [Dynamic allocation](18-dynamic-allocation.md)
- [Constructors and destructors](21-constructors-and-destructors.md)
- [Enumerations](16-enumerations.md)
- [Interfaces](25-interfaces.md)
- [Operator overloading](27-operator-overloading.md)
- [Pattern matching](37-pattern-matching.md)
- [Generics](32-generics.md)

[← Index](README.md)
