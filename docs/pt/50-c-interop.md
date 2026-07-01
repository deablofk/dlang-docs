# Interoperabilidade com C (FFI)

DLang conversa com C diretamente — sem gerador de wrappers, sem blocos `extern`,
sem parsing de cabeçalhos. Como DLang já compila através de um backend nativo e
usa a ABI C da plataforma para suas próprias chamadas, uma função C fica
acessível no momento em que você a *declara*. Esta página descreve toda a
interface de funções externas: como declarar uma função externa, como os tipos
se alinham na fronteira, como compartilhar structs e ponteiros, e como linkar as
bibliotecas que fornecem os símbolos.

## Declarando uma função externa

Uma função com **assinatura mas sem corpo** é externa. Você declara seu nome,
parâmetros e tipo de retorno; a implementação vive em uma biblioteca C que o
linker liga pelo nome do símbolo. Não há palavra-chave `extern` — a *ausência de
corpo* é o marcador inteiro, exatamente como a ausência de tipo de retorno é o
marcador inteiro de um procedimento (veja [Funções](09-functions.md)).

```dlang
// implementada na libc — nenhuma definição aqui
puts   :: (s: string) -> int
strlen :: (s: string) -> long
abs    :: (n: int) -> int

// implementada na SDL3
SDL_GetTicks     :: () -> long
SDL_CreateWindow :: (title: string, w: int, h: int, flags: long) -> Ptr(byte)
```

O nome que você escreve **é** o símbolo que o linker resolve, então ele precisa
casar exatamente com o nome exportado da função C (`SDL_Init`, `malloc`, `puts`).
Chamar uma função externa é, no resto, indistinguível de chamar uma função
DLang:

```dlang
main :: () -> int {
  puts("hello from C")
  return cast(int, strlen("abcde"))   // 5
}
```

## Mapeamento de tipos na fronteira

Os tipos DLang mapeiam para seus equivalentes C pela sua representação de ABI:

| C | DLang | Notas |
|---|-------|-------|
| `int` / `long` | `int` / `long` | inteiros com sinal de 32 / 64 bits |
| `float` / `double` | `float` / `double` | |
| `bool` | `boolean` | |
| `char *` / `const char *` | `string` | ponteiro de bytes terminado em NUL |
| `T *` | `Ptr(T)` | ponteiro para um valor de tipo correspondente |
| handle opaco (`SDL_Window *`, `FILE *`) | `Ptr(byte)` | quando você nunca o desreferencia |
| `NULL` | `null` | |
| `void` (sem retorno) | omita `-> T` | um procedimento |

Não há **conversões numéricas implícitas** na fronteira, assim como não há dentro
do DLang: se C espera um `long` e você tem um `int`, escreva `cast(long, x)`.
Isso mantém o ponto de chamada honesto quanto às larguras.

## Compartilhando structs

Um struct que você entrega ao C precisa **espelhar seu layout em C** — os mesmos
tipos de campo na mesma ordem. Você passa um ponteiro para ele com `ref`, e o C o
lê ou escreve no lugar:

```dlang
Timeval :: struct { sec: long, usec: long }   // espelha `struct timeval`

gettimeofday :: (tv: Ptr(Timeval), tz: Ptr(byte)) -> int

main :: () -> int {
  var tv: Timeval = Timeval { sec: cast(long, 0), usec: cast(long, 0) }
  gettimeofday(ref tv, null)          // C preenche tv através do ponteiro
  return 0
}
```

`ref valor` produz um `Ptr(T)` (veja [Ponteiros e Referências](12-pointers-and-references.md));
`null` fornece um `NULL` de C. Agregados em DLang têm semântica de valor, então
passar um struct *por valor* o copia — use `ref` sempre que o C precisar mutar
seus dados ou esperar um ponteiro.

## Handles opacos

Muitas APIs C devolvem um ponteiro que você deve guardar e repassar mas nunca
olhar dentro (`SDL_Window *`, `FILE *`). Modele-os como `Ptr(byte)`: você pode
armazenar e encaminhar o handle, compará-lo com `null`, e nunca precisar de seu
layout.

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

## Funções variádicas

Variádicas de C como `printf` não têm uma assinatura fixa única. Declare a
**aridade fixa** exata que você pretende chamar para um dado formato:

```dlang
printf :: (fmt: string, n: int) -> int      // este formato de chamada

main :: () -> int {
  printf("n=%d\n", 42)                       // imprime: n=42
  return 0
}
```

Cada formato distinto de argumentos que você precisar é uma declaração distinta.
Para qualquer coisa além de casos simples — ou para ter segurança sobre como a
plataforma passa argumentos variádicos — escreva um pequeno shim C de aridade
fixa e linke-o com `--c-source`, depois declare o shim.

## Linkando

A libc é linkada automaticamente, então `puts`, `strlen`, `malloc`, `abs` e
companhia funcionam sem flags extras. Para trazer outra biblioteca, nomeie-a no
build:

```bash
python -m oven app.dlang -o app -l SDL3      # linka libSDL3
python -m oven app.dlang --run -l m          # linka libm (sqrt, sin, …)
```

Flags de build para interop:

| Flag | Propósito |
|------|-----------|
| `-l NOME` / `--lib NOME` | linka `libNOME` (repetível) |
| `-L DIR` / `--lib-dir DIR` | adiciona um diretório de busca de bibliotecas |
| `--c-source ARQUIVO.c` | compila um arquivo C extra no programa (ex.: um shim) |
| `--cc-arg ARG` | passa uma flag crua diretamente ao compilador/linker C |

A API de embedding espelha essas flags: `oven.build(src, file, out, libs=["m"],
lib_dirs=[...], c_sources=[...], cc_args=[...])`.

## Exemplo completo

```dlang
// libm — linke com `-l m`
sqrt :: (x: double) -> double
// libc — automático
printf :: (fmt: string, x: double) -> int

main :: () -> int {
  val r: double = sqrt(16.0)          // 4.0, calculado pelo C
  printf("sqrt = %f\n", r)            // imprime: sqrt = 4.000000
  return cast(int, r)                 // código de saída 4
}
```

```bash
python -m oven example.dlang --run -l m
```

## Por quê

FFI em DLang é deliberadamente *nada além de uma declaração*. Como o compilador
já usa a ABI C e linka através do compilador C do sistema, expor uma função C não
exige nenhuma maquinaria nova — apenas um nome, uma assinatura e (se o símbolo
viver fora da libc) uma flag `-l`. Reutilizar `string`, `Ptr(T)`, `ref` e `null`
em vez de inventar tipos exclusivos de FFI faz a fronteira ler como DLang comum,
e a regra estrita de "sem conversão implícita" que governa o resto da linguagem
também governa a fronteira — então larguras e ponteiros nunca são silenciosamente
reinterpretados a caminho do C.

## Relacionados

- [Funções](09-functions.md)
- [Ponteiros e Referências](12-pointers-and-references.md)
- [Gerenciamento Manual de Memória](13-manual-memory.md)
- [Estruturas de Dados](17-structs.md)

[← Índice](README.md)
