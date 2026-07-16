# Memória Manual — o Piso Builtin

Código DLang comum **não gerencia memória**. Toda alocação pertence a um valor dono — uma `string`, uma `List`, um `Map`, um `ByteBuf`, um `Pool`, ou um dono que você mesmo escreve — e o compilador destrói cada dono no seu último uso estático ([Segurança de Memória](14a-memory-safety.md)). Não há `malloc` visível ao usuário, não há bloco de arena e não há chamada de `free` para esquecer.

Mas *alguém* precisa implementar a `List`, e alguém precisa segurar o recurso cru que uma biblioteca C devolve. Esse alguém é o **piso Builtin**: a camada de baixo, auditada, onde o vocabulário cru — `Ptr(T)`, `New`, `Undo`, `ref`, `_alloc.*` — é legal. Esta página é sobre escrever código de piso corretamente. Se você não está implementando um handle dono nem fazendo binding de C, você nunca deve precisar dele.

## A lei de fronteira

Operações de memória crua são legais **apenas**:

1. dentro dos métodos de um **handle dono `nocopy` + `deinit`** — o struct cujo único trabalho é possuir uma alocação ou um recurso estrangeiro,
2. em **assinaturas extern C** (declarações sem corpo — veja [Interop com C](50-c-interop.md)),
3. na implementação da própria `string`,
4. em corpos de acessores `yields` (o `ref` enraizado no receiver),
5. nos hooks fixos do runtime.

Em qualquer outro lugar elas são **`E_RAW_OUTSIDE_BUILTIN`**, em todo build. Não há allowlist de módulos — a biblioteca padrão joga pelas mesmas regras, e o mesmo punhado de primitivas por baixo da `List` é o que você ganha para os seus próprios donos.

## A REGRA DE OURO

> **Todo design declara quem possui cada alocação e onde ela morre.**

No piso essa regra é literal: cada `New` deve pertencer a exatamente um handle dono, e o `deinit` desse handle é onde ela morre. O compilador garante que o `deinit` roda exatamente uma vez, no último uso do dono — seu trabalho é só fazer o `deinit` liberar tudo que o handle possui.

## Escrevendo um handle dono

O cidadão canônico do piso: um struct `nocopy` cujos *métodos* fazem o trabalho cru e cujo `deinit` libera a alocação. Nada fora dos métodos vê um ponteiro.

```dlang
// Uma pilha de ints que cresce, implementada crua — exatamente como a List funciona.
IntStack :: nocopy struct {
  data: Ptr(int)
  len : int
  cap : int
}

IntStack.empty :: () -> IntStack = IntStack { data: null, len: 0, cap: 0 }

IntStack.push :: (v: int) {
  if (_.len == _.cap) {
    var grown: int = _.cap * 2
    if (grown == 0) {
      grown = 4
    }
    val buf: Ptr(int) = _alloc.alloc(int, grown)   // legal: método de handle dono
    for (i : 0..(_.len - 1)) {
      buf[i] = _.data[i]
    }
    if (_.cap > 0) {
      _alloc.free(_.data)
    }
    _.data = buf
    _.cap = grown
  }
  _.data[_.len] = v
  _.len = _.len + 1
}

IntStack.pop :: () -> int {
  _.len = _.len - 1
  return _.data[_.len]
}

IntStack.deinit :: () {          // o compilador chama isto no último uso
  if (_.cap > 0) {
    _alloc.free(_.data)
  }
}
```

Quem chama usa `IntStack` como um valor seguro comum: ele move como qualquer tipo `nocopy`, `E_USE_AFTER_MOVE` o protege, e o buffer é liberado automaticamente. O campo `Ptr(int)` é legal *porque* o struct é um dono `nocopy`+`deinit`; o mesmo campo num struct copiável é rejeitado onde quer que esse struct seja usado.

Dentro dos métodos, o vocabulário cru é o clássico:

```dlang
val h: Ptr(Pessoa) = New(Pessoa)    // aloca um T na heap   (= _alloc.alloc(T))
Undo(h)                             // o free pareado       (= _alloc.free(h))
val buf: Ptr(int) = New(int, 8)     // N elementos contíguos
buf[3] = 42                         // indexação de ponteiro, sem verificação
val p: Ptr(int) = ref score         // endereço-de
p.value = 10                        // dereferência
```

Não há verificação de limites nem de lifetime aqui dentro — esta é deliberadamente a camada auditada onde a garantia é responsabilidade do seu código, mantida pequena o bastante para auditar.

## Embrulhando um recurso de C

Um recurso alocado por C — uma lista `addrinfo`, uma sessão SSL, um mapeamento de arquivo — recebe o mesmo tratamento: um handle dono cujos métodos fazem as chamadas cruas e cujo `deinit` o libera exatamente uma vez. `AddrInfoList` em `std/net/socket.dlang` é o modelo:

```dlang
getaddrinfo  :: (node: Ptr(byte), service: Ptr(byte), hints: Ptr(byte), res: Ptr(byte)) -> int
freeaddrinfo :: (res: Ptr(byte)) -> void

AddrInfoList :: nocopy struct { head: long }     // a lista crua, carregada como long opaco
AddrInfoList.deinit :: () {
  if (_.head != cast(long, 0)) {
    freeaddrinfo(cast(Ptr(byte), _.head))        // liberado exatamente uma vez, automaticamente
  }
}
```

Dois idiomas de piso completam a história de FFI:

- **Buffers de rascunho** para out-structs de C são um `ByteBuf` local: `ByteBuf.new(n)` + `.zeros(n)`, passe `.addr(0)` (um `long` opaco) para o C, leia os campos de volta com `.i32at`/`.i64at`. O buffer morre no último uso como qualquer dono — `std/time` e `std/net` são os modelos.
- **Endereços viajam como `long`.** Uma expressão `Ptr` pode fluir *um salto* para um argumento extern C ou um método de handle dono/`string`; além disso, tudo cruza como `long` opaco (`ByteBuf.addr(i)`, `cast(long, s.cstr())`). Ponteiros nunca se espalham por assinaturas.

## E o `defer`?

`defer` continua existindo como ferramenta geral de controle (rodar um statement na saída da função), mas **não é mais como memória é liberada** — o `deinit` no último uso substituiu o idioma `defer Undo(p)`, e não pode ser esquecido nem duplicado. Use `defer` para efeitos que não são posse (logar, destravar em código que precede um dono, teardown de teste).

## O alocador é um detalhe de implementação

Os métodos dos donos roteiam alocações pelo alocador do runtime (`std/mem/allocator.dlang`). **Não há jeito suportado de código comum trocá-lo** — nenhuma API de alocador ambiente existe acima do piso. Os dois artefatos restantes (`debugAllocator` para rastrear vazamentos, e a arena em bloco que o compilador usa no próprio pipeline durante sua automigração) são ferramentas, compiladas com `--raw-floor` — a flag que desliga a lei de fronteira para código abaixo do modelo. Aplicações nunca precisam dessa flag.

## Racional de design

A memória manual não desapareceu — ela ganhou um *lugar*. O piso mantém DLang uma linguagem de sistemas: ponteiros de verdade, layout exato, FFI custo-zero, alocação que se lê. A lei de fronteira impede o piso de vazar para cima: o vocabulário inseguro fica confinado a tipos cuja única responsabilidade é posse, pequenos o bastante para auditar, embrulhados numa interface em que o verificador pode confiar. Toda propriedade de segurança acima (moves, borrows, projeções, `deinit` ASAP) repousa sobre esses handles estarem corretos — e é por isso que a linguagem faz de "onde código cru pode viver" uma lei imposta pelo compilador, não uma convenção.

## Relacionados

- [Segurança de Memória](14a-memory-safety.md)
- [Alocação Dinâmica — valores donos](18-dynamic-allocation.md)
- [Ponteiros e Referências](12-pointers-and-references.md)
- [Interop com C](50-c-interop.md)
- [Construtores e Destrutores](21-constructors-and-destructors.md)

[← Índice](README.md)
