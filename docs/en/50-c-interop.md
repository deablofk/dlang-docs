# C Interoperability (FFI)

DLang talks to C directly — no wrapper generator, no `extern` blocks, no header
parsing. Because DLang already compiles through a native backend and uses the
platform C ABI for its own calls, a C function is reachable the moment you
*declare* it. This page describes the whole foreign-function interface: how to
declare an external function, how types line up at the boundary, how to share
structs and pointers, and how to link the libraries that provide the symbols.

## Declaring an external function

A function with a **signature but no body** is external. You state its name,
parameters, and return type; the implementation lives in a C library that the
linker binds by symbol name. There is no `extern` keyword — the *absence of a
body* is the whole marker, exactly as the absence of a return type is the whole
marker for a procedure (see [Functions](09-functions.md)).

```dlang
// implemented in libc — no definition here
puts   :: (s: string) -> int
strlen :: (s: string) -> long
abs    :: (n: int) -> int

// implemented in SDL3
SDL_GetTicks     :: () -> long
SDL_CreateWindow :: (title: string, w: int, h: int, flags: long) -> Ptr(byte)
```

The name you write **is** the symbol the linker resolves, so it must match the C
function's exported name exactly (`SDL_Init`, `malloc`, `puts`). Calling an
external function is otherwise indistinguishable from calling a DLang one:

```dlang
main :: () -> int {
  puts("hello from C")
  return cast(int, strlen("abcde"))   // 5
}
```

## Type mapping at the boundary

DLang types map to their C counterparts by their ABI representation:

| C | DLang | Notes |
|---|-------|-------|
| `int` / `long` | `int` / `long` | 32- / 64-bit signed |
| `float` / `double` | `float` / `double` | |
| `bool` | `boolean` | |
| `char *` / `const char *` | `string` | a NUL-terminated byte pointer |
| `T *` | `Ptr(T)` | pointer to a value of a matching type |
| opaque handle (`SDL_Window *`, `FILE *`) | `Ptr(byte)` | when you never dereference it |
| `NULL` | `null` | |
| `void` (no return) | omit `-> T` | a procedure |

There are **no implicit numeric conversions** across the boundary, just as there
are none inside DLang: if C expects a `long` and you have an `int`, write
`cast(long, x)`. This keeps the call site honest about widths.

## Sharing structs

A struct you hand to C must **mirror its C layout** — the same field types in the
same order. You pass a pointer to it with `ref`, and C reads or writes it in
place:

```dlang
Timeval :: struct { sec: long, usec: long }   // mirrors `struct timeval`

gettimeofday :: (tv: Ptr(Timeval), tz: Ptr(byte)) -> int

main :: () -> int {
  var tv: Timeval = Timeval { sec: cast(long, 0), usec: cast(long, 0) }
  gettimeofday(ref tv, null)          // C fills tv through the pointer
  return 0
}
```

`ref value` produces a `Ptr(T)` (see [Pointers and References](12-pointers-and-references.md));
`null` supplies a C `NULL`. Aggregates in DLang have value semantics, so passing
a struct *by value* copies it — use `ref` whenever C needs to mutate your data or
expects a pointer.

## Opaque handles

Many C APIs hand back a pointer you are meant to keep and pass around but never
look inside (`SDL_Window *`, `FILE *`). Model these as `Ptr(byte)`: you can store
and forward the handle, compare it against `null`, and never need its layout.

```dlang
fopen  :: (path: string, mode: string) -> Ptr(byte)
fclose :: (f: Ptr(byte)) -> int

main :: () -> int {
  val f: Ptr(byte) = fopen("/tmp/x", "w")
  if (f == null) { return 1 }
  fclose(f)
  return 0
}
```

## Variadic functions

C variadics such as `printf` have no single fixed signature. Declare the exact
**fixed arity** you intend to call for a given shape:

```dlang
printf :: (fmt: string, n: int) -> int      // this one call shape

main :: () -> int {
  printf("n=%d\n", 42)                       // prints: n=42
  return 0
}
```

Each distinct argument shape you need is a distinct declaration. For anything
beyond simple cases — or to be safe about how the platform passes variadic
arguments — write a tiny fixed-arity C shim and link it with `--c-source`, then
declare the shim instead.

## Linking

libc is linked automatically, so `puts`, `strlen`, `malloc`, `abs`, and friends
work with no extra flags. To pull in another library, name it at build time:

```bash
python -m oven app.dlang -o app -l SDL3      # link libSDL3
python -m oven app.dlang --run -l m          # link libm (sqrt, sin, …)
```

Build flags for interop:

| Flag | Purpose |
|------|---------|
| `-l NAME` / `--lib NAME` | link `libNAME` (repeatable) |
| `-L DIR` / `--lib-dir DIR` | add a library search directory |
| `--c-source FILE.c` | compile an extra C file into the program (e.g. a shim) |
| `--cc-arg ARG` | pass a raw flag straight to the C compiler/linker |

The embedding API mirrors these: `oven.build(src, file, out, libs=["m"],
lib_dirs=[...], c_sources=[...], cc_args=[...])`.

## Worked example

```dlang
// libm — link with `-l m`
sqrt :: (x: double) -> double
// libc — automatic
printf :: (fmt: string, x: double) -> int

main :: () -> int {
  val r: double = sqrt(16.0)          // 4.0, computed by C
  printf("sqrt = %f\n", r)            // prints: sqrt = 4.000000
  return cast(int, r)                 // exit code 4
}
```

```bash
python -m oven example.dlang --run -l m
```

## Design rationale

FFI in DLang is deliberately *nothing but a declaration*. Because the compiler
already uses the C ABI and links through the system C compiler, exposing a C
function needs no new machinery — only a name, a signature, and (if the symbol
lives outside libc) a `-l` flag. Reusing `string`, `Ptr(T)`, `ref`, and `null`
rather than inventing FFI-only types means the boundary reads like ordinary
DLang, and the strict "no implicit conversion" rule that governs the rest of the
language also governs the boundary — so widths and pointers are never silently
reinterpreted on the way to C.

## Related

- [Functions](09-functions.md)
- [Pointers and References](12-pointers-and-references.md)
- [Manual Memory Management](13-manual-memory.md)
- [Structs](17-structs.md)

[← Index](README.md)
