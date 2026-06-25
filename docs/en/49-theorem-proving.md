# Compile-Time Theorem Proving

> Status: Deliberately absent.

DLang is **not** a theorem prover. It is not Lean, Agda, Idris, or Coq, and it makes no attempt to encode mathematical proofs in its type system. For a systems language there is no motivating payoff in doing so: encoding proofs would weigh heavily on both the compiler and everyday ergonomics with little to show for it. What DLang offers *instead* is pragmatic compile-time verification — checks that are "strong enough" to catch real bugs without the cost of a full proof system.

## What exists instead

### Compile-time assertions

The `#assert` directive lets the compiler check a condition during compilation and fail the build with a message if it does not hold. This is the practical substitute for a proof: not "prove this is always true for all inputs", but "verify this concrete fact about the program as compiled".

```dlang
#assert(tamanhoDe(Pessoa) == 24, "the layout of Pessoa changed size!")
#assert(VERSAO >= 3, "this module requires version >= 3")
```

These run in the compiler — there is zero runtime cost — and they guard exactly the kinds of structural invariants that silently break in C: a struct's size drifting, a version assumption going stale. `#assert` is part of the unified metaprogramming system; see [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md).

### Exhaustive `match`

A `match` over an enum or tagged union must cover every variant or supply an `else`. Adding a new variant turns every non-exhaustive `match` into a compile error, so the compiler mechanically proves you have handled every case. See [Pattern Matching](37-pattern-matching.md).

### Dimension checks from limited dependent types

Because compile-time values parameterise types (see [Dependent Types](48-dependent-types.md)), a mismatched dimension `N` is a compile error. The compiler is, in a narrow and useful sense, *proving* that the shapes of your vectors and matrices line up — without any general proof machinery.

### Verified immutability and no implicit conversions

`val` and `const` give the compiler a checked guarantee that a binding never changes, and the absence of implicit numeric conversion (see [Static Typing](29-static-typing.md)) means no value silently changes width or sign. These are small, local guarantees, but they are *verified*, not merely conventional.

## Design rationale

The honest framing is that DLang's compile-time guarantees come from **assertions and structural checks**, not from dependent type theory or formal proofs. That is a deliberate ceiling, not an unfinished feature. A full proof system would force the language to reason about arbitrary propositions, dragging in heavy machinery and a steep learning curve that almost no systems programmer wants to pay for. The pragmatic alternative — `#assert`, exhaustive `match`, dimension checking, and verified immutability — captures the bugs that actually occur in systems code (wrong layouts, unhandled cases, mismatched shapes, accidental mutation, silent numeric coercion) while keeping the compiler fast and the language teachable. It is "strong enough" verification chosen on purpose over "maximally powerful" proof.

## Related

- [Dependent Types](48-dependent-types.md)
- [Pattern Matching](37-pattern-matching.md)
- [Static Typing](29-static-typing.md)
- [Enumerations](16-enumerations.md)
- [Metaprogramming and Reflection](45-metaprogramming-and-reflection.md)

[← Index](README.md)
