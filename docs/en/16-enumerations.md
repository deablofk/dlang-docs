# Enumerations

An enumeration is a named type whose values are drawn from a fixed, finite set of named constants. In DLang an enum is bound with `::`, like any other type, and in its simplest form it is just a set of integer-backed names.

## Plain integer enums

Declaring an enum with `enum { ... }` gives each variant an automatic integer value, starting at `0` and counting up in declaration order:

```dlang
Erro :: enum {
  ArquivoNaoEncontrado, // 0
  PermissaoNegada       // 1
}
```

`ArquivoNaoEncontrado` is `0`, `PermissaoNegada` is `1`. You rarely need to think about the underlying numbers — the point of the enum is to give meaningful names to a closed set of cases, so that code reads in terms of intent rather than magic integers.

## Custom values with `enum(int)`

When the numeric values matter — for example HTTP status codes that must match a wire protocol — annotate the backing type as `enum(int)` and assign each variant explicitly:

```dlang
StatusHttp :: enum(int) {
  Ok = 200,
  NotFound = 404,
  InternalError = 500
}
```

Here the names carry their real-world numbers. The `(int)` parenthesized type echoes the same call-notation used throughout the language (`Ptr(T)`, `List(T)`), and makes the backing representation explicit rather than assumed.

## Using an enum

You refer to a variant through its enum type, which keeps the namespace clean and makes the origin of each constant obvious:

```dlang
val codigo: StatusHttp = StatusHttp.NotFound
```

Enums pair naturally with `match`, which can branch on each variant by name. Because the compiler knows the full set of cases, a `match` over an enum can be checked for exhaustiveness:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("arquivo sumiu")
  Erro.PermissaoNegada      -> println("acesso negado")
  else                      -> println("ok")
}
```

## Enums that carry data

The enums shown here are plain *tags* — each variant is just a name (optionally with a fixed integer). DLang also supports **tagged-union enums**, where a variant carries its own payload of fields, for example `Circulo(raio: float)`. Those are a richer construct: the only safe way to read a variant's payload is through `match`, which destructures it. Because that behavior is inseparable from pattern matching, it is documented there rather than here — see [Pattern matching](37-pattern-matching.md) for enums-with-data.

## Design rationale

Plain enums are nothing more than named integers, so they cost exactly what an integer costs — no boxing, no runtime type information, no allocation. Making the backing type explicit with `enum(int)` keeps you honest about representation when it matters (protocols, file formats) while letting the auto-numbered form stay terse when it does not. Routing data-carrying variants through `match` is what guarantees safety: there is no way to read `Circulo.raio` off a value that is actually a `Retangulo`, because the payload is only reachable after the tag has been checked. This is the data-oriented replacement for class hierarchies — a compact tag plus payload, with the compiler enforcing that you handle every case.

## Related

- [Pattern matching](37-pattern-matching.md)
- [Conditionals](05-conditionals.md)
- [Error handling](15-error-handling.md)
- [Structs](17-structs.md)
- [Static typing](29-static-typing.md)

[← Index](README.md)
