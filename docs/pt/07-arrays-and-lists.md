# Arrays e Listas Nativas

DLang distingue dois tipos de coleção sequencial, e a distinção é deliberada e visível. Um **array de tamanho fixo** é um tipo de nível de compilador cujo comprimento faz parte do seu tipo e é conhecido em tempo de compilação. Uma **lista dinâmica** é um tipo comum de biblioteca padrão, `List(T)`, que cresce em runtime e é dona do próprio buffer. Nenhum dos dois esconde de você uma alocação na heap.

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

Quando o número de elementos só é conhecido em runtime, você recorre a `List(T)`. Crucialmente, `List(T)` **não** é mágica do compilador — é uma struct genérica normal fornecida pela biblioteca padrão, implementada no piso Builtin do mesmo jeito que você escreveria seu próprio dono ([Memória Manual](13-manual-memory.md)). O que a torna dinâmica é que ela **possui** um buffer que cresce — e posse é toda a história de como você a passa adiante (abaixo).

```dlang
var lista: List(int) = List(int).empty()
lista.add(10)
```

`List(int).empty()` constrói uma lista vazia; `lista.add(10)` anexa, crescendo o buffer (dobrando) quando necessário. O buffer é liberado automaticamente no último uso da lista — o `deinit` dela roda exatamente uma vez, inserido pelo compilador ([Segurança de Memória](14a-memory-safety.md)).

## Listas são donas: moves e cópias

`List(T)` é um **dono `nocopy` (afim)**: tem exatamente um dono por vez, e atribuí-la ou retorná-la a **move** em vez de copiar. Usar o binding antigo depois de um move é erro de compilação — o verificador está protegendo você de dois donos liberando um buffer.

```dlang
var xs: List(int) = List(int).empty()
xs.add(1)
val ys: List(int) = xs        // MOVE — a posse transfere para ys
val n: int = xs.size()        // ERRO[E_USE_AFTER_MOVE]
val zs: List(int) = ys.copy() // cópia explícita elemento a elemento: agora dois donos
```

Passar uma lista para uma função segue as convenções de parâmetro ([Passagem de Parâmetros](10-parameter-passing.md)): um parâmetro simples a empresta só-leitura, `inout` deixa o chamado mutar com write-back, `sink` a consome.

## Tocando elementos in place: projeções `.at(i)`

`.get(i)` retorna uma *cópia* de um elemento e `xs[i] = v` substitui um — mas para mutar um elemento struct (ou seus donos aninhados) **in place**, projete-o com `.at(i)`:

```dlang
xs.at(i).hp = 99                    // auto-deref: escreve o campo dentro da lista
xs.at(i).inventario.add("poção")    // donos aninhados também mutam in place

inout e = xs.at(i)                  // segura a projeção por alguns statements
e.hp = e.hp - 10
e.escudo = 0
// enquanto e vive, xs fica travada (usá-la é E_EXCLUSIVITY):
// um crescimento poderia realocar o buffer e pender a projeção
```

Uma projeção não pode ser guardada, retornada nem vinculada com `val`/`var` (`E_REF_ESCAPES`); para ficar com um elemento, mova-o para fora com `xs.removeAt(i)`. A história completa de projeções — incluindo declarar acessores `yields` nos seus próprios tipos — está em [Segurança de Memória](14a-memory-safety.md).

Indexar uma `List(T)` com `[i]` funciona como num array, mas isso também não é sintaxe embutida: a lista implementa os métodos `operator_get` e `operator_set`, e o compilador resolve `lista[i]` para eles em tempo de compilação. Veja [Sobrecarga de Operadores](27-operator-overloading.md).

## Por quê

Separar arrays fixos de listas dinâmicas mantém o custo honesto. Um array `[N]T` é um layout primitivo, dimensionado em compile-time, sem sobrecarga, perfeito para dados cujo tamanho você conhece. Uma `List(T)` é um tipo de biblioteca que precisa alocar para crescer, e a linguagem mantém esse custo visível sem fazer você gerenciá-lo: a criação é explícita, o crescimento é amortizado, a liberação é automática no último uso. Posse move-only é o modelo de custo honesto para um tipo dono de buffer — uma cópia profunda silenciosa esconderia trabalho O(n), e uma cópia rasa silenciosa seria uma fábrica de liberação dupla. Manter `List` na biblioteca padrão em vez de no compilador prova a afirmação central da linguagem: coleções ricas são apenas structs genéricas mais alguns métodos de operador, não built-ins privilegiados.

## Relacionados

- [Loops e Iterações](06-loops.md)
- [Tabelas e Dicionários](08-maps-and-dictionaries.md)
- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Generics](32-generics.md)
- [Sobrecarga de Operadores](27-operator-overloading.md)

[← Índice](README.md)
