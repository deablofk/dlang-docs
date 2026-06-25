# Compreensão de Listas

> Status: Ausente.

DLang deliberadamente **não** tem sintaxe de compreensão de listas. Isso é uma decisão de design, não uma omissão a ser preenchida depois.

## Por que está ausente

Uma compreensão de listas seria açúcar redundante sobre as [funções de ordem superior](35-higher-order-functions.md) que a linguagem já oferece. Qualquer coisa que uma compreensão expressa — filtrar e então mapear uma fonte em uma nova lista — já é escrita diretamente com `.filtrar { }` e `.map { }`. Acrescentar uma segunda sintaxe paralela para a mesma operação violaria o princípio da linguagem de "um jeito óbvio de fazer".

Há também uma preocupação de memória. Uma compreensão produz uma nova lista, mas sua sintaxe esconde *onde* e *como* essa lista é alocada. DLang trata a alocação como algo que você deve sempre ver; uma compreensão contrabandearia uma alocação de `List` atrás de uma sintaxe compacta de colchetes, indo contra o compromisso da linguagem com a memória explícita.

## O idioma no lugar

Escreva o pipeline diretamente. Ele se lê na mesma ordem em que executa, e a alocação da lista de resultado mora nos métodos que você pode ver:

```dlang
val r = nums.filtrar { _ > 0 }.map { _ * 2 }
```

Isso expressa "mantenha os positivos, então dobre-os" sem sintaxe especial e sem alocação escondida além do que `filtrar` e `map` já documentam.

## Por quê

Recusar a compreensão de listas mantém a superfície pequena e o modelo de custo honesto. As funções de ordem superior encadeadas já cobrem o caso de uso, com a mesma legibilidade, ao mesmo tempo que tornam a alocação da lista de resultado visível no ponto de chamada. Duas sintaxes para uma operação não comprariam nada e custariam tanto a clareza quanto a garantia de memória explícita.

## Relacionados

- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Expressões Lambda](39-lambda-expressions.md)
- [Avaliação Preguiçosa](36-lazy-evaluation.md)
- [Arrays e listas](07-arrays-and-lists.md)

[← Índice](README.md)
