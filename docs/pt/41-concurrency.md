# Multithreading e Concorrência

A concorrência de DLang é **livre de corrida de dados por construção**. Uma
corrida de dados exige duas threads com *acesso mutável aliasado* ao mesmo dado.
Sob a Semântica de Valores Mutáveis (MVS) não há aliasing — um valor entregue a
outra thread é **copiado ou movido, nunca compartilhado** — então o ingrediente
que uma corrida exige simplesmente não existe. Este é o modelo de concorrência de
Hylo, e DLang o herda; o papel do compilador é transformar isso, de um acaso de
como os closures capturam, numa garantia **verificada**. A especificação completa
está em SPEC §23.

Os primitivos são código comum da biblioteca padrão (`std/concurrency/*.dlang`)
sobre pthreads reais. Nada é escondido: não há runtime de fundo nem escalonador
global.

## Threads do SO — `Thread`

`Thread.start` executa um closure numa nova thread do SO e devolve um handle;
`join` espera por ela, `detach` deixa-a rodar sem dono.

```dlang
inline import("std/concurrency/thread")

work :: () -> () = { println("running on another thread") }

main :: () -> int {
  val t: Thread = Thread.start(work)
  t.join()                     // espera terminar
  return 0
}
```

O parâmetro do corpo é declarado `sending` (veja abaixo), que é o que submete
suas capturas à verificação de segurança.

## O que pode cruzar uma thread — a send-check

Um closure entregue a uma thread captura **por valor**. Se uma captura pode
cruzar a fronteira é decidido em tempo de compilação, em toda build:

- **Valores copiáveis e sem `deinit`** (`int`, uma view genuinamente copiável) são
  enviados por **snapshot** — cada thread recebe sua própria cópia independente.
- Um **valor afim próprio** (um local, ou um parâmetro `sink`/`sending`) é enviado
  por **movimento**: a thread assume a posse e o escopo externo a abre mão. Um uso
  posterior no escopo externo é `E_USE_AFTER_MOVE`.
- Um **valor afim emprestado** (um parâmetro `borrow`/`inout`) ou uma **projeção**
  **não é enviável** — você não pode mover o que não possui, e uma captura por
  valor aliasaria o buffer do chamador: `E_NOT_SENDABLE`.

```dlang
spawnList :: (xs: List(int)) -> () {     // xs é um BORROW
  worker :: () -> () = { println(xs.size()) }
  val t = Thread.start(worker)           // E_NOT_SENDABLE — 'xs' é emprestado
  t.join()
}
```

Para mover um valor próprio para dentro da thread, possua-o (um local, ou receba
`sink`):

```dlang
consume :: (sink xs: List(int)) -> () {
  worker :: () -> () = { println(xs.size()) }   // xs MOVIDO para a thread
  val t = Thread.start(worker)
  t.join()
  // usar xs aqui seria E_USE_AFTER_MOVE — a thread é dona dele agora
}
```

O dono movido para dentro é recuperado pelo corpo da thread quando ela termina —
sem vazamento, com o alocador balanceado.

## A fronteira geral — parâmetros `sending`

A send-check **não é especial a `Thread.start`**. Qualquer API que receba um
closure para outra thread adere declarando um parâmetro **`sending`**, e todo
argumento passado a ele recebe o mesmo tratamento (capturas Sendable, capturas
próprias movidas para dentro). `Thread.start` e `Task.start` são apenas APIs que
declaram `sending body` — o compilador não tem conhecimento embutido delas.

```dlang
// uma API de thread definida pelo usuário — 'work' recebe a send-check em cada chamada
runAsync :: (sending work: () -> int) -> Task(int) {
  return spawn work()
}
```

`sending` transfere a posse como `sink` (passado por valor, consumido na chamada);
ele apenas adiciona a verificação de cruzamento de thread.

## Estado mutável compartilhado — `Mutex(T)`

A MVS torna impossível o estado mutável compartilhado casual, então `Mutex(T)` é o
*único* lugar sancionado onde ele vive. É um handle proprietário, contado por
referência atomicamente, sobre um `T` protegido por trava. `clone()` cria outro
handle para o **mesmo** valor guardado; mova um clone para cada worker; o último
handle a ser destruído libera tudo.

```dlang
inline import("std/concurrency/task")     // Task nu para `spawn`
val mutex = import("std/concurrency/mutex")

bump :: (sink m: mutex.Mutex(int), n: int) -> int {
  var i: int = 0
  while (i < n) { m.update((x: int) -> int = x + 1)  i = i + 1 }
  return n              // spawn precisa de um corpo que produz valor
}

shared :: () -> int {
  val counter: mutex.Mutex(int) = mutex.Mutex(int).of(0)
  val c1: mutex.Mutex(int) = counter.clone()      // um segundo handle
  val t: Task(int) = spawn bump(c1, 1000)         // c1 movido para o worker
  val here: int = bump(counter.clone(), 1000)
  await t
  return counter.get()                            // 2000
}
```

`update(f)` trava, substitui o valor por `f(value)` e destrava — a trava é o token
de exclusividade, então a Lei da Exclusividade se estende *entre* threads através
dela. `get()` lê uma cópia sob a trava.

## Contadores sem trava — `Atomic`

`Atomic` é um handle proprietário sobre uma célula de 4 bytes no heap, dirigida
pelas instruções atômicas sequencialmente consistentes do hardware. É o primitivo
de contagem de referências sob `Shared`/`Mutex`/`Channel`, e um contador autônomo
por si só.

```dlang
val atom = import("std/concurrency/atomic")

var a: atom.Atomic = atom.Atomic.of(0)
val old: int = a.fetchAdd(1)     // devolve o valor ANTES da soma
val now: int = a.subFetch(1)     // devolve o valor DEPOIS da subtração
println(a.load())
```

O compilador linka `libatomic` automaticamente sempre que um programa usa essas
operações — sem necessidade de flag.

## Compartilhamento contado por referência — `Shared(T)`

`Shared(T)` é um **Arc**: um handle contado por referência atomicamente para
compartilhar um valor imutável entre threads. `clone()` é um incremento de
contagem sem trava; a última destruição libera.

```dlang
inline import("std/concurrency/task")     // Task nu para `spawn`
val shared = import("std/concurrency/shared")

val cfg: shared.Shared(int) = shared.Shared(int).of(42)
val c1: shared.Shared(int) = cfg.clone()
val t: Task(int) = spawn readConfig(c1)   // c1 movido para o worker
println(cfg.get())                         // 42
await t
```

Use `Shared` para estado *imutável* compartilhado; use `Mutex` quando o valor
compartilhado precisa ser mutado.

## Importando os módulos de concorrência

Duas regras cobrem todos os casos:

- **`spawn` precisa de `task` inline** — `inline import("std/concurrency/task")`.
  A palavra-chave `spawn` expande para `Task(T).start(…)`, que nomeia `Task` nu,
  então o módulo `task` precisa ser importado com `inline` (isso também dá acesso
  a `Thread`).
- **Importe todo o resto por prefixo de binding** —
  `val ch = import("std/concurrency/channel")`, `val mutex = import(…)`, etc.
  Esses módulos compartilham dependências internas de `thread`/`atomic` que
  colidiriam no espaço de nomes plano sob `inline import`.

```dlang
inline import("std/concurrency/task")        // Task, spawn/await, Thread
val mutex   = import("std/concurrency/mutex")
val channel = import("std/concurrency/channel")
```

## Relacionados

- [Concorrência Estruturada — Tasks e Futures](42-coroutines-and-promises.md)
- [spawn / await](43-async-await.md)
- [Canais e Passagem de Mensagens](44-channels.md)
- [Segurança de Memória](14a-memory-safety.md)

[← Índice](README.md)
