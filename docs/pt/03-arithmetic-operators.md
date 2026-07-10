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

## Atribuição composta

Para o padrão comum de "atualizar uma variável usando o próprio valor", DLang oferece os operadores de atribuição composta convencionais. `x += e` é exatamente um atalho para `x = x + e`, e o mesmo vale para cada operador aritmético e bit a bit:

```dlang
var total: int = 0
total += 10   // total = total + 10
total -= 3    // total = total - 3
total *= 2    // total = total * 2
total /= 4    // total = total / 4
total %= 5    // total = total % 5

var flags: int = 0
flags |= 4    // liga um bit
flags &= 6    // mascara bits
flags ^= 2    // alterna um bit
```

Eles funcionam sobre qualquer alvo atribuível — um `var` simples, um campo de struct, o `.value` de um ponteiro, um índice:

```dlang
contador.value.n += 1   // através de um ponteiro
placar[i] += pontos      // através de um índice
```

O conjunto completo é `+= -= *= /= %= &= |= ^=`. (As formas de deslocamento `<<=` / `>>=` ainda não estão disponíveis; use `x = x << n` para essas.) Assim como `++`/`--`, a atribuição composta exige um alvo mutável.

## Operadores bit a bit

Para trabalhar no nível dos bits, DLang oferece o conjunto convencional do C. Eles operam apenas sobre os tipos inteiros (`byte`, `short`, `int`, `long`) — nunca sobre `float`, `double` ou `boolean` — e, como na aritmética, ambos os operandos já precisam ser do mesmo tipo inteiro:

```dlang
val band: int = 0b1100 & 0b1010   // 0b1000 — e (and)
val bor:  int = 0b1100 | 0b1010   // 0b1110 — ou (or)
val bxor: int = 0b1100 ^ 0b1010   // 0b0110 — ou-exclusivo (xor)
val bnot: int = ~0                // -1     — não (not, unário)
val shl:  int = 1 << 4            // 16     — deslocamento à esquerda
val shr:  int = 256 >> 2          // 64     — deslocamento à direita
```

Como os inteiros de DLang são todos **com sinal**, `>>` é um deslocamento *aritmético* (que estende o sinal): `-8 >> 1` é `-4`, não um valor positivo grande. Não há operador separado de deslocamento lógico; se você precisa de semântica sem sinal, mascare o resultado explicitamente.

A precedência segue a escada familiar do C, da mais frouxa para a mais firme: `||` < `&&` < `|` < `^` < `&` < `== !=` < `< > <= >=` < `<< >>` < `+ -` < `* / %`. Como sempre, você pode usar parênteses para clareza — `(flags & mask) == mask` lê melhor do que confiar na tabela.

## Bases de literais inteiros

Literais inteiros podem ser escritos em decimal, hexadecimal (`0x`), binário (`0b`) ou octal (`0o`). Um `_` pode ser usado como separador de dígitos em qualquer base, para legibilidade; ele é ignorado pelo compilador:

```dlang
val mask:  int = 0xFF          // 255
val flags: int = 0b1010_1010   // 170
val perms: int = 0o755         // 493
val big:   long = 0x1_0000_0000 // precisa de `long` — estoura `int`
```

Um literal é tipado como `int` por padrão, mas um literal inteiro puro não tem largura *fixa* até o contexto lhe dar uma — então ele **se adapta** ao tipo com que é usado. Um literal que não cabe em 32 bits precisa ser anotado (ou sofrer `cast`) para `long`:

```dlang
val big: long = 0x1_0000_0000   // o literal adota `long` da anotação
```

### Adaptação de literal na aritmética

A mesma adaptação se aplica dentro de uma operação binária: um literal inteiro puro assume o tipo inteiro do *outro* operando. Isso faz com que os casos comuns simplesmente funcionem, sem um `cast` no literal:

```dlang
var n: long = 5
val m: long = n + 1       // o `1` vira `long`; sem cast

var b: byte = 12
val masked: byte = b & 0xF   // `0xF` vira `byte`
```

Apenas *literais* se adaptam. Dois *valores tipados* de larguras diferentes ainda exigem um `cast` explícito — `intVar + longVar` é erro, pois nenhum lado é um literal que o compilador possa retipar. Isso preserva a regra "sem coerção escondida" (veja [Tipagem Estática](29-static-typing.md)) ao mesmo tempo que remove o ruído de dar `cast` em constantes.

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
