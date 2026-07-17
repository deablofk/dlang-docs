# Concorrência Estruturada — Tasks e Futures

DLang **não tem corrotinas com pilha nem um tipo `Promise`**. Sua resposta para
"computar um valor em outra thread e coletá-lo depois" é `Task(T)`, um future
**estruturado**: é um handle proprietário cujo tempo de vida está atado a um
escopo, e que não pode sobreviver ao escopo que o criou. É a mesma disciplina de
MVS que o resto da linguagem usa, aplicada à concorrência (SPEC §23.4).

Esta página descreve o tipo `Task(T)`; a superfície `spawn`/`await` que o dirige
está em [spawn / await](43-async-await.md).

## `Task(T)` — um future juntável

Um `Task(T)` representa um worker computando um `T`. É um handle proprietário
`nocopy` com um `deinit` que faz o **join** do worker — então uma task é
*sincronizada por construção*:

- `await t` faz o join do worker e **move** o resultado `T` para fora.
- Se uma task nunca é aguardada, seu `deinit` ainda assim faz o join do worker na
  saída do escopo (o resultado é computado e então descartado). Uma task nunca
  pode ser abandonada silenciosamente enquanto sua thread continua.

```dlang
inline import("std/concurrency/task")

sumTo :: (n: int) -> int {
  var s: int = 0
  var i: int = 1
  while (i <= n) { s = s + i  i = i + 1 }
  return s
}

main :: () -> int {
  val a: Task(int) = spawn sumTo(100)   // roda num worker
  val b: Task(int) = spawn sumTo(10)
  println(await a + await b)            // 5050 + 55, computados concorrentemente
  return 0
}
```

## Por que estruturada (sem futures desacoplados)

Como `Task(T)` é afim e seu `deinit` faz o join, o worker está garantido a
terminar dentro do escopo que o criou. Não há como vazar uma thread em execução
nem ler um resultado antes de estar pronto — o sistema de tipos força o join. É
isto que "concorrência estruturada" significa: a concorrência aninha como os
escopos aninham.

```dlang
withResults :: () -> int {
  val t: Task(int) = spawn sumTo(1000)
  // ... outro trabalho, concorrente com a task ...
  return await t          // garantidamente juntado aqui
}                         // (se não tivéssemos aguardado, o deinit faria o join aqui)
```

## Resultados afins movem-se de forma limpa

Uma task pode produzir um valor próprio — o resultado é **movido** para fora do
worker no `await`, nunca copiado nem compartilhado:

```dlang
buildList :: (n: int) -> List(int) {
  var xs: List(int) = List(int).empty()
  var i: int = 0
  while (i < n) { xs.add(i)  i = i + 1 }
  return xs
}

main :: () -> int {
  val t: Task(List(int)) = spawn buildList(6)
  var xs: List(int) = await t      // a List é MOVIDA para fora do worker
  println(xs.size())               // 6
  return 0
}
```

## Justificativa de projeto

- **Sem coloração de funções.** `spawn`/`await` são expressões comuns, não um
  modificador `async` contagioso. Qualquer função pode ser lançada; nada numa
  assinatura precisa mudar.
- **Sem runtime escondido.** Uma `Task` é uma thread do SO (pthreads reais),
  criada quando você faz `spawn` e juntada quando você faz `await` ou quando o
  handle é destruído. Não há escalonador rodando por trás.
- **Segurança de graça.** Como um closure lançado passa pela mesma
  [send-check e move-in](41-concurrency.md) de qualquer corpo de thread, uma task
  não pode capturar um dono emprestado nem compartilhar estado mutável por acaso.

## Relacionados

- [spawn / await](43-async-await.md)
- [Multithreading e Concorrência](41-concurrency.md)
- [Canais e Passagem de Mensagens](44-channels.md)

[← Índice](README.md)
