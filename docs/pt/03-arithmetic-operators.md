# Operadores Aritméticos

DLang oferece o conjunto familiar de operadores aritméticos para trabalhar com tipos numéricos. Eles seguem a sintaxe de superfície convencional ao estilo C, então quem vem de C, Zig ou Scala os lê de imediato. O que permanece coerente com o resto da linguagem é que eles operam apenas sobre valores do mesmo tipo — não há coerção escondida entre tipos numéricos.

## Os operadores binários

Os cinco operadores binários centrais são adição, subtração, multiplicação, divisão e o resto (módulo):

```dlang
val a: int = 1 + 1
val b: int = 1 - 1
val c: int = 1 * 1
val d: int = 1 / 1
val e: int = 1 % 1
```

`+`, `-`, `*` comportam-se como esperado. `/` é divisão inteira quando ambos os operandos são inteiros, e `%` produz o resto dessa divisão. Como aqui ambos os operandos são `int`, o resultado é `int`. Se você quisesse divisão de ponto flutuante, usaria operandos `float` ou `double` — a linguagem não promove silenciosamente um `int` para `double` por você (veja [Tipagem Estática](29-static-typing.md)).

## Incremento e decremento

DLang suporta os operadores `++` e `--` tanto na posição prefixa quanto na pós-fixa, e a distinção entre elas é a mesma do C. A forma **pós-fixa** produz o valor *antes* da mudança; a forma **prefixa** produz o valor *depois* da mudança:

```dlang
val f: int = e++   // f recebe o valor antigo de e, depois e aumenta
val g: int = ++e   // e aumenta primeiro, depois g recebe o novo valor
val h: int = e--   // h recebe o valor antigo de e, depois e diminui
val i: int = --e   // e diminui primeiro, depois i recebe o novo valor
```

Como esses operadores mutam o operando, só fazem sentido sobre uma ligação mutável (`var`). Aplicá-los a um `val` imutável é erro de compilação — veja [Variáveis e Escopo](04-variables-and-scope.md) para as regras de mutabilidade.

## Operadores são expressões

Como o resto da linguagem, uma expressão aritmética *é* um valor, e os operadores aritméticos participam do design orientado a expressões. Eles são também o exemplo canônico de resolução de operadores em tempo de compilação: para os seus próprios tipos você pode dar significado a `+` (e companhia) definindo `operator_add` e métodos similares, que o compilador resolve com despacho estático de custo zero. Esse mecanismo é coberto em [Sobrecarga de Operadores](27-operator-overloading.md).

## Por quê

Manter a aritmética sobre um único tipo — sem promoção implícita — faz com que o custo e a precisão de cada operação fiquem visíveis no código. Uma expressão como `a + b` não pode alargar silenciosamente, perder precisão ou trocar de sinal pelas suas costas; se você quer um resultado mais largo, escreve o `cast` você mesmo. A distinção prefixo/pós-fixo é mantida por ser uma ferramenta precisa e bem compreendida para expressar "usa e então muda" versus "muda e então usa" em um único token. E como os mesmos operadores podem ser sobrecarregados para tipos de usuário em tempo de compilação, a superfície permanece uniforme, seja somando dois `int`s ou dois `Vetor2D`s.

## Relacionados

- [Tipos Primitivos](01-primitive-types.md)
- [Variáveis e Escopo](04-variables-and-scope.md)
- [Tipagem Estática](29-static-typing.md)
- [Sobrecarga de Operadores](27-operator-overloading.md)

[← Índice](README.md)
