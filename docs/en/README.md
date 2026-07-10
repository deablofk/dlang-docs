# DLang Documentation (English)

**DLang** is a data-oriented systems programming language inspired by Jai, Zig,
Odin and Scala. This is the full topic index. _(Use the language selector in the
header to switch to Português.)_

## Design philosophy

- **Data-oriented, no OOP** — no classes, no inheritance, no vtables. Behavior is
  *syntax sugar over data*; polymorphism is achieved with structural interfaces
  (fat pointers).
- **Explicit over implicit** — an ambient, swappable allocator context
  (`New(T)`, `pushAllocator`), explicit `.value` pointer dereference, no implicit
  numeric conversions (though bare integer literals adapt), no hidden heap allocation.
- **Zero-cost / static dispatch** — generics by monomorphization, interfaces as fat
  pointers, operator overloading resolved entirely at compile time.
- **Bindings:** `::` binds a compile-time constant (function, type); `val` is an
  immutable runtime binding; `var` is mutable; `const val` is a true constant.
- **`_` is the universal placeholder** — `this`/`self` inside methods, the implicit
  argument in single-argument lambdas, and the ignored slot in patterns/destructuring.
- **C-style surface, expression-oriented core** — `()` in conditions and loops,
  mandatory braces, but `if`/`match` are expressions and functions can be `= expr`.
- **Library-first concurrency** — coroutines, promises and channels live in the
  standard library; the compiler only exposes a context-switch intrinsic and atomics.
- **Unified metaprogramming** — `@annotations` on declarations and `#directives` at
  use sites power intrinsics, compile-time execution, reflection and macros.

## Topics

### Fundamentals
1. [Primitive Types](01-primitive-types.md)
2. [Text Literals](02-text-literals.md)
3. [Arithmetic Operators](03-arithmetic-operators.md)
4. [Variables and Scope](04-variables-and-scope.md)
5. [Conditionals](05-conditionals.md)
6. [Loops and Iteration](06-loops.md)

### Data structures
7. [Arrays and Native Lists](07-arrays-and-lists.md)
8. [Maps and Dictionaries](08-maps-and-dictionaries.md)
16. [Enumerations](16-enumerations.md)
17. [Custom Data Structures (structs)](17-structs.md)

### Functions
9. [Functions and Procedures](09-functions.md)
10. [Parameter Passing](10-parameter-passing.md)
11. [Multiple Return Values](11-multiple-returns.md)
33. [Function Pointers](33-function-pointers.md)
34. [Closures and Anonymous Functions](34-closures.md)
35. [Higher-Order Functions](35-higher-order-functions.md)
39. [Lambda Expressions](39-lambda-expressions.md)
50. [C Interoperability (FFI)](50-c-interop.md)

### Memory
12. [Pointers and References](12-pointers-and-references.md)
13. [Manual Memory Management](13-manual-memory.md)
14. [Garbage Collection](14-garbage-collection.md)
18. [Dynamic Allocation](18-dynamic-allocation.md)

### Error handling & modules
15. [Error Handling](15-error-handling.md)
19. [Modules and Namespaces](19-modules-and-namespaces.md)

### Types & contracts (the "no OOP" model)
20. [Classes and Objects](20-classes-and-objects.md)
21. [Constructors and Destructors](21-constructors-and-destructors.md)
22. [Encapsulation and Access Modifiers](22-encapsulation.md)
23. [Single Inheritance](23-single-inheritance.md)
24. [Multiple Inheritance](24-multiple-inheritance.md)
25. [Interfaces and Abstract Classes](25-interfaces.md)
26. [Polymorphism](26-polymorphism.md)
27. [Operator Overloading](27-operator-overloading.md)
28. [Virtual Methods](28-virtual-methods.md)

### Type system
29. [Static Typing](29-static-typing.md)
30. [Dynamic Typing](30-dynamic-typing.md)
31. [Type Inference](31-type-inference.md)
32. [Generics and Parametric Programming](32-generics.md)
48. [Dependent Types](48-dependent-types.md)
49. [Compile-Time Theorem Proving](49-theorem-proving.md)

### Functional programming
36. [Lazy Evaluation](36-lazy-evaluation.md)
37. [Pattern Matching](37-pattern-matching.md)
38. [Tuples and Destructuring](38-tuples-and-destructuring.md)
40. [List Comprehension](40-list-comprehension.md)

### Concurrency
41. [Multithreading and Concurrency](41-concurrency.md)
42. [Coroutines and Promises](42-coroutines-and-promises.md)
43. [Async/Await Programming](43-async-await.md)
44. [Channels and Message Passing](44-channels.md)

### Metaprogramming
45. [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)
46. [Macros and Code Expansion](46-macros.md)
47. [Runtime Compilation](47-runtime-compilation.md)

### Tooling
51. [Code Formatting (dfmt)](51-formatting.md)
