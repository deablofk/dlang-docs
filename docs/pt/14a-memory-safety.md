# Segurança de Memória

DLang é seguro em memória por construção. O modelo é **Mutable Value Semantics (MVS) puro** — a disciplina pioneirada pelo **Hylo** — com as palavras-chave próprias da DLang: todo dado é um *valor* com exatamente um dono, mutação acontece através do dono (nunca através de um alias), e o compilador destrói cada dono automaticamente no seu último uso. Use-after-free, liberação dupla, uso-após-move, referências pendentes e mutação com alias são **erros de compilação**, rejeitados com **custo zero em runtime**. Não há coletor de lixo, não há contagem de referências e não há anotações de lifetime.

Isso não é opcional e não há flag: as verificações rodam em **todo build**. Ponteiros crus ainda existem, mas apenas no *piso Builtin* — dentro das implementações auditadas dos tipos donos — nunca em código de aplicação (veja [a lei de fronteira](#a-lei-de-fronteira--nada-de-memória-crua-fora-do-piso)).

## O vocabulário, de relance

| Palavra-chave / forma | Onde | Significado |
|---|---|---|
| `nocopy` | antes de `struct` | o tipo é **afim**: movido, não copiado; exatamente um dono |
| `deinit` | nome de método | destrutor; o compilador o chama **automaticamente no último uso do valor** |
| `nodrop` | antes de `struct` | reservado: afirma um `deinit` que só libera memória (hoje inerte) |
| `borrow` | antes de um parâmetro (o padrão) | acesso só de leitura; o chamador mantém a posse |
| `inout` | antes de um parâmetro | acesso mutável exclusivo com **write-back** — o chamador vê a mutação |
| `sink` | antes de um parâmetro | a posse transfere-se para o chamado |
| `set` | antes de um parâmetro | um **slot de saída**: começa não inicializado, o chamado deve atribuí-lo em todo caminho |
| `yields` | na assinatura de um acessor | declara um acessor de **projeção** (acesso in-place a um elemento) |
| `yield e` | dentro de um corpo `yields` | a expressão que a projeção expõe |
| `inout e = xs.at(i)` | statement | vincula uma projeção por uma sequência de statements; o dono fica travado enquanto ela vive |
| `.copy()` | chamada de método | cópia profunda explícita de um valor afim — o único jeito de duplicá-lo |

## Valores são o padrão

Um `struct` comum é um valor. Atribuí-lo ou passá-lo o copia, e a cópia é independente — não há aliasing para raciocinar e não há ponteiro para pender. Cópia implícita é permitida **apenas para dados que não precisam de limpeza**; qualquer coisa com destrutor é move-only por regra (abaixo).

```dlang
Point :: struct { x: int  y: int }
val p: Point = Point { x: 1, y: 2 }
val q: Point = p          // cópia independente — mudar q nunca afeta p
```

## Recursos com dono — tipos `nocopy` (afins)

Um recurso que precisa ser liberado exatamente uma vez — um socket, um arquivo, um buffer que cresce — é um struct **`nocopy`**. Um valor `nocopy` é *afim*: ele é **movido, não copiado**. A atribuição transfere a posse, e usar o binding antigo depois disso é um erro de compilação — o mesmo defeito de um use-after-free, pego antes de o programa rodar.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () { /* fecha o fd */ }       // destrutor — roda automaticamente
shutdown :: (sink s: Socket) { }               // `sink` = toma posse

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  shutdown(s)                // posse consumida aqui
  val vazou: int = s.fd      // ERRO[E_USE_AFTER_MOVE]
  shutdown(s)                // ERRO[E_USE_AFTER_MOVE]  (uma liberação dupla, estaticamente)
  return vazou
}
```

Os contêineres padrão são eles mesmos donos `nocopy`: **`List(T)`, `Map(K, V)`, `ByteBuf`, `Pool(T)`** possuem seu armazenamento assim. Ou seja, `val ys = xs` numa `List` é um **move** — o modelo de custo honesto. Para entregar o mesmo conteúdo a dois donos, peça explicitamente com `xs.copy()`.

A afinidade é **contagiosa**: um struct contendo um campo `nocopy` é ele próprio `nocopy` — não dá para contrabandear um valor com dono por dentro de um invólucro copiável.

### Destruição automática — `deinit` ASAP

Um tipo `nocopy` pode definir `deinit`. O compilador insere a chamada **no último uso estático do valor** — o mais cedo possível, não no fim do escopo — sem drop flags e sem contabilidade de runtime, exatamente uma vez em **todo** caminho (fall-through, `return` antecipado, `break`, `continue`). É a destruição ASAP no estilo Mojo: você nunca escreve um free, e não tem como esquecer um.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () { println("socket fechado") }
peek :: (s: Socket) -> int = s.fd     // borrow — NÃO consome

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  val a: int = peek(s)      // borrow — ainda com dono
  val b: int = peek(s)      // borrow de novo — ok
  return a + b              // "socket fechado" impresso após o último uso de s
}
```

Valores `string` são gerenciados do mesmo jeito (o compilador libera na hora os intermediários mortos de `+`/interpolação — veja a nota sobre strings abaixo), e o `deinit` de uma `List` derruba recursivamente cada elemento antes de liberar o buffer.

## Convenções de parâmetro — `borrow`, `inout`, `sink`, `set`

Uma convenção num parâmetro declara o que o chamado faz com o argumento. Essa é toda a história de "referências" em DLang: referências existem apenas *em fronteiras de chamada*, são criadas implicitamente (sem `&` no call site) e não podem escapar da chamada.

| Convenção | Acesso do chamado | Posse |
|---|---|---|
| `borrow` (padrão) | só leitura | o chamador mantém |
| `inout` | leitura-escrita exclusiva, **com write-back** | o chamador mantém e vê a mutação |
| `sink` | total | transfere-se ao chamado |
| `set` | escreve-primeiro (começa **não inicializado**) | o chamador fica com o resultado inicializado |

```dlang
peek    :: (s: Socket) -> int = s.fd          // borrow: chame quantas vezes quiser
rename  :: (inout p: Pessoa, n: string) { p.nome = n }   // o p do chamador muda
consume :: (sink s: Socket) { }               // s morre aqui (o deinit roda no chamado)
firstTwo :: (xs: List(int), set a: int, set b: int) {    // slots de saída
  a = xs.get(0)
  b = xs.get(1)                               // todo caminho DEVE atribuir a e b
}
// chamador: `var a: int` (não inicializado, ok) e então firstTwo(xs, a, b)
```

As regras que mantêm isso sadio:

- **Um parâmetro simples (borrow) é imutável.** Atribuir a ele ou através dele é `E_IMMUTABLE`. Se o chamador deve ver a mudança, diga: `inout`.
- **`inout` é write-back de verdade.** O argumento precisa ser um lvalue mutável enraizado num `var`; o valor do chamador é atualizado quando a chamada retorna. Isso importa especialmente para valores afins: passar um struct `nocopy` como parâmetro simples dá ao chamado uma *visão só de leitura*, não um alias mutável.
- **Um borrow não escapa.** Retornar, armazenar ou dar `sink` num parâmetro emprestado é `E_REF_ESCAPES` — um borrow nunca sobrevive à sua chamada.
- **Lei da Exclusividade.** Dois argumentos `inout` não podem apelidar o mesmo armazenamento (`E_EXCLUSIVITY`); um empréstimo mutável é sempre exclusivo.
- **`set` é verificado por atribuição definitiva.** O chamado deve atribuir o slot em todo caminho (`E_SET_UNASSIGNED`) e não pode lê-lo antes da primeira atribuição (`E_SET_BEFORE_ASSIGN`). `set` é a resposta PVS para "construir o resultado onde ele precisa viver" — construção-para-fora in place, sem ponteiro.

```dlang
bump2 :: (inout a: int, inout b: int) { }
main :: () -> int {
  var x: int = 1
  bump2(x, x)     // ERRO[E_EXCLUSIVITY]: 'x' apelidado por dois argumentos inout
  return x
}
```

## Projeções — `yields`, auto-deref e bindings `inout`

Contêineres move-only precisam de um jeito de tocar *um elemento in place* sem copiá-lo para fora nem movê-lo. Isso é uma **projeção**: uma referência de segunda classe, enraizada no receiver, produzida por um acessor `yields`. `List(T).at` é o modelo:

```dlang
xs.at(i).hp = 99                 // auto-deref: muta um campo do elemento i in place
xs.at(i).inventario.add("poção") // donos aninhados também mutam in place
```

Para segurar uma projeção por vários statements, vincule-a com `inout`:

```dlang
inout e = xs.at(i)     // e projeta o elemento i
e.hp = e.hp - 10
e.escudo = 0
// enquanto e vive, xs fica TRAVADA: usá-la aqui é E_EXCLUSIVITY
// (um crescimento poderia realocar o buffer e pender a projeção)
```

Qualquer outra retenção de uma projeção — um binding `val`/`var`, guardar num campo, retornar, passar a uma função comum — é `E_REF_ESCAPES`, em todo build. Para *ficar* com um elemento, mova-o para fora com `xs.removeAt(i)`.

Você declara projeções nos seus próprios donos:

```dlang
Cell :: struct { v: int }
Board :: nocopy struct { cells: List(Cell) }
Board.cell :: (x: int, y: int) yields Cell = _.cells.at(y * 8 + x).value
// (encaminhar uma projeção interna a dereferencia com .value; corpos em bloco usam `yield e`)

board.cell(3, 4).v = 1        // acesso a membro auto-dereferencia, igual a List.at
```

Uma projeção de um *escalar* (`yields int`) é escrita através de `.value` — `score.cell(i).value = 9` — já que não há membro para auto-deref. Dentro de um corpo `yields` o compilador permite o `ref` enraizado no receiver de que ele precisa; chamadores nunca veem um ponteiro.

## Grafos e identidade compartilhada — `Pool(T)` + `Handle`, ou índices

Posse única expressa árvores. Para **ciclos, referências de volta e lifetimes em formato ECS** (entidades que se referenciam e morrem independentemente), a resposta da DLang é *índices em vez de ponteiros*:

- **`Pool(T)` + `Handle`** (`import("std/collections/pool")`): um armazém de slots com **handles geracionais**. `Handle { slot, gen }` é um valor copiável comum — guarde em campos, listas, outras entidades; ciclos são de graça. Matar uma entidade incrementa a geração do slot, então toda cópia velha do handle fica *detectavelmente morta* (`alive(h) == false`) em vez de pendente:

```dlang
inline import("std/collections/pool")

var mobs: Pool(Mob) = Pool(Mob).empty()
val h: Handle = mobs.spawn(Mob { hp: 10, alvo: Handle { slot: -1, gen: -1 } })
if (mobs.alive(h)) {
  mobs.at(h).hp = 9        // .at(h) é uma projeção, mesmas regras de List.at
}
mobs.kill(h)               // idempotente; o slot é reciclado por um spawn futuro
```

- **A codificação por índice**: para armazéns append-only (uma AST, uma tabela de interning), índices `int` simples numa `List(Node)` funcionam direto — um índice não pende num armazém que nunca encolhe. É assim que o próprio compilador da DLang representa suas árvores de sintaxe.

**Não há blocos de região/arena na linguagem.** O antigo tier `region { … }` / `detach` foi removido quando o modelo MVS puro chegou (escrevê-los é `E_NOT_SUPPORTED`, com uma dica de migração): tudo que uma região fazia é coberto por donos que morrem no último uso, `Pool`/índices para grafos e parâmetros `set` para construir resultados in place.

## A lei de fronteira — nada de memória crua fora do piso

`Ptr(T)`, `New`, `Undo`, `ref` e `_alloc.*` ainda existem — são o material de que `List` e `string` são *feitas* — mas estão confinados ao **piso Builtin**. Operações cruas são legais apenas:

1. dentro dos métodos de um **handle dono** `nocopy` + `deinit` (a superfície de implementação crua de `List`, `Map`, `ByteBuf`, seus próprios invólucros de recursos),
2. em **assinaturas extern C** (declarações FFI sem corpo),
3. na implementação da própria `string`,
4. em corpos de acessores `yields` (o `ref` enraizado no receiver),
5. nos hooks fixos do runtime.

Em qualquer outro lugar — uma assinatura, um campo de struct, um local, uma alocação em código comum — é **`E_RAW_OUTSIDE_BUILTIN`**, em todo build, **sem allowlist de módulos**: a biblioteca padrão obedece à mesma lei, e o compilador está migrando as próprias fontes para ela. `--raw-floor` desliga a lei apenas para código abaixo do modelo (o bootstrap do compilador e os harnesses de prova que introspectam o alocador); não é para aplicações.

Buffers de FFI cruzam fronteiras de API como endereços `long` opacos (`ByteBuf.addr(i)`, `cast(long, s.cstr())`), e um recurso possuído por C é embrulhado num handle dono cujo `deinit` o libera exatamente uma vez. Veja [Memória Manual](13-manual-memory.md) para o piso completo.

## Strings e recuperação ASAP

`string` é um valor com posse gerenciada pelo compilador: temporários de interpolação e `+`, argumentos de `println` e locais de acumulação (`var s` … `s = s + pedaço` num laço) são liberados **na hora** por drops inseridos pelo compilador. O idioma de acumulação é, portanto, o jeito *preferido* de construir strings — ele não vaza mais. (Continua sendo O(n²) de cópia para saídas muito grandes; use junção divide-e-conquista nessas.)

## Os códigos de erro

| Código | Forma de programa rejeitada |
|---|---|
| `E_USE_AFTER_MOVE` | usar / reconsumir um valor afim depois de movido |
| `E_IMMUTABLE` | escrever através de um parâmetro simples (borrow) |
| `E_EXCLUSIVITY` | argumentos `inout` apelidados; tocar um dono enquanto sua projeção vive |
| `E_REF_ESCAPES` | um borrow ou projeção escapando da sua chamada / escopo de statement |
| `E_SET_UNASSIGNED` / `E_SET_BEFORE_ASSIGN` | um slot `set` não atribuído em todo caminho / lido cedo demais |
| `E_RAW_OUTSIDE_BUILTIN` | qualquer vocabulário de memória crua fora do piso sancionado |
| `E_NOT_SUPPORTED` | o tier removido `region` / `detach` |

## Técnicas e trabalhos anteriores

O modelo é uma síntese de técnicas estabelecidas — a contribuição da DLang é o compromisso com a combinação *pura*, sem sobrar nenhum tier inseguro visível ao usuário:

- **Mutable Value Semantics** — valores com posse única, mutação só através do dono, sem referências de primeira classe: **Hylo** (ex-Val). DLang é uma implementação purista de Hylo com sua própria superfície de palavras-chave.
- **Convenções de passagem de parâmetro** (`borrow` / `inout` / `sink` / `set`) e **referências de segunda classe** — também do **Hylo**, espelhadas pelos modificadores `borrowing`/`consuming` do **Swift**; `set` é a convenção de out-inicialização do Hylo.
- **Lei da Exclusividade** — acesso mutável exclusivo, do **Swift** (SE-0176).
- **Projeções** — acessores `yields` no estilo subscript são as corrotinas de acessor do Hylo (e do Swift); o travamento de raiz em tempo de compilação substitui verificações de exclusividade em runtime.
- **Tipos afins / semântica de move** — `nocopy` é a disciplina de posse do **Rust**, os tipos lineares do **Austral**, as abilities do **Move**.
- **Destruição ASAP sem drop flags** — da destruição ASAP do **Mojo** e da análise de reuso do **Perceus** (Koka).
- **Índices geracionais** — `Pool(T)` + `Handle` é o idioma ECS em que Hylo e a comunidade Rust de gamedev convergiram: obsolescência dinâmica em vez de lifetimes léxicos.

Uma iteração anterior do modelo também tinha regiões léxicas no estilo Tofte–Talpin para grafos de ponteiros; foram **deletadas** quando projeções, `set` e `Pool` se provaram suficientes — uma zona crua léxica era o único lugar onde a alegação de segurança ficava condicional, e o Hylo demonstra que o modelo se sustenta sem ela.

## As garantias, de relance

| Bug | Resultado |
|---|---|
| use-after-free / liberação dupla | **erro de compilação** (`E_USE_AFTER_MOVE`) |
| referência pendente | irrepresentável — referências nunca escapam de uma chamada |
| mutação com alias | **erro de compilação** (`E_EXCLUSIVITY`) |
| projeção pendendo através de um grow | **erro de compilação** (trava de raiz / `E_REF_ESCAPES`) |
| handle de entidade obsoleto | **detectável** (`pool.alive(h) == false`), nunca pendente |
| ponteiro cru em código de aplicação | **erro de compilação** (`E_RAW_OUTSIDE_BUILTIN`) |
| limpeza esquecida | impossível — `deinit` é automático, exatamente uma vez, ASAP |
| custo de runtime de tudo isso | **zero** — inteiramente estático |

## Relacionados

- [Memória Manual — o piso Builtin](13-manual-memory.md)
- [Coleta de Lixo (por que não há)](14-garbage-collection.md)
- [Alocação Dinâmica — valores donos](18-dynamic-allocation.md)
- [Ponteiros e Referências](12-pointers-and-references.md)
- [Passagem de Parâmetros](10-parameter-passing.md)
- [Construtores e Destrutores](21-constructors-and-destructors.md)

[← Índice](README.md)
