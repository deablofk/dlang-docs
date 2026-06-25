# Encapsulation and Access Modifiers

> Status: Deliberately absent

DLang has no access modifiers. There is no `private`, no `protected`, no `public`, and no getters or setters generated to guard fields. Every field of a [struct](17-structs.md) is directly readable and writable wherever the struct's type is visible. This is a deliberate decision for a data-oriented systems language, not a feature that was overlooked.

## Why there is no `private`

Encapsulation in the object-oriented sense exists to hide data behind a wall of methods, so that the "internal state" of an object can only be touched through an approved interface. That model assumes the object owns its data and that outside code should not be trusted with it. A data-oriented language inverts that assumption: data is the primary thing, it is meant to be looked at and laid out and transformed directly, and the code that operates on it is secondary. Wrapping every field in a `private` barrier with accessor methods adds ceremony, indirection, and compiler complexity for no benefit that this language values. You end up writing `getNome()` and `setNome()` that do nothing but read and write a field the caller could have touched directly.

There is also a cost argument. Accessor methods that exist purely to satisfy `private` are either inlined away (in which case they were pure ceremony) or they are real calls (in which case they cost something for nothing). Languages like Zig and Odin — DLang's closest relatives — take the same position: in a systems context, hiding the layout of your data from the programmer who must reason about its memory is a barrier, not a protection.

## What to use instead

You communicate intent through **naming conventions, modules, and documentation**, not through compiler-enforced walls. A struct simply exposes its fields:

```dlang
Conta :: struct {
  titular: string
  saldo: int        // no `private`; readable and writable directly
}

// Behavior that enforces an invariant is offered as a function, not imposed
// by hiding the field. Callers who want the check call this; the field is
// still there for code that legitimately needs raw access.
Conta.depositar :: (valor: int) {
  if (valor <= 0) return
  _.saldo = _.saldo + valor
}

usar :: () {
  var c = Conta { titular: "Gabriel", saldo: 0 }
  c.depositar(100)      // the guarded path
  println(c.saldo)      // direct read — perfectly legal, nothing is hidden
}
```

When you genuinely want to limit what other code can reach, the unit of boundary is the **[module](19-modules-and-namespaces.md)**, not the field. A module chooses which names it exposes when imported; what it does not export is simply not visible to importers. That gives you a real, coarse-grained boundary at the level where it matters — between compilation units — without sprinkling `private` across every field of every struct.

## Design rationale

The point of refusing access modifiers is to keep the data transparent. In a data-oriented program you frequently want to view the same bytes through different lenses — iterate a field across an array of structs, serialise a record, cast a pointer, inspect layout with reflection. Every `private` field is friction against those legitimate operations. By trusting the programmer with direct field access and reserving boundaries for the module level, DLang keeps structs honest: a struct is exactly its fields, with nothing hidden behind them, and what you read is what is really there in memory.

## Related

- [Structs](17-structs.md)
- [Classes and Objects](20-classes-and-objects.md)
- [Modules and Namespaces](19-modules-and-namespaces.md)
- [Constructors and Destructors](21-constructors-and-destructors.md)
- [Single Inheritance](23-single-inheritance.md)

[← Index](README.md)
