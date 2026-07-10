# Tabelas e Dicionários

Um mapa associa chaves a valores. DLang oferece duas ferramentas complementares: um **literal de mapa fixo** embutido diretamente na linguagem e um **`Map(K, V)` dinâmico** que vive na biblioteca padrão. Essa divisão espelha a filosofia usada para arrays e listas — o compilador conhece a forma pequena, de tamanho estático, enquanto o crescimento ao longo do tempo é um tipo de biblioteca que tira do alocador atual (ambiente).

## Mapas fixos

Um mapa fixo é escrito `{N}[K: V]`, onde `N` é a quantidade de elementos, `K` o tipo da chave e `V` o tipo do valor. A forma rima de propósito com tuplas e funções de múltiplo retorno: as chaves envolvem o conteúdo, e a parte `[K: V]` se lê como "indexado por `K`, produzindo `V`".

```dlang
var keyValueMap: {2}[string: int] = {
  "maça": 50,
  "banana": 30
}
```

Como o tamanho faz parte do tipo, o mapa é disposto inline, sem nenhuma alocação na heap — ele se comporta como uma pequena tabela de valor que vive onde quer que você a declare (pilha, campo de struct, global). Isso o torna ideal para tabelas de consulta conhecidas em tempo de compilação.

### Leitura e escrita

O acesso usa colchetes, igual a um array, mas indexado pelo tipo da chave em vez de um inteiro:

```dlang
keyValueMap["maça"] = 20
val preco: int = keyValueMap["banana"]
```

Como a capacidade é fixa, você não pode adicionar chaves totalmente novas além de `N` — a forma com colchetes atualiza entradas existentes. A busca é uma varredura linear que compara chaves com `==` (então chaves `string`, chaves de enum e chaves inteiras funcionam); se a chave não existe, a leitura devolve um valor zero. Quando precisar crescer, recorra ao `Map` dinâmico.

### Iteração

Iterar um mapa fixo produz cada entrada como um par `(chave, valor)`. O laço `for` desestrutura esse par diretamente em dois nomes:

```dlang
for (chave, valor : keyValueMap) {
  println("Item: ${chave} | valor: ${valor}")
}
```

Essa é a mesma maquinaria de desestruturação usada em todo o restante da linguagem — o laço está simplesmente iterando tuplas, onde cada elemento é a visão empacotada `(chave, valor)` de uma entrada. Veja [Tuplas e desestruturação](38-tuples-and-destructuring.md).

## Mapas dinâmicos

Quando o conjunto de chaves não é conhecido de antemão, use `Map(K, V)`. Ele é uma struct genérica normal da biblioteca padrão — **não** um recurso embutido no compilador — construída a partir dos mesmos generics e sobrecarga de operadores que todo outro contêiner usa.

```dlang
var mapa: Map(string, int) = Map(string, int).empty()

mapa.set("banana", 30)              // insere ou sobrescreve
val preco: int = mapa.get("banana") // lê de volta
```

`.set(k, v)` insere uma nova chave ou sobrescreve uma existente, fazendo o armazenamento interno crescer quando a chave está ausente; `.get(k)` lê de volta (a busca é uma varredura linear por `==`). Outros métodos incluem `.contains(k)`, `.remove(k)`, `.size()`, `.keyAt(i)` / `.valueAt(i)`, além de `operator_get` / `operator_set`, então `mapa["k"]` e `mapa["k"] = v` também funcionam.

A memória em que um `Map` cresce vem do **alocador atual** — o contexto de memória ambiente e trocável de DLang (veja [Alocação dinâmica](18-dynamic-allocation.md)), não um alocador que você passa à mão.

## Por quê

Dividir mapas em um literal fixo mais um tipo de biblioteca mantém a linguagem pequena. A forma fixa é genuinamente de custo zero: seu tamanho está no tipo, então o compilador a dispõe inline (na pilha, em um campo de struct ou em um global) sem alocação na heap. A forma dinâmica tira seu armazenamento do alocador atual, então seu modelo de memória é o mesmo contexto trocável que todo outro contêiner usa — e como `Map(K, V)` é uma struct genérica comum, não exige mágica especial do compilador: é construída a partir dos mesmos generics e sobrecarga de operadores (`operator_get` / `operator_set`) que todo o resto.

## Relacionados

- [Arrays e listas](07-arrays-and-lists.md)
- [Tuplas e desestruturação](38-tuples-and-destructuring.md)
- [Alocação dinâmica](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Laços](06-loops.md)

[← Índice](README.md)
