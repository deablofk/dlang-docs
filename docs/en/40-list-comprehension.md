# List Comprehension

> Status: Absent.

DLang deliberately has **no** list-comprehension syntax. This is a design decision, not an omission to be filled in later.

## Why it is absent

A list comprehension would be redundant sugar over the [higher-order functions](35-higher-order-functions.md) the language already provides. Anything a comprehension expresses — filtering then mapping a source into a new list — is already written directly with `.filtrar { }` and `.map { }`. Adding a second, parallel syntax for the same operation would violate the language's "one obvious way to do it" principle.

There is also a memory concern. A comprehension produces a new list, but its syntax hides *where* and *how* that list is allocated. DLang treats allocation as something you should always see; a comprehension would smuggle a `List` allocation behind compact bracket syntax, working against the language's commitment to explicit memory.

## The idiom instead

Write the pipeline directly. It reads in the same order it executes, and the allocation of the result list lives in the methods you can see:

```dlang
val r = nums.filtrar { _ > 0 }.map { _ * 2 }
```

This expresses "keep the positives, then double them" with no special syntax and no hidden allocation beyond what `filtrar` and `map` already document.

## Design rationale

Refusing list comprehension keeps the surface area small and the cost model honest. The chained higher-order functions already cover the use case, with the same readability, while making the result list's allocation visible at the call site. Two syntaxes for one operation would buy nothing and cost both clarity and the explicit-memory guarantee.

## Related

- [Higher-Order Functions](35-higher-order-functions.md)
- [Lambda Expressions](39-lambda-expressions.md)
- [Lazy Evaluation](36-lazy-evaluation.md)
- [Arrays and Lists](07-arrays-and-lists.md)

[← Index](README.md)
