# Enumerações

Uma enumeração é um tipo nomeado cujos valores são extraídos de um conjunto fixo e finito de constantes nomeadas. Em DLang um enum é ligado com `::`, como qualquer outro tipo, e em sua forma mais simples é apenas um conjunto de nomes apoiados em inteiros.

## Enums inteiros simples

Declarar um enum com `enum { ... }` dá a cada variante um valor inteiro automático, começando em `0` e contando para cima na ordem de declaração:

```dlang
Erro :: enum {
  ArquivoNaoEncontrado, // 0
  PermissaoNegada       // 1
}
```

`ArquivoNaoEncontrado` é `0`, `PermissaoNegada` é `1`. Você raramente precisa pensar nos números subjacentes — o objetivo do enum é dar nomes significativos a um conjunto fechado de casos, para que o código se leia em termos de intenção em vez de inteiros mágicos.

## Valores customizados com `enum(int)`

Quando os valores numéricos importam — por exemplo códigos de status HTTP que precisam casar com um protocolo de rede — anote o tipo de apoio como `enum(int)` e atribua cada variante explicitamente:

```dlang
StatusHttp :: enum(int) {
  Ok = 200,
  NotFound = 404,
  InternalError = 500
}
```

Aqui os nomes carregam seus números do mundo real. O tipo entre parênteses `(int)` ecoa a mesma notação de chamada usada em toda a linguagem (`Ptr(T)`, `List(T)`), e torna a representação de apoio explícita em vez de presumida.

## Usando um enum

Você se refere a uma variante através de seu tipo de enum, o que mantém o namespace limpo e torna óbvia a origem de cada constante:

```dlang
val codigo: StatusHttp = StatusHttp.NotFound
```

Enums combinam naturalmente com `match`, que pode ramificar por cada variante pelo nome. Como o compilador conhece o conjunto completo de casos, um `match` sobre um enum pode ser verificado quanto à exaustividade:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("arquivo sumiu")
  Erro.PermissaoNegada      -> println("acesso negado")
  else                      -> println("ok")
}
```

## Enums que carregam dados

Os enums mostrados aqui são apenas *tags* — cada variante é só um nome (opcionalmente com um inteiro fixo). DLang também suporta **enums de união etiquetada (tagged union)**, onde uma variante carrega seu próprio payload de campos, por exemplo `Circulo(raio: float)`. Esses são uma construção mais rica: a única maneira segura de ler o payload de uma variante é através de `match`, que o desestrutura. Como esse comportamento é inseparável do casamento de padrões, ele é documentado lá e não aqui — veja [Casamento de padrões](37-pattern-matching.md) para enums-com-dados.

## Por quê

Enums simples nada mais são do que inteiros nomeados, então custam exatamente o que um inteiro custa — sem boxing, sem informação de tipo em runtime, sem alocação. Tornar o tipo de apoio explícito com `enum(int)` mantém você honesto sobre a representação quando ela importa (protocolos, formatos de arquivo), enquanto deixa a forma autonumerada concisa quando não importa. Rotear variantes que carregam dados por `match` é o que garante a segurança: não há como ler `Circulo.raio` de um valor que na verdade é um `Retangulo`, porque o payload só é alcançável depois que a tag foi verificada. Esta é a substituição orientada a dados para hierarquias de classe — uma tag compacta mais payload, com o compilador impondo que você trate cada caso.

## Relacionados

- [Casamento de padrões](37-pattern-matching.md)
- [Estruturas condicionais](05-conditionals.md)
- [Tratamento de erros](15-error-handling.md)
- [Estruturas de dados](17-structs.md)
- [Tipagem estática](29-static-typing.md)

[← Índice](README.md)
