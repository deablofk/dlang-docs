# Generics e Programação Paramétrica

Generics permitem que uma única definição funcione sobre muitos tipos. DLang os implementa por **monomorfização** — o compilador estampa uma cópia especializada para cada instanciação concreta, exatamente como Rust e Zig — então código genérico tem *custo zero*: uma `List(int)` é tão rápida e compacta quanto uma lista de inteiros escrita à mão. Parâmetros genéricos são escritos em `Nome(...)` **antes** do `::`, espelhando como você já os *usa* no ponto de chamada (`List(int)`, `Map(string, int)`).

## Structs genéricas

A lista de parâmetros de tipo vem logo após o nome, antes do `::`. É por isso que uma struct genérica se lê do mesmo jeito quer você a esteja definindo, quer instanciando.

```dlang
// struct genérica — o (T) antes do "::" casa com o uso List(int)
List(T) :: struct {
  arrayInterno: Ptr(T)
  tamanho: int
  capacidade: int
}
```

## Métodos em tipos genéricos

Um método sobre um tipo genérico mantém os parâmetros de tipo em escopo, e é isso que permite a um método mencionar `T` na sua assinatura:

```dlang
List(T).add :: (item: T) {
  // ...
}

List(T).operator_get :: (indice: int) -> T {
  return _.arrayInterno[indice]
}
```

Múltiplos parâmetros são apenas uma lista separada por vírgulas, espelhando `Map(string, int)` no ponto de uso:

```dlang
Map(K, V) :: struct {
  // ...
}
```

## Funções genéricas

Funções seguem a regra idêntica: os parâmetros genéricos vivem em `Nome(...)` antes do `::`.

```dlang
max(T) :: (a, b: T) -> T = if (a > b) a else b
```

Você pode chamar com inferência, deixando o compilador recuperar `T` a partir dos argumentos, ou passar o tipo explicitamente para desambiguar:

```dlang
val m = max(10, 20)        // T = int, inferido dos argumentos
val x = max(int)(10, 20)   // instancia max(int), depois chama
val l = List(int).init(_alloc)
```

## Parâmetros de valor em tempo de compilação

Parâmetros genéricos não se limitam a tipos. Um parâmetro pode ser um *valor* de tempo de compilação, fiel à postura "tipos são valores de compile-time" da linguagem e conectando diretamente com os arrays fixos `[N]T`:

```dlang
// T é um tipo, N é um valor int conhecido em compile-time
Buffer(T, N: int) :: struct {
  data: [N]T // tamanho fixo resolvido durante a compilação
}

val b: Buffer(int, 16) = ... // um array interno de 16 ints, custo zero
```

Como `N` é conhecido em tempo de compilação, `Buffer(int, 16)` tem seu tamanho gravado sem contabilidade em runtime. Esta é a base dos tipos dependentes limitados de DLang (veja [Sistema de Tipos Dependentes](48-dependent-types.md)).

## Restrições via interfaces (opcionais)

Um parâmetro genérico pode ser *sem restrição*, caso em que funciona duck-typed em tempo de compilação — qualquer operação que você use simplesmente precisa existir para o tipo concreto, ao estilo Zig. Ou você pode anexar um limite por interface, que documenta o contrato e move o erro para o ponto de chamada, ao estilo Rust.

```dlang
// 'Comparable' é uma interface comum (define operator_compare, por exemplo)
ordenar(T: Comparable) :: (lista: List(T)) {
  // o compilador garante que todo T aqui implementa Comparable
  // -> um erro claro no ponto da chamada, não no fundo da função
}
```

Ambas as formas têm igual custo zero; a única diferença é *onde* e *com que clareza* uma incompatibilidade é reportada. Sem um limite você ganha máxima flexibilidade; com um limite você ganha um contrato documentado e um erro mais amigável.

## Por quê

A monomorfização é o que torna os generics gratuitos: não há empacotamento, despacho virtual nem informação de tipo em runtime envolvidos — cada instanciação compila para um código tão específico quanto se você o tivesse escrito à mão. Colocar os parâmetros em `Nome(...)` antes do `::` faz definição e uso compartilharem uma sintaxe, então `List(T) :: struct` e `List(int)` são visivelmente a mesma forma. Permitir parâmetros de *valor* em compile-time, não só de tipo, é o que deixa buffers de tamanho fixo e tipos dimensionados existirem sem custo em runtime, e é a ponte para os tipos dependentes limitados da linguagem. Tornar as restrições por interface *opcionais* mantém o caso comum leve enquanto ainda oferece mensagens de erro no ponto de chamada, nível Rust, quando você quer o contrato escrito. Uma consequência agradável é que `List` e `Map` não precisam de nenhuma mágica do compilador — viram structs genéricas comuns incluídas na biblioteca padrão.

## Relacionados

- [Tipagem Estática](29-static-typing.md)
- [Inferência de Tipos](31-type-inference.md)
- [Interfaces](25-interfaces.md)
- [Arrays e Listas](07-arrays-and-lists.md)
- [Sistema de Tipos Dependentes](48-dependent-types.md)
- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)

[← Índice](README.md)
