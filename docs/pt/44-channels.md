# Canais e Passagem de Mensagens

Um canal em DLang é uma struct genérica da biblioteca padrão — **zero envolvimento do compilador**. Ele dá comunicação no estilo CSP (estilo Go): corrotinas e threads se coordenam passando *mensagens* em vez de compartilhar memória. Um canal é construído inteiramente a partir de peças que você já viu: um `Mutex`, uma lista de buffer e cooperação com o `Executor` (ver [Multithreading e Concorrência](41-concurrency.md)).

## A struct do canal

`Canal(T)` é uma struct genérica sobre um buffer, uma capacidade, uma trava e uma flag de fechado. Capacidade `0` significa um canal de rendezvous sem buffer; capacidade positiva significa um canal bufferizado.

```dlang
Canal(T) :: struct {
  buffer: List(T)
  capacidade: int     // 0 = sem buffer (rendezvous); >0 = bufferizado
  trava: Mutex
  fechado: boolean
}

Canal(T).criar :: (alloc: Allocator, capacidade: int) -> Ptr(Canal(T)) { ... }
```

## Enviar e receber

As duas pontas se coordenam pelo mesmo mecanismo cooperativo: quando uma operação não pode prosseguir, ela **cede a corrotina** em vez de bloquear a thread do SO, devolvendo o controle ao escalonador. `enviar` cede enquanto o buffer está cheio; `receber` cede enquanto está vazio (e o canal ainda está aberto).

```dlang
// enviar: bloqueia CEDENDO a corrotina se o buffer estiver cheio
Canal(T).enviar :: (eu: Ptr(Corrotina), valor: T) {
  _.trava.travar()
  defer _.trava.destravar()
  while (_.buffer.tamanho >= _.capacidade) eu.value.ceder()
  _.buffer.add(valor)
}

// receber: devolve (valor, ok). ok=false quando o canal foi fechado e esvaziou.
Canal(T).receber :: (eu: Ptr(Corrotina)) -> (T, boolean) {
  _.trava.travar()
  defer _.trava.destravar()
  while (_.buffer.tamanho == 0 && !_.fechado) eu.value.ceder()
  if (_.buffer.tamanho == 0) return (zero(T), false)   // fechado e vazio
  return (_.buffer.removerPrimeiro(), true)
}

Canal(T).fechar :: () { _.fechado = true }
```

O retorno `(valor, ok)` é uma tupla comum (ver [Tuplas e Desestruturação](38-tuples-and-destructuring.md)): `ok` é `false` exatamente quando o canal está fechado e vazio, o que é o sinal para um consumidor parar.

## Produtor / consumidor

Um produtor agenda uma corrotina que envia alguns valores e então fecha o canal; um consumidor agenda outra que lê até o canal fechar, desestruturando a tupla `(v, ok)` a cada vez. `euMesmo()` é um helper da std lib que devolve a corrotina atual.

```dlang
exemploCanal :: (exec: Ptr(Executor)) {
  val canal = Canal(int).criar(_alloc, 8)

  // produtor
  exec.value.agendar(Corrotina.criar(_alloc, {
    var i = 0
    while (i < 5) { canal.value.enviar(euMesmo(), i); i++ }
    canal.value.fechar()
  }))

  // consumidor: lê até o canal fechar, desestruturando a tupla (v, ok)
  exec.value.agendar(Corrotina.criar(_alloc, {
    while (true) {
      val (v, ok) = canal.value.receber(euMesmo())
      if (!ok) break
      println("recebido: ${v}")
    }
  }))
}
```

## `select` é uma função de biblioteca, não sintaxe

Esperar em vários canais ao mesmo tempo — o `select` do Go — **não** é uma construção do compilador em DLang. É uma função da biblioteca padrão (ou macro; ver [Macros e Expansão de Código](46-macros.md)). Isso é coerente com a regra da linguagem de que *comportamento é açúcar sobre dados*: o controle sobre múltiplos canais é expresso por código de biblioteca comum, não por uma nova palavra-chave.

## Por quê

Canais dão coordenação segura sem malabarismo manual de locks, mas não exigem nada do compilador: `Canal(T)` é uma struct genérica em camadas sobre um `Mutex` e o escalonamento cooperativo do executor. Manter até o `select` na biblioteca, em vez da gramática, sustenta a regra de que a superfície de DLang permanece pequena e sua concorrência permanece auditável — cada envio, recebimento e espera é código simples que você pode ler.

## Relacionados

- [Corrotinas e Promises](42-coroutines-and-promises.md)
- [Multithreading e Concorrência](41-concurrency.md)
- [Programação Assíncrona (async/await)](43-async-await.md)
- [Tuplas e Desestruturação](38-tuples-and-destructuring.md)

[← Índice](README.md)
