# Prova de Teoremas em Tempo de Compilação

> Status: Ausente de propósito.

DLang **não** é um provador de teoremas. Não é Lean, Agda, Idris nem Coq, e não faz nenhuma tentativa de codificar provas matemáticas no seu sistema de tipos. Para uma linguagem de sistema não há retorno que motive isso: codificar provas pesaria tanto no compilador quanto na ergonomia do dia a dia, com pouco a mostrar em troca. O que DLang oferece *em vez disso* é verificação pragmática em tempo de compilação — checagens "fortes o suficiente" para pegar bugs reais sem o custo de um sistema de provas completo.

## O que existe no lugar

### Asserções de compilação

A diretiva `#assert` permite ao compilador checar uma condição durante a compilação e falhar o build com uma mensagem se ela não se sustentar. Este é o substituto prático de uma prova: não "prove que isto é sempre verdade para todas as entradas", mas "verifique este fato concreto sobre o programa tal como compilado".

```dlang
#assert(tamanhoDe(Pessoa) == 24, "o layout de Pessoa mudou de tamanho!")
#assert(VERSAO >= 3, "este módulo exige versão >= 3")
```

Essas rodam no compilador — há custo zero em runtime — e guardam exatamente o tipo de invariante estrutural que silenciosamente se quebra em C: o tamanho de uma struct mudando, uma suposição de versão envelhecendo. `#assert` faz parte do sistema unificado de metaprogramação; veja [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md).

### `match` exaustivo

Um `match` sobre um enum ou união etiquetada precisa cobrir toda variante ou fornecer um `else`. Adicionar uma variante nova transforma todo `match` não exaustivo num erro de compilação, então o compilador prova mecanicamente que você tratou todos os casos. Veja [Casamento de Padrões](37-pattern-matching.md).

### Checagens de dimensão dos tipos dependentes limitados

Como valores de compile-time parametrizam tipos (veja [Sistema de Tipos Dependentes](48-dependent-types.md)), uma dimensão `N` incompatível é um erro de compilação. O compilador está, num sentido estreito e útil, *provando* que os formatos dos seus vetores e matrizes se alinham — sem nenhuma maquinaria geral de provas.

### Imutabilidade verificada e ausência de conversões implícitas

`val` e `const` dão ao compilador uma garantia checada de que uma ligação nunca muda, e a ausência de conversão numérica implícita (veja [Tipagem Estática](29-static-typing.md)) significa que nenhum valor muda silenciosamente de largura ou sinal. São garantias pequenas e locais, mas são *verificadas*, não meramente convencionais.

## Por quê

O enquadramento honesto é que as garantias de compilação de DLang vêm de **asserções e checagens estruturais**, não de teoria de tipos dependentes nem de provas formais. Isso é um teto deliberado, não uma feature inacabada. Um sistema de provas completo forçaria a linguagem a raciocinar sobre proposições arbitrárias, arrastando maquinaria pesada e uma curva de aprendizado íngreme que quase nenhum programador de sistema quer pagar. A alternativa pragmática — `#assert`, `match` exaustivo, checagem de dimensões e imutabilidade verificada — captura os bugs que de fato ocorrem em código de sistema (layouts errados, casos não tratados, formatos incompatíveis, mutação acidental, coerção numérica silenciosa) enquanto mantém o compilador rápido e a linguagem ensinável. É verificação "forte o suficiente" escolhida de propósito em vez de provas "maximamente poderosas".

## Relacionados

- [Sistema de Tipos Dependentes](48-dependent-types.md)
- [Casamento de Padrões](37-pattern-matching.md)
- [Tipagem Estática](29-static-typing.md)
- [Enumerações](16-enumerations.md)
- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)

[← Índice](README.md)
