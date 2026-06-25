# Tipagem Dinâmica

DLang é uma linguagem estaticamente tipada, e quase tudo que você buscaria numa linguagem dinâmica é expressável com tipos estáticos, generics e interfaces. A tipagem dinâmica existe apenas como um **opt-in explícito** e estreito: o tipo `any`. Você pede por ele pelo nome; ele nunca acontece por padrão.

## O tipo `any`

`any` é um *fat pointer* (ponteiro gordo) — ele guarda um valor junto com uma tag em tempo de execução que identifica o tipo concreto desse valor. Esse é exatamente o mesmo mecanismo que DLang usa para interfaces (um ponteiro para o dado mais um ponteiro de tipo/método), então `any` reaproveita uma maquinaria que já existe em vez de adicionar um runtime dinâmico separado.

```dlang
// 'any' guarda qualquer valor + sua tag de tipo em runtime
val caixa: any = 42
```

Aqui `caixa` carrega tanto o inteiro `42` quanto uma tag que diz "isto é um `int`". O tipo estático de `caixa` é apenas `any`; o tipo concreto vive em tempo de execução.

## Recuperando o tipo concreto com `match`

Você não pode usar o valor dentro de um `any` diretamente — não há como lê-lo como um `int` até ter *provado* que ele é um. A recuperação é feita com `match`, ligando o valor a um nome no braço cujo tipo casa com a tag.

```dlang
match (caixa) {
  n: int    -> println("inteiro: ${n}")
  s: string -> println("texto: ${s}")
  else      -> println("tipo desconhecido ${caixa}")
}
```

Cada braço nomeia um tipo (`n: int`, `s: string`); o braço que casa liga o valor desempacotado com seu tipo estático apropriado, então dentro daquele braço `n` é realmente um `int`. É o mesmo construto `match` usado para [Casamento de Padrões](37-pattern-matching.md) e despacho de enum — a recuperação dinâmica não é uma feature nova, apenas `match` aplicado à tag de runtime. O braço `else` é o caso padrão para qualquer tipo não listado.

## Use com parcimônia

A intenção de design é explícita na filosofia da linguagem: `any` deve ser raro. Se um problema pode ser modelado com generics, uma interface ou uma união etiquetada (um enum carregando dados), essas ferramentas estáticas têm custo zero e são checadas em compilação, enquanto `any` empurra uma checagem de tipo para o runtime e paga pela tag. `any` só conquista seu lugar onde a heterogeneidade é genuinamente dinâmica — por exemplo, um valor vindo da reflexão ou um contêiner genérico que precisa guardar tipos verdadeiramente sem relação. O `any` de DLang é próximo em espírito ao `any` de Odin: uma válvula de escape pragmática, não um estilo de programação.

## Por quê

Uma linguagem de sistema orientada a dados quer o custo de cada operação visível no código, então a tipagem dinâmica não pode ser o padrão — espalharia tags de runtime e checagens de tipo escondidas por todo um código que seria estático. Ao tornar `any` um tipo explícito que reaproveita o mecanismo de fat pointer das interfaces, DLang mantém o caso dinâmico honesto: você enxerga exatamente onde um valor se tornou dinâmico (a anotação `any`) e exatamente onde ele volta a ser concreto (o `match`). Nada é empacotado ou etiquetado a menos que você tenha escrito `any`, e o único caminho de volta a um valor utilizável é um `match` que o compilador consegue manter exaustivo. O resultado é que a linguagem suporta dinamismo onde ele é realmente necessário sem deixá-lo vazar para os 99% de código que ficam melhor totalmente estáticos.

## Relacionados

- [Tipagem Estática](29-static-typing.md)
- [Inferência de Tipos](31-type-inference.md)
- [Casamento de Padrões](37-pattern-matching.md)
- [Interfaces](25-interfaces.md)
- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)

[← Índice](README.md)
