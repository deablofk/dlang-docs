# Ponteiros de Função

Em DLang uma função é um valor de primeira classe. Como funções são declaradas com `::` (um nome ligado a um literal de função), a própria função é apenas um dado que por acaso é chamável, e pode ser guardada em uma variável, passada como argumento ou disposta em um array — sem nenhuma sintaxe nova.

## O tipo de uma função

Um tipo de função é escrito como a lista de tipos de entrada entre parênteses, seguida de `->` e o tipo de saída:

```dlang
// o tipo de uma função é (tipos-de-entrada) -> tipo-de-saída
val op: (int, int) -> int = somar   // 'somar' definido com :: encaixa aqui
```

Qualquer função nomeada cuja assinatura case com o tipo pode ser atribuída a essa variável. Não há invólucro, nem boxing, nem decoração — o nome da função *é* o valor.

## Chamada através de um valor de função

Diferente de um ponteiro de dados (`Ptr(T)`), que é desreferenciado por meio de `.value`, um valor de função é chamado diretamente. Os próprios parênteses são o operador de chamada:

```dlang
// chama-se direto, sem .value (diferente de um ponteiro de dados)
val r = op(2, 3)   // 6
```

Essa é a assimetria deliberada entre `Ptr(T)` e um tipo de função: um ponteiro de dados aponta *para* algo que você precisa ler, enquanto um valor de função já *é* aquilo que você invoca.

## Passar funções como parâmetros

Como um tipo de função é um tipo comum, ele pode aparecer em uma lista de parâmetros. Essa é a base sobre a qual tudo o que vem depois nesta parte da linguagem se constrói — [closures](34-closures.md), [funções de ordem superior](35-higher-order-functions.md) e [expressões lambda](39-lambda-expressions.md).

```dlang
// passar uma função como parâmetro
aplicar :: (f: (int, int) -> int, a, b: int) -> int = f(a, b)

aplicar(somar, 10, 5)   // 15
```

## Tabelas de despacho

Como um valor de função é dado puro, você pode guardar muitos deles em um array de tamanho fixo e indexá-lo. Isso dá uma *tabela de despacho*: um substituto orientado a dados para uma cadeia de condicionais ou uma tabela virtual.

```dlang
// tabela de despacho: um array de ponteiros de função
val operacoes: [2]((int, int) -> int) = [somar, subtrair]
val res = operacoes[0](4, 2)
```

O array guarda as funções de forma contígua; selecionar uma é um índice, e chamá-la é um salto direto. Não há indireção escondida além do índice que você mesmo escreveu.

## Por quê

Ponteiros de função decorrem de uma regra já presente na linguagem: uma função é um nome ligado a um literal de função. Tornar esse literal um valor não custa nada e destrava toda a camada funcional. Chamar sem `.value` mantém o ponto de chamada limpo, ao mesmo tempo que preserva a regra clara e explícita de desreferência para ponteiros de dados.

## Relacionados

- [Closures e Funções Anônimas](34-closures.md)
- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Expressões Lambda](39-lambda-expressions.md)
- [Ponteiros e referências](12-pointers-and-references.md)

[← Índice](README.md)
