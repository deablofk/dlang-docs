# Programação Assíncrona (async/await)

> Status: Ausente como sintaxe.

DLang não tem palavra-chave `async` nem `await`. A programação assíncrona é totalmente suportada, mas é obtida inteiramente pelo modelo de concorrência library-first — corrotinas stackful, promises, canais e um executor explícito — em vez de sintaxe dedicada.

## Não existe `async`/`await`

Em muitas linguagens, `async` marca uma função como suspensível e `await` a suspende até um resultado estar pronto. DLang omite ambos de propósito. Os mesmos resultados são expressos com chamadas de biblioteca comuns já descritas em outros tópicos:

- **Suspensão e retomada** vêm de corrotinas stackful: `Corrotina.retomar` e `Corrotina.ceder` (yield). Ver [Corrotinas e Promises](42-coroutines-and-promises.md).
- **Esperar por um resultado** é `Promise(T).aguardar`, que cede cooperativamente até a promessa resolver — exatamente o comportamento que uma expressão `await` fornece, mas como uma chamada de método comum.
- **Escalonamento** é um `Executor` explícito, o "alocador da concorrência". Ver [Multithreading e Concorrência](41-concurrency.md).
- **Comunicação** entre tarefas concorrentes é feita com `Canal(T)`. Ver [Canais e Passagem de Mensagens](44-channels.md).

Uma "tarefa que aguarda um valor" é simplesmente uma corrotina que chama `aguardar` em uma promise:

```dlang
// sem 'async' na função, sem expressão 'await' — só chamadas de biblioteca
buscarUsuario :: (eu: Ptr(Corrotina), p: Ptr(Promise(string))) {
  val nome = p.value.aguardar(eu)   // cede cooperativamente até resolver
  println("recebido: ${nome}")
}
```

## Por que está ausente

O par de palavras-chave async/await é deixado de fora por três razões que se reforçam:

1. **Evita a coloração de funções.** Com `async`/`await`, a cor de uma função (síncrona vs. assíncrona) vaza para todo chamador e força uma cópia "colorida" paralela de boa parte do ecossistema. Como as corrotinas de DLang são stackful, qualquer função pode ceder de qualquer lugar; não há cor para propagar.
2. **Mantém o compilador minúsculo.** Toda a história de concorrência se apoia em um intrínseco de troca de contexto mais alguns atômicos (ver [Corrotinas e Promises](42-coroutines-and-promises.md)). Adicionar `async`/`await` significaria uma transformação em máquina de estados e novas regras de tipo embutidas no compilador, para um comportamento que a biblioteca já entrega.
3. **Mantém o custo explícito.** Com o modelo de biblioteca você vê o alocador, a pilha de 64 KB da corrotina e o executor que a agenda. Uma palavra-chave que conjura máquinas de estado escondidas e um runtime implícito esconderia exatamente os custos que uma linguagem de sistema precisa manter visíveis.

## Por quê

Async/await é açúcar sintático conveniente para uma ideia — suspensão cooperativa esperando por um resultado — que DLang já expressa com valores: corrotinas, promises, canais e um executor explícito. Escolher a forma de biblioteca mantém as funções sem cor, o compilador pequeno e cada custo na página. A feature está "ausente como sintaxe" precisamente *porque* a capacidade está totalmente presente como biblioteca.

## Relacionados

- [Corrotinas e Promises](42-coroutines-and-promises.md)
- [Multithreading e Concorrência](41-concurrency.md)
- [Canais e Passagem de Mensagens](44-channels.md)

[← Índice](README.md)
