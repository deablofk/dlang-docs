# Modules and Namespaces

DLang organises code with two complementary ideas. A **module** is a whole file: every `.dlang` file is automatically a module, with no boilerplate or special declaration required. A **namespace** is a named grouping of declarations *inside* a file, created with a `namespace` block. Together they let you split a program across files and still carve out logical groupings within a single file.

## Files are modules automatically

You do not declare a module — the file *is* the module. Top-level declarations in a file are simply the module's members.

```dlang
// file with an automatic module
// the file name: matematica.dlang

// an ordinary constant function of your system
somar :: (a, b: int) -> int = a + b
```

The constant binding `::` introduces `somar` as a compile-time-known function (see Functions). Because the file is a module, `somar` becomes a member that other files can import.

## Importing a module

`import("path")` loads another module and returns its namespace as a value. You bind that value to a name and reach its members through dot access.

Paths are **root-relative**: the project root is the nearest directory above your file that contains a `project.dlang` marker, and every import resolves against it — never relative to the importing file. There is **no `..`** and **no `.dlang` suffix** (it is implicit):

```dlang
// project.dlang marks the root; this resolves to <root>/matematica.dlang
val mat = import("matematica")

principal :: () {
  val resultado = mat.somar(10, 5)
  println(resultado)
}
```

`import` is an expression that yields a first-class namespace value, so `mat` is an ordinary binding — there is no special import statement syntax to memorise, and the imported names live **only** behind `mat.`, never dumped into your scope. This keeps origins explicit: reading `mat.somar` tells you exactly where `somar` came from. The rule is enforced — a bare `somar` from another module is a compile error. It applies to types too: a type from `mat` is written `mat.Tipo`, usable anywhere a type is expected (annotations, `mat.Tipo { .. }` literals, `mat.Tipo.factory()`).

## Inner namespaces

Within one file you can group related declarations under a name using `Nome :: namespace { ... }`. The members are then reached with `Nome.member`, exactly like the members of an imported module.

```dlang
// creating an inner namespace in the same file
Geometria :: namespace {
    const val PI: float = 3.14159

    areaQuadrado :: (lado: int) -> int = lado * lado
}

// to use it in the same file:
val area = Geometria.areaQuadrado(4)
```

Note the symmetry: `Geometria.areaQuadrado` (an inner namespace) and `mat.somar` (an imported module) are accessed identically. A namespace block can hold any declarations — constants like `PI` bound with `const val`, functions, structs — and bundles them under one dotted prefix.

## Modules and namespaces are the same shape

The reason `import` and `namespace` feel interchangeable is that they produce the same kind of thing: a named bag of members accessed with a dot. An imported file *is* a namespace value; an inner `namespace { ... }` block *is* a namespace value. Whether a grouping lives in its own file or inside a larger one, you consume it the same way.

## Design rationale

Treating every file as an automatic module removes ceremony: there is nothing to declare and nothing to keep in sync between a file's name and its module name. Making `import` return a first-class namespace value, rather than splicing names into the current scope, keeps every external reference traceable to its source and avoids name collisions by default. Reusing the *same* namespace concept for in-file grouping means there is exactly one mental model — a dotted bag of members — whether you are reaching across files or organising one. Nothing here needs runtime support; it is purely how declarations are named and resolved at compile time.

## Related

- [Functions](09-functions.md)
- [Structs](17-structs.md)
- [Static Typing](29-static-typing.md)

[← Index](README.md)
