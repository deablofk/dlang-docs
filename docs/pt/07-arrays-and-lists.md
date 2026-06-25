# Arrays e Listas Nativas

DLang distingue dois tipos de coleção sequencial, e a distinção é deliberada e visível. Um **array de tamanho fixo** é um tipo de nível de compilador cujo comprimento faz parte do seu tipo e é conhecido em tempo de compilação. Uma **lista dinâmica** é um tipo comum de biblioteca padrão, `List(T)`, que cresce em runtime usando um alocador explícito. Nenhum dos dois esconde de você uma alocação na heap.

## Arrays de tamanho fixo

Um array fixo tem o tipo `[N]T`, onde `N` é o comprimento de tempo de compilação e `T` é o tipo do elemento. Seu armazenamento é exatamente `N` elementos dispostos de forma contígua — sem cabeçalho, sem campo de capacidade, sem indireção. Você o indexa com `[i]`:

```dlang
var nomes: [2]string = ["0", 2]   // tamanho 2, preenchido com zero e então atribuído
nomes[0] = "a"
nomes[1] = "b"
```

Como o comprimento faz parte do tipo, o compilador conhece o tamanho exato do array em cada uso, o que faz dele um bloco de construção de custo zero. Arrays fixos são também o que faz funcionar os generics dimensionados em tempo de compilação da linguagem: um `Buffer(T, N)` cujo campo é `[N]T` resolve seu armazenamento inteiramente na compilação (veja [Generics](32-generics.md)).

Você pode deixar o compilador inferir o comprimento a partir do literal. Um literal de array escrito sem uma contagem explícita assume o comprimento do literal — `[]string` com dois elementos é o mesmo que `[2]string` (você também pode ver isso escrito `[_]string`, usando o placeholder para "inferir a contagem"):

```dlang
val nomes: []string = ["gabriel", "bruno"]   // implicitamente [2]string
```

## Listas dinâmicas

Quando o número de elementos só é conhecido em runtime, você recorre a `List(T)`. Crucialmente, `List(T)` **não** é mágica do compilador — é uma struct genérica normal fornecida pela biblioteca padrão, o mesmo tipo de tipo que você poderia escrever. O que a torna dinâmica é que ela possui um buffer que cresce, e crescer esse buffer significa alocar memória. DLang nunca aloca implicitamente, então você entrega um alocador à lista ao criá-la:

```dlang
var lista: List(int) = List(int).init(_alloc)   // _alloc = alocador padrão
lista.add(10)
```

`List(int).init(_alloc)` constrói uma lista vazia respaldada pelo alocador padrão `_alloc`. Você poderia passar qualquer alocador aqui — esse é justamente o ponto de tornar o alocador explícito. `lista.add(10)` anexa um elemento, crescendo o buffer de respaldo se necessário. Como a lista possui memória na heap, você é responsável por liberá-la (tipicamente com `defer lista.deinit()`); os detalhes de alocação e limpeza são cobertos em [Alocação Dinâmica](18-dynamic-allocation.md) e [Gerenciamento de Memória Manual](13-manual-memory.md).

Indexar uma `List(T)` com `[i]` funciona como num array, mas isso também não é sintaxe embutida: a lista implementa os métodos `operator_get` e `operator_set`, e o compilador resolve `lista[i]` para eles em tempo de compilação. Veja [Sobrecarga de Operadores](27-operator-overloading.md).

## Por quê

Separar arrays fixos de listas dinâmicas mantém o custo honesto. Um array `[N]T` é um layout primitivo, dimensionado em compile-time, sem sobrecarga, perfeito para dados cujo tamanho você conhece. Uma `List(T)` é um tipo de biblioteca que precisa alocar para crescer, e, ao forçar você a passar um alocador, a linguagem torna esse custo impossível de não perceber — não há alocação escondida por trás de um anexar de aparência inocente. Manter `List` na biblioteca padrão em vez de no compilador prova a afirmação central da linguagem: coleções ricas são apenas structs genéricas sobre um alocador e alguns métodos de operador, não built-ins privilegiados.

## Relacionados

- [Loops e Iterações](06-loops.md)
- [Tabelas e Dicionários](08-maps-and-dictionaries.md)
- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Sobrecarga de Operadores](27-operator-overloading.md)

[← Índice](README.md)
