# Closures e Funções Anônimas

Uma função anônima é um literal de função sem nome: exatamente a mesma sintaxe de uma função nomeada, menos a parte `nome ::`. Uma *closure* é um literal desses que captura variáveis do escopo ao redor. A promessa central de DLang aqui é que o custo de uma closure é sempre visível: uma closure que não sobrevive ao seu escopo é gratuita, e uma que sobrevive exige um alocador explícito.

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

O caso comum é uma closure que não escapa: é criada, usada e descartada dentro do mesmo escopo. Isso não custa nada. Ela vive na pilha e captura suas variáveis *por referência*; nenhum alocador é envolvido.

```dlang
// closure não-escapante — usada e descartada dentro do escopo.
// custo zero: vive na pilha, captura por referência, sem alocador.
lista.map({ _ * taxa })
```

## Captura e memória: o caso escapante

Uma closure *escapa* quando é retornada ou guardada em algum lugar que sobrevive à função que a criou. Nesse ponto seu estado capturado não pode mais viver na pilha, então — exatamente como qualquer outro dado que precisa sobreviver a uma função — ela precisa de um alocador explícito. Você pede a alocação com `_alloc.closure({ ... })`, que devolve um `Ptr` para a closure, e a chama através de `.value`:

```dlang
// closure escapante: retornada/guardada além do escopo.
// precisa de um alocador explícito, como qualquer dado que sobrevive à função.
fazContador :: () -> Ptr((() -> int)) {
  var n = 0
  // captura 'n' e sobrevive à função -> alocação explícita e clara
  return _alloc.closure({ n = n + 1; return n })
}
```

O valor retornado é um `Ptr((...) -> ...)`, então é invocado através de `.value`, igual a qualquer ponteiro alocado na heap.

## Por quê

Um literal de função é uma função nomeada sem o nome — uma regra, zero sintaxe nova. A forma curta `{ _ * 2 }` reaproveita o mesmo placeholder do laço `for`, então uma lambda de um argumento fica enxuta; dois ou mais argumentos, ou tipos explícitos, voltam à forma completa.

O coração do design é a distinção de escape. Uma closure não-escapante é gratuita (pilha); uma escapante leva um alocador explícito. A linguagem nunca aloca heap *escondido* atrás de uma closure — o pecado de muitas linguagens com coletor de lixo. Você vê o `_alloc` e sabe o custo. Se preferir entregar o ciclo de vida ao coletor de lixo, `_gcAlloc` também funciona aqui.

## Relacionados

- [Ponteiros de Função](33-function-pointers.md)
- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Expressões Lambda](39-lambda-expressions.md)
- [Gerenciamento de memória manual](13-manual-memory.md)
- [Coleta de lixo](14-garbage-collection.md)

[← Índice](README.md)
