# Code Formatting (dfmt)

DLang ships a single canonical formatter, **dfmt**, so that every DLang program in the wild looks the same. There is no style to configure and no options to bikeshed: one input has exactly one formatted output. The formatter is an AST-based pretty-printer — it parses your source to the untyped syntax tree and re-emits it from scratch — so it enforces the layout rather than merely tidying whitespace.

Because it works from the parse tree, dfmt **refuses to touch a file that does not parse**. A syntax error is reported and the file is left untouched rather than risk corrupting it. Formatting is therefore always safe: it can only ever produce valid, equivalent source.

## Running the formatter

```bash
python -m tasty.format file.dlang            # print formatted source to stdout
python -m tasty.format -i file.dlang ...     # rewrite files in place
python -m tasty.format --check file.dlang    # exit non-zero if a file is not formatted
python -m tasty.format -                     # format stdin -> stdout
```

With multiple files, `-i`/`--check` apply to each; without either flag the formatted text of every file is concatenated to stdout. `--check` is what you wire into CI — it writes nothing and fails if any file is not already formatted. `-i` and `--check` are mutually exclusive.

## Guarantees

dfmt makes three promises, each verified by its test suite (unit tests plus a corpus pass over every `*.dlang` file in the repository):

- **Idempotent** — `format(format(x)) == format(x)`. Running it twice never changes anything the first run produced.
- **Comment-preserving** — no comment text is ever lost. Comments are recovered by an independent scan of the raw source (the lexer discards them) and re-attached to the declaration they belong to.
- **Semantics-preserving** — the output always re-parses, and precedence is preserved by parenthesization, so meaning never changes.

## The style

### Indentation and width

Two-space indentation, targeting a **120-column** width. Constructs that fit stay on one line; only those that would overflow 120 columns are broken.

### Block-based control flow

Every `if` / `else` / `while` / `for` / `match` / `try` in **statement position** is expanded to braces on their own lines — dfmt never emits an inline statement body. The same applies to `if` and `match` used in **value position**: they expand to block form rather than staying on one line.

```dlang
pick :: (a: int, b: int) -> int = if (a > b) {
  a
} else {
  b
}
```

A function body that is a single, simple expression keeps the inline `= expr` form; only control-flow values expand.

### Grouped parameters expand

Parameters that share a type in the source (`(a, b: int)`) are always written out in full so each name carries its own annotation:

```dlang
add :: (a: int, b: int) -> int = a + b
```

### One member per line

Struct, enum, and interface bodies are laid out one member per line. Long calls, arrays, tuples, struct literals, map literals, and parameter lists that would exceed 120 columns wrap to **one element per line**:

```dlang
build :: () = createWidget(
  titleText,
  widthInPixels,
  heightInPixels,
  backgroundColor,
  borderColor,
  isVisibleFlag,
  zIndexValue
)
```

### Literals and small niceties

- Leaf literals — integers, doubles, chars, strings — are copied **verbatim** from source, so digit separators (`1_000_000`), string interpolation (`${x}`), escapes, and triple-quoted strings are never disturbed.
- Ranges are written tight: `0..count`, not `0 .. count`.
- A trailing lambda drops empty parentheses: `xs.map { ... }`, never `xs.map() { ... }`.
- The binding keywords are normalized: `const` is written `const val` and `lazy` is written `lazy val`.

### Comments

A single `//` line is kept as-is. A **run of two or more consecutive own-line `//` comments folds into one `/* ... */` block**, since `//` reads best for a single line:

```dlang
/*
  first
  second
  third
*/
```

Existing `/* */` blocks are preserved, and a trailing `//` comment stays attached to its line.

## Grouping methods under their type

A method — a definition whose target is `Owner.name` — is **reordered to sit directly after the definition of the type it belongs to**, no matter where you wrote it in the file. Methods keep their original relative order, and each one carries its leading doc-comment with it. This means you can add a method anywhere while editing, and dfmt files it in the right place.

Given input where the struct and its methods are scattered:

```dlang
Writer.close :: () -> throws (IOError)

Box :: struct { value: int }

Writer.write :: (n: int) -> throws (int, IOError)

Writer :: struct { fd: int }
```

dfmt clusters each type with its methods:

```dlang
Box :: struct {
  value: int
}

Box.get :: () -> int

Writer :: struct {
  fd: int
}

Writer.close :: () -> throws (IOError)

Writer.write :: (n: int) -> throws (int, IOError)
```

Only methods whose owning type is defined **in the same file** are relocated. A method on a type declared elsewhere is left exactly where you put it (so extension-style methods in another module stay put).

Reordering applies in *declaration contexts* — the top level of a module and the body of a `namespace`. It never reorders statements inside a function body, where order is meaningful.

## Vertical alignment

Consecutive definitions are aligned so their `::` line up, forming a clean column. dfmt aligns a **run** of adjacent function definitions that share the same owner and the same shape (all signatures, all expression-bodied, or all block-bodied). A definition that carries its own leading comment starts a fresh run.

```dlang
read  :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
write :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
close :: (fileDescriptor: int) -> long
fsync :: (fileDescriptor: int) -> int
```

The same alignment applies to a type's method group, and generic parameters are part of the aligned target:

```dlang
Writer.write       :: (bytes: Ptr(byte), count: int) -> throws (int, IOError)

Writer.writeString :: (str: string) -> throws (int, IOError)

Writer.writeByte   :: (byt: byte) -> throws (IOError)

Writer.print(T)    :: (x: T)

Writer.println(T)  :: (x: T)

Writer.flush       :: () -> throws (IOError)  // fsync

Writer.close       :: () -> throws (IOError)
```

Alignment is not limited to functions. Within a struct, enum, or interface body, dfmt aligns members when the list is uniform:

- **struct fields** align their `:`
- **interface methods** align their `::`
- **enum variants** with explicit values align their `=`

```dlang
Token :: enum {
  Plus  = 1
  Minus = 2
  Star  = 3
}
```

## Blank lines between definitions

The spacing between two adjacent definitions is decided by what kind of definitions they are, not by how many blank lines you happened to type. Within a run of related definitions:

| Kind of definition | Spacing |
|---|---|
| Block-bodied implementation (`f :: () { ... }`) | one blank line between each |
| Method **signature** (`Writer.write :: ...`, owner present) | one blank line between each |
| Free / external **signature** (`read :: ...`, no owner) | tight — no blank line |
| Expression body (`f :: () = expr`) | tight — no blank line |

Unrelated groups — a type and its method block, or two different owners — are always separated by a single blank line. The effect is that a table of external C signatures stays compact, while a type's methods breathe:

```dlang
read  :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
write :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long

Writer :: struct {
  fileDescriptor: int
}

Writer.write       :: (bytes: Ptr(byte), count: int) -> throws (int, IOError)

Writer.writeString :: (str: string) -> throws (int, IOError)
```

## Known limitations

A few constructs are intentionally left as you wrote them:

- Long **binary / boolean expressions** are not wrapped; only breakable containers (calls, arrays, tuples, struct/map literals, parameter lists) are.
- A comment that sits **inside a wrapped expression** re-anchors to the nearest statement boundary rather than staying mid-expression.
- **Multi-statement lambdas** are kept inline.

## Design rationale

A single canonical format removes an entire category of decisions and diffs from day-to-day work: there is nothing to argue about in review, and a reformatting run never buries a real change under whitespace churn. Building the formatter on the parse tree — rather than on tokens or regexes — is what lets it do more than reindent: it can safely reorder methods under their type and align columns, because it understands the structure it is printing. The grouping and alignment rules exist so that the shape of the code mirrors the shape of the data: a type and everything that acts on it read as one visual block, and a column of aligned `::` turns a list of declarations into a table you can scan at a glance.

## Related

- [Functions and Procedures](09-functions.md)
- [Custom Data Structures (structs)](17-structs.md)
- [Enumerations](16-enumerations.md)
- [Interfaces and Abstract Classes](25-interfaces.md)
- [Modules and Namespaces](19-modules-and-namespaces.md)
- [C Interoperability (FFI)](50-c-interop.md)

[← Index](README.md)
