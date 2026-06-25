# Loops and Iteration

DLang offers two looping constructs — `while` for condition-driven repetition and `for` for iterating over a collection — plus an ergonomic placeholder form of `for` for the common "do something with each element" case. Like conditionals, loops keep the C-style surface: parenthesized headers and mandatory braces.

## `while`

A `while` loop repeats its body as long as the parenthesized condition holds. This is the tool for repetition driven by a changing condition rather than a fixed collection:

```dlang
var contador: int = 0
while (contador < 10) {
  contador++
}
```

Note that the counter is a `var`, because it is mutated on each pass; an immutable `val` could not be incremented. See [Variables and Scope](04-variables-and-scope.md) for the mutability rules.

## `for` over a collection

The `for (x : coll)` form binds each element of a collection to a name in turn and runs the body once per element. The element type is inferred from the collection, so you do not annotate it:

```dlang
val nomes: []string = ["gabriel", "bruno"]   // implicitly [2]string
for (nome : nomes) {
  println(nome)
}
```

On each iteration `nome` is bound to the next element of `nomes`. This is the idiomatic way to walk arrays and lists. When iterating a key-value map, the loop variable destructures into a `(key, value)` pair — that variant is covered in [Maps and Dictionaries](08-maps-and-dictionaries.md).

## The automatic placeholder form

For the very common case where the body simply uses each element once, DLang provides a shorter form: `for (coll)` with no explicit variable. Inside such a loop the element is available as the universal placeholder `_`. The placeholder is passed automatically — it behaves like a one-argument lambda `x -> ...` whose parameter is `_`:

```dlang
for (nomes) {
  println(_)
}
```

This reads as "for each of `nomes`, print it." It is exactly equivalent to `for (x : nomes) { println(x) }`, just without naming the throwaway variable. This form is provided by the standard library rather than being compiler magic, and it reuses the same `_` placeholder you see in lambdas and method bodies — one idea, applied consistently.

## Design rationale

Two loop constructs cover the two genuinely different needs — repeat while a condition holds, and visit every element of a collection — without piling on variants. The placeholder `for` form exists because the most frequent loop body uses its element exactly once, and naming a variable just to immediately consume it is noise. Making `_` mean "the current element" here is the same convention used for the implicit lambda argument and for `this`/`self` in methods, so a reader who knows `_` in one place already knows it everywhere. Keeping the placeholder form a library feature rather than a keyword reinforces the language's stance that behavior is sugar over data, not built-in privilege.

## Related

- [Variables and Scope](04-variables-and-scope.md)
- [Conditionals](05-conditionals.md)
- [Arrays and Native Lists](07-arrays-and-lists.md)
- [Maps and Dictionaries](08-maps-and-dictionaries.md)
- [Lambda Expressions](39-lambda-expressions.md)

[← Index](README.md)
