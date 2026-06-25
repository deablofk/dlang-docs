# Tuples and Destructuring

A tuple is an **anonymous, positional aggregate**. It is a value type: it lives on the stack, costs zero, and needs no allocator. Think of it as the "throwaway struct" for when you do not want to name a type. In DLang the tuple unifies three things that are often separate features — [multiple return](11-multiple-returns.md), destructuring, and [pattern matching](37-pattern-matching.md) — into a single concept.

## 1. Type and literal

A tuple type and a tuple value are both written as a parenthesized, comma-separated list:

```dlang
val ponto: (int, int) = (10, 20)
val registro: (string, int, boolean) = ("Gabriel", 25, true)
```

## 2. Access — destructuring only (no `.0`, no `[0]`)

The only way to read a tuple's contents is to destructure it. There is no positional field access:

```dlang
val (x, y) = ponto          // the only way to extract the values
val (_, y) = ponto          // '_' ignores a slot (the same '_' as in match)
val (x, _) = ponto
val (nome, idade, _) = registro
```

A tuple can be swapped without a temporary variable, and tuples nest:

```dlang
// swap with no temporary
(a, b) = (b, a)

// nested
val (nome, (px, py)) = ("base", (1, 2))
```

### Why destructuring only

A tuple is *heterogeneous* — each position has its own type. A positional index into it would therefore have to be a compile-time literal so the compiler could know the resulting type, which is different from a *homogeneous* array `[i]`, where every element has the same type and `i` may be a runtime value. Rather than invent a `.0` or a `[0]` with special compile-time-literal rules, the tuple simply has no positional access at all. If you need random access, reach for a struct (named) or an array (homogeneous).

## 3. Multiple return is returning a tuple

A function that returns multiple values is, exactly, a function that returns a tuple. `return 10, 10` is sugar for `return (10, 10)`:

```dlang
buscarCoordenadas :: () -> (int, int) = (10, 10)   // 'return 10, 10' == 'return (10, 10)'
val (cx, cy) = buscarCoordenadas()
```

## 4. Where tuples were already in use

Several existing features turn out to be tuples, now unified under one concept:

```dlang
val conteudo, err = lerArquivo("config.txt")   // destructures a tuple (string, Erro)
for (chave, valor : keyValueMap) { ... }         // 'for' iterates tuples (chave, valor)
```

## 5. Struct destructuring outside match

The struct-destructuring form from [pattern matching](37-pattern-matching.md) also works as a plain binding, outside any `match`:

```dlang
val Pessoa { nome, idade } = usuario
println(nome)
```

## The parentheses rule

The use of parentheses is single and predictable:

- **Tuple value or type:** always parenthesized — `(10, 20)`, `(int, int)`.
- **`val`/`var` binding and `return`:** optional, because the keyword already delimits the tuple. `val a, b = f()` is the same as `val (a, b) = f()`, and `return 1, 2` is the same as `return (1, 2)`.
- **Inside `match`, `for`, or when nested:** mandatory — `(x, y) ->`, `(nome, (x, y))`.

## Access table by type

DLang gives exactly one access form per type, so the forms never collide:

| Form | Type | Why |
|------|------|-----|
| `[i]` | array / List | homogeneous, runtime index |
| `.campo` | struct | heterogeneous, named |
| `val (a, b) =` | tuple | heterogeneous, anonymous, destructuring only |

## Design rationale

By making the tuple a stack-resident value type with no positional access, DLang keeps a clean division of labor: arrays for homogeneous indexed data, structs for named heterogeneous data, tuples for the quick, anonymous, heterogeneous grouping you destructure immediately. Multiple return, `for` over a map, and error returns all collapse into this one concept instead of being three separate language features.

## Related

- [Multiple Returns](11-multiple-returns.md)
- [Pattern Matching](37-pattern-matching.md)
- [Structs](17-structs.md)
- [Arrays and Lists](07-arrays-and-lists.md)

[← Index](README.md)
