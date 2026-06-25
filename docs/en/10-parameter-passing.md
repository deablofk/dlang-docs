# Parameter Passing

Once you have defined a function (see [Functions and procedures](09-functions.md)), you call it by supplying arguments. DLang supports **positional** arguments, **named** arguments, and **default** values, and these three combine to give flexible, readable call sites without needing function overloading.

## Positional arguments

The simplest call passes arguments in declaration order. Each value is matched to the parameter in the same position:

```dlang
val a: int = 10

funcaoNome :: (parametroUm: int) -> int = parametroUm

funcaoNome(a)
```

The argument `a` lands in `parametroUm` because it is in the first (and only) position. Positional calling is concise and is the right choice when the parameter order is obvious from context.

## Named arguments

You can instead address a parameter by name using `parametroNome = valor` at the call site. This is invaluable when a function has optional parameters and you want to set one without supplying the others, or simply to make a call self-documenting:

```dlang
funcaoNome :: (parametroUm: int = 10, parametroDois: int) -> int = parametroUm + parametroDois

funcaoNome(parametroDois = a)
```

Here `parametroUm` already has a default of `10`, and the caller only needs to provide `parametroDois`. By naming it explicitly, the call skips straight to the parameter that matters — `parametroUm` keeps its default, and the result is `10 + a`. Without named arguments you would be unable to "jump over" the defaulted parameter.

## Combining defaults, positional, and named

Default values (covered in [Functions and procedures](09-functions.md)) are what make named arguments powerful. A parameter with a default may be omitted entirely; a parameter without one must be supplied, either positionally or by name. A common and readable pattern is to pass the required arguments positionally and reach for named arguments only when overriding a specific optional parameter:

```dlang
configurar :: (host: string, porta: int = 8080, tls: boolean = false)

configurar("localhost")                 // porta=8080, tls=false
configurar("localhost", tls = true)     // skips porta, names tls
configurar("localhost", 9090)           // porta=9090 positionally
```

## Design rationale

Named arguments plus defaults deliberately replace function overloading. Instead of declaring three versions of `configurar` to cover the optional cases, you declare one function and let the call site express intent. This keeps the symbol table small and resolution trivial — there is exactly one `configurar`, so there is nothing to disambiguate. It also fits the **explicit > implicit** philosophy: a named argument states exactly which parameter it fills, leaving no doubt at the call site. As with everything else in DLang, no hidden conversions happen to the arguments; values are passed as their declared types, and a mismatch is a compile error rather than a silent coercion.

## Related

- [Functions and procedures](09-functions.md)
- [Multiple return values](11-multiple-returns.md)
- [Pointers and references](12-pointers-and-references.md)
- [Static typing](29-static-typing.md)

[← Index](README.md)
