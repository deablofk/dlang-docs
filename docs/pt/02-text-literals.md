# Literais de Texto

Texto em DLang é representado pelo tipo `String`. A linguagem oferece várias formas de literal para escrever strings diretamente no código-fonte — do texto entre aspas simples, passando por sequências de escape e Unicode, até blocos de múltiplas linhas e templates interpolados. Todas produzem valores `String` comuns; são conveniências de superfície, não tipos diferentes.

## Strings simples e escapes

O literal mais simples é texto entre aspas duplas. Dentro dele você pode usar sequências de escape com barra invertida, sendo a mais comum `\n` para uma nova linha:

```dlang
val a: String = "Simple text"
val b: String = "Simple text with line break\n"
```

## Escapes Unicode

Para embutir um caractere pelo seu code point Unicode, use o escape `\u` seguido do valor hexadecimal. Por exemplo, `A` é o code point da letra `A`:

```dlang
val c: String = "Simple text with unicode: A"
```

Essa é a forma portável de escrever caracteres que podem ser difíceis de digitar diretamente, mantendo o arquivo-fonte em ASCII puro se você quiser.

## Blocos com aspas triplas

Para texto que se estende por várias linhas, use um **bloco com aspas triplas** delimitado por `"""`. Tudo entre a abertura e o fechamento das aspas triplas é tomado literalmente, incluindo quebras de linha, então você não precisa salpicar a string com `\n`:

```dlang
val d: String = """Text Block with multiple lines"""
```

Blocos com aspas triplas são ideais para documentos embutidos, SQL, templates ou qualquer literal em que o layout faça parte do conteúdo.

## Interpolação

Um literal pode embutir o valor de uma expressão usando `${...}`. A expressão dentro das chaves é avaliada e seu resultado é inserido na string naquela posição:

```dlang
val e: String = "Formatted string: ${a}"
```

Aqui `${a}` é substituído pelo conteúdo da variável `a`. Qualquer expressão é permitida dentro das chaves, não apenas um nome solto. Essa sintaxe `${}` tem deliberadamente a mesma forma que reaparece em macros como o operador de splice `$` (veja [Macros](46-macros.md)) e na interpolação de padrões — uma única ideia visual reaproveitada por toda a linguagem.

## Por quê

Oferecer formas distintas de literal mantém cada caso comum ergonômico sem inventar novos tipos: um literal entre aspas, um escape Unicode, um bloco de aspas triplas e um template interpolado produzem todos a mesma `String`. A interpolação, em particular, remove o ruído da concatenação manual mantendo-se explícita sobre exatamente onde um valor é injetado. Reutilizar a forma `${}` para interpolação de string, e `$` para splice de AST em macros, faz com que um único modelo mental — "isto marca o buraco onde um valor entra" — cubra tanto texto em runtime quanto geração de código em tempo de compilação.

## Relacionados

- [Tipos Primitivos](01-primitive-types.md)
- [Variáveis e Escopo](04-variables-and-scope.md)
- [Macros](46-macros.md)

[← Índice](README.md)
