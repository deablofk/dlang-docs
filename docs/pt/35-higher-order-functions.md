# Funções de Ordem Superior

Uma função de ordem superior é aquela que recebe uma função como argumento ou devolve uma. Em DLang elas não são mágica de compilador — são métodos [genéricos](32-generics.md) comuns em `List(T)`, escritos com os mesmos [tipos de ponteiro de função](33-function-pointers.md) e [lambdas](39-lambda-expressions.md) que você já tem. Os três cavalos de batalha são `map`, `filtrar` e `reduce`.

## map, filtrar, reduce

`map` transforma cada elemento e produz uma nova `List`. Ela não recebe um parâmetro de alocador: a nova lista cresce a partir do alocador atual, o mesmo contexto ambiente que toda alocação usa (veja [Alocação Dinâmica](18-dynamic-allocation.md)).

```dlang
// map: definida com generics; a nova lista cresce do alocador atual
List(T).map(R) :: (transform: (T) -> R) -> List(R) {
  var saida = List(R).empty()   // cresce do alocador atual (contexto ambiente)
  for (item : _) {
    saida.add(transform(item))
  }
  return saida
}
```

`filtrar` mantém apenas os elementos que satisfazem um predicado e devolve um subconjunto — novamente em uma `List` recém-alocada:

```dlang
// filtrar: mesma forma de entrada, devolve um subconjunto
List(T).filtrar :: (pred: (T) -> boolean) -> List(T) {
  var saida = List(T).empty()
  for (item : _) {
    if (pred(item)) saida.add(item)
  }
  return saida
}
```

`reduce` (também chamado *fold*) colapsa a lista inteira em um único valor. O ponto crucial é que ele **não aloca nada** — apenas conduz um acumulador através do laço:

```dlang
// reduce/fold: agrega tudo num só valor — não aloca nada
List(T).reduce(R) :: (inicial: R, op: (R, T) -> R) -> R {
  var acc = inicial
  for (item : _) acc = op(acc, item)
  return acc
}
```

Então `map` e `filtrar` são *eager* (ansiosos) — rodam o laço agora e materializam uma nova `List` — enquanto `reduce` produz um escalar e não aloca nada.

## A escada de formas de lambda

Chamar essas funções mostra as três formas de lambda como uma escada de verbosidade, da mais curta à mais explícita:

```dlang
var nums = List(int).empty()
// ... nums populada

// 1 argumento -> placeholder '_'
val dobrados = nums.map({ _ * 2 })
val positivos = nums.filtrar({ _ > 0 })

// n argumentos -> nomeados, tipos inferidos do contexto, separados por '->'
val soma = nums.reduce(0, { acc, x -> acc + x })

// forma completa quando quiser tipos explícitos
val soma2 = nums.reduce(0, (acc: int, x: int) -> int { return acc + x })
```

## Pipelines

Como cada um de `map` e `filtrar` devolve uma `List`, as chamadas se encadeiam em um pipeline que se lê de cima para baixo:

```dlang
// pipeline, leitura de cima para baixo
val resultado = nums
  .filtrar({ _ > 0 })
  .map({ _ * 2 })
  .reduce(0, { acc, x -> acc + x })
```

## Retornar uma função

Uma função de ordem superior também pode *retornar* uma função. Como a função retornada captura estado local e sobrevive ao seu escopo, isso é uma closure escapante e portanto aloca na heap seu ambiente capturado a partir do alocador atual — fiel à regra de [closures](34-closures.md):

```dlang
// HOF que retorna uma função: uma closure escapante -> env na heap do alocador atual
// devolve uma função que lembra do 'fator'
multiplicador :: (fator: int) -> Ptr((int) -> int) {
  return _alloc.closure({ _ * fator })   // captura 'fator' e sobrevive -> aloca
}

val triplicar = multiplicador(3)
triplicar.value(10)   // 30 (chamada via .value, pois é ponteiro de closure alocada)
```

## Por quê

Essas funções permanecem na biblioteca padrão como métodos genéricos comuns, o que significa que o núcleo da linguagem não precisa saber nada de especial sobre elas. Ao tirar do alocador atual, dispensam um parâmetro de alocador, e ao fazer `reduce` não alocar nada, mantêm a agregação barata.

Há um custo que vale registrar: um pipeline como `filtrar().map()` cria uma **List intermediária em cada estágio** — cada estágio aloca. É exatamente o problema que o desenho parqueado de iteradores lazy resolveria depois, fundindo os estágios num único laço. Veja [Avaliação Preguiçosa](36-lazy-evaluation.md) para essa otimização futura e parqueada.

## Relacionados

- [Ponteiros de Função](33-function-pointers.md)
- [Closures e Funções Anônimas](34-closures.md)
- [Avaliação Preguiçosa](36-lazy-evaluation.md)
- [Expressões Lambda](39-lambda-expressions.md)
- [Generics](32-generics.md)

[← Índice](README.md)
