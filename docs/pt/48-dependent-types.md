# Sistema de Tipos Dependentes

> Status: Limitado.

DLang oferece uma forma **limitada e prática** de tipagem dependente: *valores* de tempo de compilação podem parametrizar tipos, e esses valores participam da checagem de tipos. É o mesmo nível que Zig alcança. O que DLang **não** tem são tipos dependentes completos — tipos indexados por valores de *runtime*, ou tipos carregando provas. A linha divisória é exatamente a fronteira compile-time/runtime.

## O que existe: valores como parte do tipo

Um parâmetro de tipo pode ser um inteiro de tempo de compilação, e esse inteiro passa a fazer parte da identidade do tipo.

```dlang
Vetor(T, N: int) :: struct {
  data: [N]T // N é um valor, mas conhecido em compile-time
}
```

`N` é resolvido durante a compilação, então `Vetor(float, 3)` e `Vetor(float, 4)` são tipos genuinamente diferentes. Como `N` é parte do tipo, o compilador consegue checar que as dimensões batem:

```dlang
// N participa da checagem de tipos: dimensões incompatíveis = erro de compilação
somar(N: int) :: (a: Vetor(float, N), b: Vetor(float, N)) -> Vetor(float, N) { ... }

val a: Vetor(float, 3) = ...
val b: Vetor(float, 3) = ...
val c = somar(a, b)        // OK, N = 3 inferido

val d: Vetor(float, 4) = ...
val e = somar(a, d)        // erro de compilação: N=3 vs N=4 não casam
```

O mesmo mecanismo torna seguras operações dimensionadas como a multiplicação de matrizes — a função só passa na checagem de tipos quando as dimensões internas se alinham:

```dlang
Matriz(L: int, C: int) :: struct { data: [L][C]float }
multiplicar(L, M, N: int) :: (a: Matriz(L, M), b: Matriz(M, N)) -> Matriz(L, N) { ... }
```

Uma chamada em que a dimensão compartilhada `M` não casa em ambos os operandos simplesmente não compila.

## O que não existe: tipos dependendo de valores de runtime

Um tipo nunca pode depender de um valor que só é conhecido enquanto o programa roda.

```dlang
lerN :: () -> int = ...        // valor só conhecido em execução
// var v: Vetor(float, lerN())  // ERRO: N precisa ser compile-time
```

Para um tamanho que é genuinamente dinâmico, você não recorre ao sistema de tipos — usa um contêiner na heap (`List(T)`):

```dlang
// para tamanho dinâmico use List(T) (heap, alocador ambiente), não o tipo
var v: List(float) = List(float).empty()
```

Isso mantém uma linha dura e legível: dimensões no *tipo* são sempre fatos de compile-time; qualquer coisa que varie em runtime vive num *valor* como `List`.

## Por quê

Tipos dependentes completos — em que um tipo pode mencionar qualquer valor de runtime e o compilador raciocina sobre proposições arbitrárias no nível de valor — compram um poder expressivo enorme ao custo de um compilador muito mais pesado e uma ergonomia bem mais difícil, o que é uma troca ruim para uma linguagem de sistema. DLang pega a fatia desse poder que se paga: valores de compile-time parametrizando tipos, reaproveitando a mesma maquinaria de generics de `Buffer(T, N: int)` (veja [Generics](32-generics.md)). Essa fatia já basta para pegar bugs reais e comuns — comprimentos de vetor incompatíveis, formatos de matriz incompatíveis — inteiramente em tempo de compilação e com custo zero em runtime, porque `N` nunca existe como uma quantidade de runtime. Traçar a fronteira na linha compile-time/runtime também mantém a regra fácil de ensinar: se um tamanho pode mudar enquanto o programa roda, ele pertence a uma `List`, não a um parâmetro de tipo.

## Relacionados

- [Generics e Programação Paramétrica](32-generics.md)
- [Arrays e Listas](07-arrays-and-lists.md)
- [Tipagem Estática](29-static-typing.md)
- [Prova de Teoremas em Tempo de Compilação](49-theorem-proving.md)
- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)

[← Índice](README.md)
