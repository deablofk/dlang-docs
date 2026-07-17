# spawn / await

DLang expressa trabalho assíncrono com duas **palavras-chave contextuais**,
`spawn` e `await`, sobre o tipo `Task(T)`
([Concorrência Estruturada](42-coroutines-and-promises.md)). Não são um
`async`/`await` colorido no sentido de Rust/JS: não há cor de função suspensível,
nem executor para instalar, nem mudança na assinatura da função. `spawn e` executa
`e` numa thread worker; `await t` faz o join e pega o resultado.

Ambas são *contextuais* — um identificador comum chamado `spawn` ou `await` ainda
é reconhecido como tal. Elas só agem como palavras-chave quando seguidas de uma
expressão.

## `spawn e` — executar num worker

`spawn e` avalia `e` num novo worker e produz uma `Task(T)`, onde `T` é o tipo de
`e`. O tipo do elemento é **inferido**, então nenhuma anotação é necessária:

```dlang
inline import("std/concurrency/task")

val a = spawn sumTo(100)      // a : Task(int)  — inferido
val b: Task(int) = spawn sumTo(10)   // anotação opcional
```

`spawn` é uma expressão prefixa comum, então funciona em **qualquer posição**, não
só numa ligação:

```dlang
// como o receptor de await — executa e espera imediatamente
val n: int = await spawn compute(x)

// como argumento de chamada
useTask(spawn sumTo(5))

// retornado diretamente
makeTask :: () -> Task(int) = spawn sumTo(50)
```

Internamente o compilador expande `spawn e` para `Task(T).start(() -> T = e)`;
você nunca escreve isso à mão.

## `await t` — juntar e pegar o resultado

`await t` faz o join do worker de `t` e **move** o `T` computado para fora. É
escrito como uma expressão prefixa:

```dlang
val total: int = await a + await b     // ambos juntados, resultados somados
```

Aguardar é o ponto onde o resultado do worker fica disponível; antes disso, a task
está apenas rodando. Uma task que nunca é aguardada ainda é juntada quando seu
handle é destruído (concorrência estruturada — veja o capítulo 42).

## Capturas são verificadas e movidas para dentro

Como `spawn e` vira um corpo de thread, as capturas de `e` passam pela mesma
[send-check e move-in](41-concurrency.md) de qualquer closure de thread:

```dlang
listSum :: (sink xs: List(int)) -> int {
  var s: int = 0
  for (x : xs) { s = s + x }
  return s
}

main :: () -> int {
  var xs: List(int) = List(int).empty()
  xs.add(3); xs.add(4); xs.add(5)
  val s: int = await spawn listSum(xs)   // xs é MOVIDO para o worker
  // xs não pode ser usado aqui — E_USE_AFTER_MOVE
  println(s)                             // 12
  return 0
}
```

Uma captura copiável recebe snapshot; uma captura afim própria é movida para
dentro; uma captura afim emprestada é `E_NOT_SENDABLE`. Veja
[Multithreading](41-concurrency.md) para as regras completas.

## Por que não um `async`/`await` colorido?

- **Sem coloração de funções.** `spawn`/`await` são expressões, então uma função
  lançada é uma função comum — sua assinatura não muda e os chamadores não são
  forçados a virar assíncronos também.
- **Sem executor.** Uma `Task` é sustentada por uma thread do SO real; não há
  runtime para configurar ou iniciar.
- **Estruturada por padrão.** `await` (ou o handle da task sendo destruído) sempre
  faz o join, então um worker não pode sobreviver ao seu escopo.

## Relacionados

- [Concorrência Estruturada — Tasks e Futures](42-coroutines-and-promises.md)
- [Multithreading e Concorrência](41-concurrency.md)
- [Canais e Passagem de Mensagens](44-channels.md)

[← Índice](README.md)
