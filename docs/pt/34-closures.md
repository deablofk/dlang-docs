# Closures e Funções Anônimas

Uma função anônima é um literal de função sem nome: exatamente a mesma sintaxe de uma função nomeada, menos a parte `nome ::`. Uma *closure* é um literal desses que captura variáveis do escopo ao redor. A promessa central de DLang aqui é que o custo de uma closure é sempre visível: uma closure que não sobrevive ao seu escopo é gratuita, e uma que sobrevive aloca seu ambiente capturado a partir do alocador atual.

## Três formas de literal

A forma completa espelha uma função nomeada — uma lista de parâmetros, um tipo de retorno e um corpo. Há tanto a forma de bloco quanto a forma de expressão:

```dlang
// 1. literal anônimo completo — mesma forma de uma função, só que sem nome
val dobro = (x: int) -> int { return x * 2 }
val dobro = (x: int) -> int = x * 2   // forma expressão, igual à de função nomeada
```

Para o caso comum de um argumento há uma forma curta que usa o placeholder universal `_` como argumento implícito:

```dlang
// 2. forma curta com o placeholder
lista.map({ _ * 2 })     // '_' é o argumento implícito
lista.filtrar({ _ > 0 })
```

O placeholder `_` é o mesmo usado no [laço `for`](06-loops.md) e no [casamento de padrões](37-pattern-matching.md): a "coisa sem nome" universal da linguagem. A [escada completa de formas de lambda](39-lambda-expressions.md) está documentada em expressões lambda.

## Capturar o escopo ao redor

Uma closure lê variáveis que vivem fora do seu próprio corpo. A captura é implícita no código, mas explícita no custo, como mostra a próxima seção:

```dlang
// 3. closure: captura variáveis do escopo ao redor
calcularDescontos :: () {
  val taxa = 0.1   // variável local
  val aplicar = (preco: float) -> float {
    return preco - (preco * taxa)   // 'taxa' é capturada
  }

  println(aplicar(100.0))
}
```

## Captura e memória: o caso não-escapante

O caso comum é uma closure que não escapa: é criada, usada e descartada dentro do mesmo escopo. Isso não custa nada: o ambiente vive na pilha, e os valores capturados são snapshots dos bindings em escopo.

```dlang
// closure não-escapante — usada e descartada dentro do escopo.
// custo zero: seu ambiente vive na pilha.
lista.map({ _ * taxa })
```

## Captura e memória: o caso escapante

Uma closure *escapa* quando é retornada ou guardada em algum lugar que sobrevive à função que a criou. Isso é uma coisa comum e suportada — a closure é um valor simples de tipo função, seu ambiente capturado vai para a heap, e o compilador gerencia esse armazenamento como qualquer outro valor com dono ([Segurança de Memória](14a-memory-safety.md)). Não há chamada de alocador, não há ponteiro e não há sintaxe especial de invocação:

```dlang
// closure escapante: retornada além do escopo, chamada diretamente
multiplicador :: (fator: int) -> (int) -> int {
  return (x: int) -> int = x * fator     // captura 'fator' e sobrevive ao frame
}

val triplicar = multiplicador(3)
val t = triplicar(10)                    // 30
```

Consistente com Mutable Value Semantics, uma captura é uma **cópia por valor** — a closure tira um snapshot dos bindings que usa, e chamá-la nunca muta o ambiente externo (nem um compartilhado). Estado que precisa evoluir entre chamadas pertence a um valor que se vê: um struct `nocopy` com um método, não uma célula de closure escondida.

## Por quê

Um literal de função é uma função nomeada sem o nome — uma regra, zero sintaxe nova. A forma curta `{ _ * 2 }` reaproveita o mesmo placeholder do laço `for`, então uma lambda de um argumento fica enxuta; dois ou mais argumentos, ou tipos explícitos, voltam à forma completa.

O coração do design é a distinção de escape. Uma closure não-escapante é gratuita — seu ambiente vive na pilha. Uma escapante aloca na heap seu snapshot capturado, e o compilador possui esse armazenamento do mesmo jeito que possui o buffer de uma `string`. Captura por valor é a face em formato de closure do Mutable Value Semantics: não há ambiente com alias para pender ou disputar, então closures não precisam de nada da maquinaria de lifetime de que precisam em linguagens de semântica de referência.

## Relacionados

- [Ponteiros de Função](33-function-pointers.md)
- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Expressões Lambda](39-lambda-expressions.md)
- [Gerenciamento de memória manual](13-manual-memory.md)
- [Coleta de lixo](14-garbage-collection.md)

[← Índice](README.md)
