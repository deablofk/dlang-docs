# Corrotinas e Promises

Corrotinas e promises em DLang são **tipos da biblioteca padrão, não sintaxe da linguagem**. Não há palavra-chave `async`/`await` nem coloração de funções. O modelo é library-first: corrotinas stackful, promises e canais são todos `.dlang` comum, e o compilador expõe exatamente um intrínseco de baixo nível — uma troca de contexto — sobre o qual todo o resto é construído.

Esta página se constrói diretamente sobre os primitivos de threading em [Multithreading e Concorrência](41-concurrency.md).

## Os intrínsecos, via `@intrinsic`

Não há namespace mágico do compilador. O módulo de concorrência declara três funções sem corpo e as marca com `@intrinsic("id")`; o compilador reconhece o id e injeta a implementação de baixo nível. É o mesmo sistema de anotações usado pelos atômicos (ver [Multithreading e Concorrência](41-concurrency.md)) e por macros e reflexão (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)). Um usuário comum nunca escreve isto — só o módulo de concorrência.

```dlang
// 1. Contexto: struct OPACA cujo layout (registradores + ponteiro de pilha +
//    ponteiro de instrução) é preenchido pelo compilador por plataforma.
@intrinsic("contexto.tipo")
Contexto :: struct {}

// 2. Inicializa 'ctx' para, ao ser retomado, executar 'entrada' sobre 'pilha'.
//    A PILHA É MEMÓRIA QUE VOCÊ ALOCA -> custo explícito.
@intrinsic("contexto.criar")
criarContexto :: (ctx: Ptr(Contexto), pilha: []byte, entrada: () -> ())

// 3. Salva o contexto atual em 'de' e retoma 'para'. Quem chama "congela aqui"
//    e só volta quando alguém trocar de volta para 'de'. É a troca de fibra.
@intrinsic("contexto.trocar")
trocarContexto :: (de: Ptr(Contexto), para: Ptr(Contexto))
```

O ponto crucial: a **chamada continua normal**: você escreve `trocarContexto(...)` como qualquer função. Só a *declaração* carrega a anotação — migrar de um namespace para uma anotação nunca tocou no código do usuário.

## Corrotinas são stackful

Cada corrotina tem sua própria pilha, e essa pilha é memória que você aloca com um **alocador explícito**. Uma pilha de 64 KB é uma linha de código visível, não um custo escondido. Como a pilha é real, uma corrotina pode ceder de qualquer lugar — não há necessidade de "colorir" funções como assíncronas.

```dlang
Corrotina :: struct {
  ctx: Contexto             // estado da própria corrotina
  retorno: Ptr(Contexto)    // pra onde voltar quando der 'yield'
  pilha: []byte             // pilha dela, alocada explicitamente
  terminada: boolean
}

// criar: a pilha é alocada COM ALOCADOR EXPLÍCITO (custo visível)
Corrotina.criar :: (alloc: Allocator, corpo: () -> ()) -> Ptr(Corrotina) {
  val c: Ptr(Corrotina) = alloc.alloc(Corrotina)
  c.value.pilha = alloc.allocBytes(64 * 1024)   // 64KB de pilha — você VÊ o custo
  c.value.terminada = false
  criarContexto(ref c.value.ctx, c.value.pilha, corpo)
  return c
}
```

Retomar e ceder são apenas duas direções da mesma troca de contexto. `retomar` congela o chamador e pula para dentro da corrotina; `ceder` (yield) congela a corrotina e volta para quem a retomou.

```dlang
// retomar: salva onde estou e pulo pra dentro da corrotina
Corrotina.retomar :: (de_onde: Ptr(Contexto)) {
  _.retorno = de_onde
  trocarContexto(de_onde, ref _.ctx)   // congela o chamador, descongela a corrotina
}

// ceder (yield, de dentro da corrotina): volto pra quem me retomou
Corrotina.ceder :: () {
  trocarContexto(ref _.ctx, _.retorno)  // congela a corrotina, descongela o chamador
}
```

## Promises são 100% biblioteca

Uma `Promise(T)` adiciona zero superfície de compilador. É só uma struct guardando um estado e um valor, resolvida por uma corrotina ou thread e lida por outra. Nenhum `async`/`await` de sintaxe está envolvido em lugar nenhum.

```dlang
EstadoPromise :: enum { Pendente, Resolvida, Rejeitada }

Promise(T) :: struct {
  estado: EstadoPromise
  valor: T
  erro: any
}

Promise(T).criar :: (alloc: Allocator) -> Ptr(Promise(T)) {
  val p: Ptr(Promise(T)) = alloc.alloc(Promise(T))
  p.value.estado = EstadoPromise.Pendente
  return p
}

// o produtor resolve a promessa
Promise(T).resolver :: (v: T) {
  _.valor = v
  _.estado = EstadoPromise.Resolvida
}
```

O consumidor espera **cedendo cooperativamente** até a promessa ser resolvida. Isso não bloqueia a thread do SO: `aguardar` devolve o controle ao escalonador e volta depois, quando o valor estiver pronto.

```dlang
// o consumidor espera CEDENDO a corrotina até resolver (cooperativo, não
// bloqueia a thread do SO — devolve o controle ao escalonador e volta depois)
Promise(T).aguardar :: (eu: Ptr(Corrotina)) -> T {
  while (_.estado == EstadoPromise.Pendente) {
    eu.value.ceder()
  }
  return _.valor
}
```

## Por quê

Corrotinas stackful mais um único intrínseco de troca de contexto dão tudo o que `async`/`await` dá — suspensão, retomada, espera por um resultado — sem dividir o mundo em funções coloridas e não coloridas e sem inchar o compilador. O custo continua explícito: você vê o alocador, vê a pilha de 64 KB, vê o executor (ver [Multithreading e Concorrência](41-concurrency.md)) que agenda o trabalho. Promises sendo structs comuns significa que a concorrência se compõe a partir de dados, exatamente como o resto da linguagem.

## Relacionados

- [Multithreading e Concorrência](41-concurrency.md)
- [Programação Assíncrona (async/await)](43-async-await.md)
- [Canais e Passagem de Mensagens](44-channels.md)
- [Gerenciamento de memória manual](13-manual-memory.md)

[← Índice](README.md)
