# Function Pointers

In DLang a function is a first-class value. Because functions are declared with `::` (a name bound to a function literal), the function itself is just data that happens to be callable, and it can be stored in a variable, passed as an argument, or laid out in an array — without any new syntax.

## The type of a function

A function type is written as the list of input types in parentheses followed by `->` and the output type:

```dlang
// the type of a function is (input-types) -> output-type
val op: (int, int) -> int = somar   // 'somar' defined with :: fits here
```

Any named function whose signature matches the type can be assigned to such a variable. There is no wrapper, no boxing, no decoration — the function name *is* the value.

## Calling through a function value

Unlike a data pointer (`Ptr(T)`), which is dereferenced through `.value`, a function value is called directly. The parentheses themselves are the call operator:

```dlang
// called directly, without .value (unlike a data pointer)
val r = op(2, 3)   // 6
```

This is the deliberate asymmetry between `Ptr(T)` and a function type: a data pointer points *at* something you must read, while a function value already *is* the thing you invoke.

## Passing functions as parameters

Because a function type is an ordinary type, it can appear in a parameter list. This is the foundation that everything else in this part of the language builds on — [closures](34-closures.md), [higher-order functions](35-higher-order-functions.md), and [lambda expressions](39-lambda-expressions.md).

```dlang
// pass a function as a parameter
aplicar :: (f: (int, int) -> int, a, b: int) -> int = f(a, b)

aplicar(somar, 10, 5)   // 15
```

## Dispatch tables

Since a function value is plain data, you can store many of them in a fixed array and index into it. This gives you a *dispatch table*: a data-oriented replacement for a chain of conditionals or a virtual table.

```dlang
// dispatch table: an array of function pointers
val operacoes: [2]((int, int) -> int) = [somar, subtrair]
val res = operacoes[0](4, 2)
```

The array holds the functions contiguously; selecting one is an index, and calling it is a direct jump. There is no hidden indirection beyond the index you wrote yourself.

## Design rationale

Function pointers fall out of one rule already present in the language: a function is a name bound to a function literal. Making that literal a value costs nothing and unlocks the whole functional layer. Calling without `.value` keeps the call site clean while preserving the clear, explicit dereference rule for data pointers.

## Related

- [Closures and Anonymous Functions](34-closures.md)
- [Higher-Order Functions](35-higher-order-functions.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Pointers and References](12-pointers-and-references.md)

[← Index](README.md)
