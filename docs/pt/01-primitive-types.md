# Tipos Primitivos

DLang oferece um conjunto pequeno e fixo de tipos primitivos escalares. Eles mapeiam diretamente para representações de máquina, então não há caixas escondidas, nem metadados implícitos, nem alocação envolvida ao declarar um deles. Um valor primitivo vive exatamente onde você o coloca — na pilha, dentro de uma struct ou em uma posição de array — que é justamente o que se espera de uma linguagem de sistema orientada a dados.

## Os escalares embutidos

Todo primitivo é declarado com uma anotação de tipo explícita. O compilador infere tipos em muitos lugares (veja [Inferência de Tipos](31-type-inference.md)), mas os próprios primitivos são os blocos irredutíveis do sistema de tipos.

```dlang
val a: byte
val b: short
val c: int
val d: long
val f: float
val g: double
val h: boolean
val i: char
```

Os tipos inteiros formam uma escada de tamanhos: `byte`, `short`, `int` e `long` são inteiros com sinal progressivamente mais largos. `float` e `double` são os tipos de ponto flutuante IEEE-754 de precisão simples e dupla. `boolean` guarda `true` ou `false`, e `char` representa um único caractere.

## Padrões e largura

Quando você escreve um literal inteiro nu com inferência, o compilador escolhe `int`; um literal decimal nu é inferido como `double`. Se você precisa de outra largura, anota explicitamente:

```dlang
val idade = 25         // inferido int
val pi = 3.14          // inferido double
val contador: long = 0 // força long em vez de int
```

Literais inteiros também podem ser escritos em hexadecimal (`0xFF`), binário (`0b1010`) ou octal (`0o17`), com um separador de dígitos `_` opcional para legibilidade (`0xDEAD_BEEF`). A base só afeta como você escreve o valor, não o seu tipo — veja [Operadores Aritméticos](03-arithmetic-operators.md) para os operadores bit a bit com que esses literais combinam.

Isso importa porque DLang **não faz conversão numérica implícita**. Um `byte` não se alarga silenciosamente para `int`, e um `int` não vira `long` sozinho. Todo movimento numérico entre tipos é escrito com `cast(T, x)`. Essa regra é detalhada em [Tipagem Estática](29-static-typing.md), mas começa aqui: a largura que você declara é a largura que você obtém.

## Por quê

Uma linguagem de sistema se justifica sendo previsível quanto a memória e custo. Manter o conjunto de primitivos pequeno e mapeado à máquina faz com que o layout de qualquer agregado construído a partir desses tipos seja óbvio à inspeção — não há surpresa de padding escondida atrás de um tipo "número" abstrato. Recusar conversões implícitas elimina uma classe inteira de bugs silenciosos de precisão e sinal que assolam o C, e empurra todo movimento com perda ou alargamento para um `cast` visível. O resultado é que ler uma anotação de tipo já lhe diz o tamanho e a representação exatos do dado, sem nenhuma cerimônia em tempo de execução.

## Relacionados

- [Literais de Texto](02-text-literals.md)
- [Operadores Aritméticos](03-arithmetic-operators.md)
- [Variáveis e Escopo](04-variables-and-scope.md)
- [Tipagem Estática](29-static-typing.md)
- [Inferência de Tipos](31-type-inference.md)

[← Índice](README.md)
