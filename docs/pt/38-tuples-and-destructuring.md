# Tuplas e Desestruturação

Uma tupla é um **agregado anônimo e posicional**. É um tipo de valor: vive na pilha, custa zero e não precisa de alocador. Pense nela como a "struct descartável" para quando você não quer nomear um tipo. Em DLang a tupla unifica três coisas que costumam ser recursos separados — [retorno múltiplo](11-multiple-returns.md), desestruturação e [casamento de padrões](37-pattern-matching.md) — em um único conceito.

## 1. Tipo e literal

Um tipo de tupla e um valor de tupla são ambos escritos como uma lista entre parênteses, separada por vírgulas:

```dlang
val ponto: (int, int) = (10, 20)
val registro: (string, int, boolean) = ("Gabriel", 25, true)
```

## 2. Acesso — somente desestruturação (não há `.0` nem `[0]`)

O único jeito de ler o conteúdo de uma tupla é desestruturá-la. Não há acesso posicional a campo:

```dlang
val (x, y) = ponto          // único jeito de extrair os valores
val (_, y) = ponto          // '_' ignora um campo (o mesmo '_' do match)
val (x, _) = ponto
val (nome, idade, _) = registro
```

Uma tupla pode ser trocada sem variável temporária, e tuplas aninham:

```dlang
// troca sem variável temporária
(a, b) = (b, a)

// aninhada
val (nome, (px, py)) = ("base", (1, 2))
```

### Por que só desestruturação

Uma tupla é *heterogênea* — cada posição tem seu próprio tipo. Um índice posicional sobre ela teria, portanto, de ser um literal de compile-time para que o compilador soubesse o tipo resultante, o que é diferente de um array *homogêneo* `[i]`, em que todo elemento tem o mesmo tipo e `i` pode ser um valor de runtime. Em vez de inventar um `.0` ou um `[0]` com regras especiais de literal-de-compile-time, a tupla simplesmente não tem acesso posicional algum. Se você precisa de acesso aleatório, use uma struct (nomeada) ou um array (homogêneo).

## 3. Retorno múltiplo é retornar uma tupla

Uma função que retorna múltiplos valores é, exatamente, uma função que retorna uma tupla. `return 10, 10` é açúcar para `return (10, 10)`:

```dlang
buscarCoordenadas :: () -> (int, int) = (10, 10)   // 'return 10, 10' == 'return (10, 10)'
val (cx, cy) = buscarCoordenadas()
```

## 4. Onde a tupla já estava em uso

Vários recursos existentes acabam sendo tuplas, agora unificados sob um conceito:

```dlang
val conteudo, err = lerArquivo("config.txt")   // desestrutura uma tupla (string, Erro)
for (chave, valor : keyValueMap) { ... }         // o 'for' itera tuplas (chave, valor)
```

## 5. Desestruturação de struct fora do match

A forma de desestruturação de struct do [casamento de padrões](37-pattern-matching.md) também funciona como uma ligação comum, fora de qualquer `match`:

```dlang
val Pessoa { nome, idade } = usuario
println(nome)
```

## A regra dos parênteses

O uso de parênteses é único e previsível:

- **Valor ou tipo de tupla:** sempre com parênteses — `(10, 20)`, `(int, int)`.
- **Ligação `val`/`var` e `return`:** opcionais, porque a palavra-chave já delimita a tupla. `val a, b = f()` é o mesmo que `val (a, b) = f()`, e `return 1, 2` é o mesmo que `return (1, 2)`.
- **Dentro de `match`, `for` ou quando aninhada:** obrigatórios — `(x, y) ->`, `(nome, (x, y))`.

## Tabela de acesso por tipo

DLang dá exatamente uma forma de acesso por tipo, então as formas nunca colidem:

| Forma | Tipo | Por quê |
|-------|------|---------|
| `[i]` | array / List | homogêneo, índice de runtime |
| `.campo` | struct | heterogêneo, nomeado |
| `val (a, b) =` | tupla | heterogêneo, anônimo, só desestruturação |

## Por quê

Ao tornar a tupla um tipo de valor residente na pilha e sem acesso posicional, DLang mantém uma divisão de trabalho limpa: arrays para dados homogêneos indexados, structs para dados heterogêneos nomeados, tuplas para o agrupamento rápido, anônimo e heterogêneo que você desestrutura na hora. Retorno múltiplo, `for` sobre um mapa e retornos de erro todos colapsam neste único conceito em vez de serem três recursos de linguagem separados.

## Relacionados

- [Retorno de múltiplos valores](11-multiple-returns.md)
- [Casamento de Padrões](37-pattern-matching.md)
- [Structs](17-structs.md)
- [Arrays e listas](07-arrays-and-lists.md)

[← Índice](README.md)
