# Canais e Passagem de Mensagens

Um `Channel(T)` dá comunicação no estilo CSP (estilo Go): threads coordenam
**movendo valores** através do canal em vez de compartilhar memória. `send` move um
`T` para fora do produtor; `recv` move-o para dentro do consumidor — sem estado
mutável compartilhado, apenas a posse passada através da fronteira de thread
(SPEC §23.5). Tipos de elemento afins (ex.: `Channel(List(int))`) movem-se de
forma limpa, já que nada é jamais aliasado.

Um canal é um handle proprietário contado por referência atomicamente: `make()`
o cria, `clone()` cria outro handle para o mesmo canal, e o último handle a ser
destruído o libera.

## Enviar e receber

```dlang
val channel = import("std/concurrency/channel")
inline import("std/concurrency/task")

produce :: (sink tx: channel.Channel(int), n: int) -> int {
  var i: int = 1
  while (i <= n) { tx.send(i)  i = i + 1 }
  return n
}

main :: () -> int {
  val ch: channel.Channel(int) = channel.Channel(int).make()
  val tx: channel.Channel(int) = ch.clone()
  val t: Task(int) = spawn produce(tx, 100)    // tx movido para o worker
  var sum: int = 0
  var i: int = 0
  while (i < 100) { sum = sum + ch.recv()  i = i + 1 }   // recv MOVE cada valor para fora
  await t
  println(sum)                                  // 5050
  return 0
}
```

`recv()` bloqueia numa variável de condição até um item estar disponível, então o
move para fora. O `recv()` simples assume que o consumidor sabe quantos itens
esperar — ele bloquearia para sempre num canal fechado e vazio. Para canais que
são fechados, use as formas cientes de fechamento abaixo.

## Fechando um canal

`close()` sinaliza o fim do fluxo e acorda todo receptor bloqueado. Um `send` num
canal fechado descarta seu valor e não enfileira nada.

Como um `T` afim não tem um "zero" para devolver no caso vazio, os `recv` cientes
de fechamento devolvem um **`ChanItem(T)`** — um opcional proprietário seguro para
movimento, que ou contém o item retirado ou está vazio porque o canal está
fechado:

```dlang
consume :: (sink rx: channel.Channel(int)) -> int {
  var total: int = 0
  var live: boolean = true
  while (live) {
    var it: channel.ChanItem(int) = rx.recvOrClosed()   // bloqueia até item ou fechado
    if (it.present()) {
      total = total + it.take()      // MOVE o item para fora
    } else {
      live = false                   // canal fechado e drenado
    }
  }
  return total
}
```

- `recvOrClosed()` bloqueia até um item estar disponível **ou** o canal estar
  fechado e drenado.
- `tryRecv()` é a forma não bloqueante (retorna imediatamente; `isClosed()`
  distingue "fechado" de "vazio agora").
- `it.present()` → `it.take()` move o item para fora; caso contrário o canal
  terminou.

O produtor fecha quando termina:

```dlang
producer :: (sink tx: channel.Channel(int), n: int) -> int {
  var i: int = 1
  while (i <= n) { tx.send(i)  i = i + 1 }
  tx.close()
  return n
}
```

## Selecionando entre canais

`selectRecv2(a, b)` bloqueia até qualquer um de dois canais ter um item (ou ambos
estarem fechados e drenados). É um select bloqueante de verdade — o selecionador
registra um único waiter compartilhado com ambos os canais e dorme sobre ele, em
vez de fazer spin. Ele recebe seus handles por `sink`, então passe clones para
continuar selecionando:

```dlang
var sel: channel.Selected(int) = channel.Channel(int).selectRecv2(ca.clone(), cb.clone())
if (sel.which == -1) {
  // ambos os canais fechados e drenados
} else {
  use(sel.which, sel.item.take())   // which = 0 (a) ou 1 (b)
}
```

Para um número **dinâmico** de canais, `SelectSet(T)` é a generalização N-ária:
construa-o uma vez, depois faça `recv()` num laço.

```dlang
var set: channel.SelectSet(int) = channel.SelectSet(int).of()
set.add(a.clone()); set.add(b.clone()); set.add(c.clone())
var live: boolean = true
while (live) {
  var r: channel.Selected(int) = set.recv()
  if (r.which == -1) { live = false }        // todos os canais fechados
  else { use(r.which, r.item.take()) }        // which = ordem de adição (base 0)
}
```

`SelectSet` possui um único waiter compartilhado e inscreve cada canal uma vez,
então o laço não aloca nenhuma condvar por chamada; `deinit` cancela as inscrições
e destrói os clones.

## Relacionados

- [Multithreading e Concorrência](41-concurrency.md)
- [Concorrência Estruturada — Tasks e Futures](42-coroutines-and-promises.md)
- [spawn / await](43-async-await.md)

[← Índice](README.md)
