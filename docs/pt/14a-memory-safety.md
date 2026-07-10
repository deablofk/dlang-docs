# Segurança de Memória

DLang está ganhando um **modelo de segurança de memória estática**: use-after-free, liberação dupla, uso-após-move e um ponteiro escapando de sua arena são **erros de compilação**, rejeitados antes de o programa poder rodar e com **custo zero em runtime** em builds de release. Não há coletor de lixo nem contabilidade escondida — a segurança vem da *forma* do programa, verificada pelo compilador.

Isso é opcional no sentido de que `Ptr(T)` cru + `Undo` (veja [Memória Manual](13-manual-memory.md)) continuam existindo como uma válvula de escape explícita e não verificada. Mas os idiomas seguros abaixo tornam classes inteiras de bug **impossíveis de expressar** em vez de apenas detectáveis.

## O problema, em um programa

Com ponteiros crus, um use-after-free e uma liberação dupla compilam sem erro e explodem em runtime:

```dlang
Socket :: struct { fd: int }
main :: () -> int {
  val s: Ptr(Socket) = New(Socket)
  s.value.fd = 42
  Undo(s)                        // libera
  val leaked: int = s.value.fd   // use-after-free (lê memória liberada)
  Undo(s)                        // liberação dupla
  return leaked
}
```

```
$ doven before.dlang
compile: OK              # o compilador aceitou o programa com bug
$ ./before
free(): double free detected in tcache 2   # crash, em runtime
```

O modelo transforma isso em erro de compilação.

## Camada 1 — valores são o padrão

DLang é semântica de valor por padrão. Um `struct` comum é um valor: atribuir ou passar copia, e não há ponteiro para ficar pendente. A maior parte dos dados vive aqui, e é segura de graça — não há nada a gerenciar.

```dlang
Point :: struct { x: int  y: int }
val p: Point = Point { x: 1, y: 2 }
val q: Point = p          // uma cópia independente
```

## Recursos possuídos — tipos `nocopy` (afins)

Um recurso que deve ser liberado exatamente uma vez — um socket, um arquivo, um lock — é um struct **`nocopy`**. Um valor `nocopy` é *afim*: é **movido, não copiado**. Ele tem exatamente um dono vivo, e usá-lo depois de essa posse ter sido cedida é erro de compilação — o mesmo defeito de um use-after-free.

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () = { /* fecha o fd */ }     // destrutor — roda automaticamente
shutdown :: (sink s: Socket) { }               // `sink` = toma posse

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  shutdown(s)                // posse consumida aqui
  val leaked: int = s.fd     // ERRO: uso de 's' depois de movido
  shutdown(s)                // ERRO: 's' consumido duas vezes (liberação dupla)
  return leaked
}
```

```
7:21: error[E_USE_AFTER_MOVE]: use of 's' after it was moved (a `nocopy` value is consumed when moved)
8:12: error[E_USE_AFTER_MOVE]: use of 's' after it was moved (a `nocopy` value is consumed when moved)
```

Tanto o uso-após-consumo quanto o consumo-duplo são rejeitados. Como há exatamente um dono, não existe uma segunda referência que pudesse ficar pendente.

### Destruição automática (`deinit`)

Um tipo `nocopy` pode definir `deinit`, que o compilador chama **automaticamente no último uso do valor** — sem `Undo` manual, sem `defer`, sem flags de drop, e exatamente uma vez em **todo** caminho (fim natural, `return` antecipado ou escopo aninhado).

```dlang
Socket :: nocopy struct { fd: int }
Socket.deinit :: () = { println("socket closed") }
use :: (s: Socket) -> int = s.fd     // empresta — NÃO consome

main :: () -> int {
  val s: Socket = Socket { fd: 42 }
  val a: int = use(s)     // empréstimo — ainda possuído
  val b: int = use(s)     // empresta de novo — ok
  return a + b
}
// imprime "socket closed" exatamente uma vez, no último uso de `s`
```

A afinidade é **contagiosa**: um struct comum que contém um campo `nocopy` vira `nocopy` automaticamente, então você não consegue contrabandear um valor possuído por meio de um invólucro copiável.

## Convenções de parâmetro — `borrow`, `sink`, `inout`

Uma convenção em um parâmetro diz como o chamado usa o argumento. É o que permite passar um valor `nocopy` a um auxiliar *sem* consumi-lo.

| Convenção | Significado |
|---|---|
| `borrow` (padrão) | acesso só-leitura; o chamador mantém a posse |
| `sink` | a posse é transferida ao chamado (o argumento é consumido) |
| `inout` | acesso mutável exclusivo |

```dlang
peek :: (s: Socket) -> int = s.fd          // borrow: pode ser chamado repetidamente
consume :: (sink s: Socket) -> int = s.fd  // sink: consome o socket
```

Duas regras mantêm os empréstimos sólidos:

- **Um empréstimo não pode escapar.** Retornar, armazenar ou fazer `sink` de um parâmetro emprestado é `E_REF_ESCAPES` — um empréstimo não pode sobreviver à chamada de onde veio.
- **Lei da Exclusividade.** Dois argumentos `inout` na mesma chamada não podem apontar para o mesmo armazenamento (`E_EXCLUSIVITY`), então um empréstimo mutável é sempre exclusivo.

```dlang
bump2 :: (inout a: int, inout b: int) { }
main :: () -> int {
  var x: int = 1
  bump2(x, x)     // ERRO[E_EXCLUSIVITY]: 'x' com alias em dois argumentos inout
  return x
}
```

## Arenas — blocos `region`

Posse única expressa árvores, mas não **ciclos ou referências de volta compartilhadas** — uma lista duplamente ligada, um grafo, uma AST com ponteiros de pai. Esses vão em uma **`region`**: uma arena lexical. Tudo alocado dentro é liberado como uma unidade no fim do bloco, e os objetos podem apontar uns para os outros livremente, sem anotações por ponteiro.

```dlang
Node :: struct { next: Ptr(Node)  prev: Ptr(Node)  v: int }
main :: () -> int {
  var sum: int = 0
  region g {
    val a: Ptr(Node) = New(Node)
    val b: Ptr(Node) = New(Node)
    a.value.next = b     // a -> b
    b.value.prev = a     // b -> a   (um ciclo — ok dentro de uma região)
    a.value.v = 30
    b.value.v = 12
    sum = a.value.v + b.value.v
  }                      // o grafo inteiro é liberado aqui, de uma vez
  return sum
}
```

### Isolamento de região

A arena é *segura*, não só conveniente: um ponteiro alocado em uma região **não pode escapar dela**. Armazenar um ponteiro de região onde ele sobreviveria à região — uma variável externa, ou um campo de um objeto externo — é erro de compilação, porque esse ponteiro ficaria pendente quando a região fosse liberada.

```dlang
main :: () -> int {
  var escaped: Ptr(Node) = null
  region g {
    val a: Ptr(Node) = New(Node)
    escaped = a          // ERRO[E_REGION_ESCAPE]: um ponteiro alocado na região
  }                      //   escapa da região ao ser armazenado em 'escaped'
  return escaped.value.v
}
```

## A válvula de escape e os limites honestos

`Ptr(T)` cru + `New`/`Undo` (veja [Memória Manual](13-manual-memory.md)) continuam disponíveis para interop com C e para os casos que o modelo estático ainda não cobre. Dentro dessa camada crua você está por sua conta, exatamente como em C — é a fronteira deliberada onde a garantia é sua responsabilidade.

O modelo está em desenvolvimento ativo. Lacunas conhecidas hoje: fluxo de controle que *escapa* de uma região (um `return` de dentro dela) é rejeitado em vez de suportado; escape de região por um chamado que armazena o ponteiro, ou por uma coleção, ainda não é pego; `inout` ainda não escreve de volta por referências; e heap de vida longa que não é nem uma `region` nem um handle possuído ainda depende da camada crua. Esses são refinamentos sobre um núcleo funcional, não buracos nele.

## Técnicas e trabalhos anteriores

Nada disso foi inventado do zero. O modelo é uma síntese de técnicas estabelecidas e nomeadas — da teoria de tipos e de outras linguagens — em que cada uma resolve uma parte do problema de use-after-free, e juntas o fecham *estaticamente*:

- **Tipos afins** (também chamados move-only / tipos substruturais) — o núcleo de `nocopy`. Um valor que pode ser usado *no máximo uma vez* não pode ser usado depois de consumido, então use-after-move e liberação dupla são o *mesmo* erro de tipo. É a disciplina de posse de **Rust**, os tipos lineares de **Austral** e os tipos de recurso da linguagem **Move**.
- **Semântica de move** — consumir um valor invalida sua ligação de origem; o compilador rastreia isso por caminho de fluxo de controle (como faz o borrow checker de **Rust**).
- **Semântica de Valor Mutável (MVS)** — semântica de valor por padrão sem aliasing visível ao usuário, de **Hylo** (antiga Val). Como os valores são independentes e referências não são de primeira classe, uma referência pendente é em grande parte impossível de expressar, e não apenas detectada.
- **Referências de segunda classe** e **convenções de passagem de parâmetro** (`borrow` / `sink` / `inout`) — também de **Hylo**, espelhadas pelos modificadores `borrowing` / `consuming` de **Swift**. Um empréstimo é criado só na fronteira da chamada e não pode escapar dela.
- **A Lei da Exclusividade** — acesso exclusivo para um empréstimo mutável (`inout`), de **Swift** (SE-0176, "Enforce Exclusive Access to Memory").
- **Gerenciamento de memória baseado em regiões** — o bloco `region { … }` é uma região de **Tofte–Talpin** (`letregion`, 1994; **MLKit**) e o dialeto seguro de C **Cyclone**. Objetos que compartilham um mesmo tempo de vida lexical são liberados como uma unidade, e o sistema de tipos garante que nenhuma referência sobrevive à sua região.
- **Isolamento de região / unicidade externa (`iso`)** — uma região é acessada por um único handle dono, então seu interior não pode ter alias de fora, de **Project Verona** e **Pony**. É o que torna a liberação em bloco de um grafo cíclico sólida e alimenta a verificação `E_REGION_ESCAPE`.
- **Tags de habilidade** (`nocopy` / `nodrop`) — capacidades de uma palavra sobre um tipo, no estilo das habilidades `copy` / `drop` / `store` da linguagem **Move**.
- **Destruição ASAP sem flags de drop** — `deinit` é inserido no *último uso* estático do valor, da destruição ASAP ("As Soon As Possible") de **Mojo** e da análise de reuso de **Perceus** (Koka). Não há flags de drop em runtime; a análise prova a posse em cada saída.
- **Contágio de afinidade** — um struct contendo um campo afim é ele próprio afim, como **Rust** propaga o não-`Copy`.

A disciplina geral — *rejeitar em tempo de compilação o que não puder ser provado seguro, com custo zero em runtime* — é o padrão de solidez estabelecido pelo borrow checker de **Rust** (formalmente, **RustBelt**). A contribuição de DLang é empacotar essas técnicas para que os casos comuns precisem de muito menos anotações, apoiando-se em semântica de valor e regiões lexicais explícitas.

## As garantias, em resumo

| Bug | Antes | Agora |
|---|---|---|
| use-after-free | compila → crash em runtime | **erro de compilação** (`E_USE_AFTER_MOVE`) |
| liberação dupla | compila → abort em runtime | **erro de compilação** (`E_USE_AFTER_MOVE`) |
| pendente em grafo liberado | compila → segfault | **erro de compilação** (`E_REGION_ESCAPE`) |
| empréstimo sobrevivendo à chamada | — | **erro de compilação** (`E_REF_ESCAPES`) |
| empréstimos mutáveis com alias | — | **erro de compilação** (`E_EXCLUSIVITY`) |
| liberação de recurso | manual, fácil de esquecer | **automática** via `deinit`, exatamente uma vez |
| custo em runtime da segurança | — | **zero** — inteiramente estático |

## Relacionados

- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Coleta de Lixo Automática](14-garbage-collection.md)
- [Construtores e Destrutores](21-constructors-and-destructors.md)
- [Ponteiros e Referências](12-pointers-and-references.md)

[← Índice](README.md)
