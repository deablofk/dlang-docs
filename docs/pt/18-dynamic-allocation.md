# Alocação Dinâmica

A alocação dinâmica reserva memória na heap em tempo de execução, para dados cujo tamanho não é conhecido em tempo de compilação. Em DLang você nunca chama um alocador para isso — **você cria um valor dono**, e o tipo do valor faz a alocação, o crescimento e a liberação. `List(T)`, `Map(K, V)`, `string`, `ByteBuf` e `Pool(T)` são os donos padrão; seus próprios tipos `nocopy` + `deinit` se juntam a eles. O compilador destrói todo dono no seu último uso, então a memória dinâmica tem a mesma disciplina de ciclo de vida de todo o resto — sem `new`, sem `free`, sem vazamento.

## Contêineres que crescem

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).empty()
  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
  println("${itens.size()} itens")    // último uso — o buffer da lista é liberado aqui
}
```

`List(string).empty()` começa vazia e cresce dobrando conforme você dá `add`; `Map(K, V).empty()` se comporta igual. Ambos são structs genéricos comuns da biblioteca padrão — não mágica do compilador — implementados no piso Builtin ([Memória Manual](13-manual-memory.md)) e expostos a você como valores donos seguros.

Como os contêineres são **donos `nocopy`**, entregá-los segue semântica de move:

```dlang
var xs: List(int) = List(int).empty()
xs.add(1)
val ys: List(int) = xs        // MOVE — xs foi consumida (usá-la de novo é E_USE_AFTER_MOVE)
val zs: List(int) = ys.copy() // cópia profunda explícita quando você realmente quer duas
```

## Strings

`string` é um valor imutável alocado dinamicamente, com posse gerenciada pelo compilador. Construa strings do jeito óbvio — concatenação, interpolação, acumulação num laço — e o compilador libera cada intermediário morto na hora:

```dlang
var relatorio: string = ""
for (item : itens) {
  relatorio = relatorio + "- ${item}\n"   // cada intermediário morto é liberado imediatamente
}
```

## Buffers de bytes

Dados binários vivem num `ByteBuf` — o buffer de bytes dono e que cresce: `ByteBuf.new(cap)` (e `.zeros(n)` para uma área de rascunho inicializada), escritores big-endian (`.u8` … `.u64`), `.appendStr(s)`, leitores (`.byteAt`, `.i32at`, `.i64at`) e `.addr(i)` quando um endereço cru precisa cruzar para o C como um `long` opaco. É o rascunho padrão para out-structs de FFI — e como todo dono, morre no último uso.

## Armazéns de entidades

Quando muitas coisas alocadas dinamicamente se referenciam e morrem de forma independente — entidades de jogo, nós de grafo — aloque-as num **`Pool(T)`** e ligue-as com valores `Handle` copiáveis ([Segurança de Memória](14a-memory-safety.md)). O pool é o único dono de todos os seus slots; o handle de um slot morto fica detectavelmente obsoleto em vez de pendente.

## Construindo no lugar — `set`

Onde C passaria um ponteiro para o chamado preencher, DLang passa um parâmetro **`set`**: o chamado deve inicializar o slot do chamador em todo caminho, verificado por atribuição definitiva. É assim que "alocar o resultado onde ele precisa viver" funciona sem ponteiro:

```dlang
Vector :: struct { x: int  y: int }

makeUniform :: (set out: Vector, scale: int) {
  out = Vector { x: scale, y: scale }   // todo caminho deve atribuir `out`
}

var v: Vector          // deliberadamente não inicializado — o chamado o constrói
makeUniform(v, 3)      // v está totalmente inicializado aqui
```

## Escrevendo seu próprio dono

Um tipo que possui uma alocação dinâmica é um struct `nocopy` com `deinit`; seus métodos (e apenas eles) podem usar o vocabulário cru do piso para alocar e crescer. Veja [Memória Manual](13-manual-memory.md) para um exemplo completo — uma `IntStack` que cresce, implementada exatamente como a `List` é.

## De onde a memória vem

Por baixo dos donos fica o alocador do runtime (`std/mem/allocator.dlang`) — um detalhe de implementação do piso Builtin. Código comum não pode (e não precisa) trocá-lo: a *estratégia* de memória em DLang se expressa escolhendo donos — um `Pool` para reuso de slots, um `ByteBuf` para bytes contíguos, `withCapacity(n)` para pré-dimensionar uma lista — não instalando um alocador diferente pelas costas do programa.

## Racional de design

A alocação manual clássica espalha pares `malloc`/`free` pelo código e faz de cada call site um vazamento em potencial. O GC clássico esconde a alocação por completo. Os donos da DLang são o meio-termo sem nenhum dos custos: a alocação é visível (`List(T).empty()`, `ByteBuf.new(n)` — dá para ler onde a heap é usada), a liberação é automática e determinística (o último uso do dono), e a maquinaria insegura que implementa o crescimento vive atrás da lei de fronteira, num punhado de tipos auditados. Memória dinâmica vira uma questão de *tipagem* — escolher o dono certo — em vez de uma questão de contabilidade.

## Relacionados

- [Segurança de Memória](14a-memory-safety.md)
- [Memória Manual — o piso Builtin](13-manual-memory.md)
- [Coleta de Lixo](14-garbage-collection.md)
- [Arrays e Listas](07-arrays-and-lists.md)
- [Mapas e Dicionários](08-maps-and-dictionaries.md)

[← Índice](README.md)
