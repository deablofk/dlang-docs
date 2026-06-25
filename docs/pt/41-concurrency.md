# Multithreading e Concorrência

DLang trata a concorrência do mesmo modo que trata a memória: como algo que a *biblioteca* fornece, não como algo que o compilador esconde. Threads do SO, mutexes e o escalonador são todos código `.dlang` comum. A única contribuição do compilador são as operações que não podem ser escritas na própria linguagem — instruções atômicas e barreiras de memória — porque elas mapeiam diretamente para o hardware.

Esta página cobre os primitivos de threading e escalonamento. A metade cooperativa da história — corrotinas, promises, canais — se constrói sobre estes e está em [Corrotinas e Promises](42-coroutines-and-promises.md) e [Canais e Passagem de Mensagens](44-channels.md).

## Os únicos intrínsecos do compilador: atômicos

Um `compare-and-swap`, uma soma atômica e uma barreira de memória não podem ser expressos com instruções normais — eles correspondem a instruções específicas da CPU. DLang os expõe pela mesma anotação `@intrinsic` usada em todo lugar: uma declaração sem corpo carrega a anotação, e o compilador injeta a implementação. O ponto de chamada é uma chamada de função perfeitamente normal.

```dlang
@intrinsic("atomic.cas")        // compare-and-swap
atomicoCAS :: (alvo: Ptr(int), esperado: int, novo: int) -> boolean

@intrinsic("atomic.add")
atomicoSomar :: (alvo: Ptr(int), delta: int) -> int

@intrinsic("atomic.fence")
barreiraMemoria :: ()
```

Note que não há um namespace mágico `atomic`. São três declarações comuns que por acaso estão marcadas com `@intrinsic` — o mesmo mecanismo que o módulo de concorrência usa para a troca de contexto (ver [Corrotinas e Promises](42-coroutines-and-promises.md)) e que a metaprogramação usa para ganchos do compilador (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)).

## Threads do SO são uma struct

Uma `Thread` é uma struct da std lib que envolve um handle opaco do SO. Seus métodos são escritos em DLang; o corpo alcança a thread real do SO via FFI (`@externo`). Criar uma thread recebe um alocador explícito e a função a executar.

```dlang
Thread :: struct {
  handle: Ptr(byte)             // handle opaco do SO
}

Thread.criar :: (alloc: Allocator, corpo: () -> ()) -> Ptr(Thread) { ... }
Thread.aguardar :: () { ... }   // join: espera a thread terminar

trabalho :: () { println("rodando em outra thread") }

usoThread :: () {
  val t = Thread.criar(_alloc, trabalho)
  defer t.value.aguardar()
}
```

`aguardar` é o join: combiná-lo com `defer` garante que a função criadora espera sua thread antes de retornar.

## Mutex: biblioteca pura sobre um atômico

Como o CAS atômico está disponível como uma chamada comum, um mutex não precisa de nenhum suporte do compilador. É uma struct que guarda um único inteiro, travada por spin em `atomicoCAS` e destravada ao limpar a flag.

```dlang
Mutex :: struct { travado: int }

Mutex.travar :: () {
  while (!atomicoCAS(ref _.travado, 0, 1)) {
    // ocupado: cede a vez (corrotina) ou faz spin (thread)
  }
}
Mutex.destravar :: () { _.travado = 0 }
```

Use-o com `defer` para que o lock seja liberado em todo caminho de saída — incluindo returns antecipados e erros:

```dlang
depositar :: (m: Ptr(Mutex), saldo: Ptr(int)) {
  m.value.travar()
  defer m.value.destravar()
  saldo.value = saldo.value + 100
}
```

## O Executor: o "alocador da concorrência"

Assim como nada aloca heap sem um `Allocator` visível, nada agenda corrotinas sem um `Executor` visível. O executor é dono da fila de trabalho e do pool de threads do SO; você passa o `_exec` de propósito, exatamente como passa o `_alloc`. **Não há runtime global escondido** — ao contrário de Go, DLang nunca inicia um escalonador pelas suas costas.

```dlang
Executor :: struct {
  fila: List(Ptr(Corrotina))
  threads: List(Ptr(Thread))
}

Executor.criar :: (alloc: Allocator, numThreads: int) -> Ptr(Executor) { ... }
Executor.agendar :: (c: Ptr(Corrotina)) { _.fila.add(c) }   // enfileira trabalho
Executor.rodar :: () { ... }   // distribui as corrotinas entre as threads

usoExecutor :: () {
  val exec = Executor.criar(_alloc, 4)        // 4 threads do SO
  defer exec.value.rodar()

  exec.value.agendar(Corrotina.criar(_alloc, { println("tarefa 1") }))
  exec.value.agendar(Corrotina.criar(_alloc, { println("tarefa 2") }))
}
```

O executor multiplexa muitas corrotinas cooperativas e baratas sobre um número pequeno de threads do SO. As corrotinas em si são explicadas em [Corrotinas e Promises](42-coroutines-and-promises.md).

## Por quê

Uma linguagem de sistema não pode enterrar a concorrência sob um runtime invisível. Ao manter `Thread`, `Mutex` e `Executor` como código de biblioteca comum e reduzir o papel do compilador a três intrínsecos atômicos, DLang mantém a implementação auditável e o custo visível. O executor espelha o alocador: tornar o escalonador um valor explícito significa que você sempre sabe o que está agendando seu trabalho e em quantas threads, sem mágica global para raciocinar.

## Relacionados

- [Corrotinas e Promises](42-coroutines-and-promises.md)
- [Programação Assíncrona (async/await)](43-async-await.md)
- [Canais e Passagem de Mensagens](44-channels.md)
- [Gerenciamento de memória manual](13-manual-memory.md)

[← Índice](README.md)
