# Coleta de Lixo Automática

DLang **não tem coletor de lixo**, e isso é uma decisão de design deliberada, não uma funcionalidade faltando. Uma linguagem de sistemas deve tornar o custo da memória visível e previsível; um coletor em segundo plano que pode pausar seu programa em um momento imprevisível é o oposto disso. Memória em DLang é explícita: você aloca com `New(T)` e libera com `Undo(p)` (veja [Gerenciamento de Memória Manual](13-manual-memory.md)).

O que DLang oferece *no lugar* da coleta automática é um jeito de tornar a memória manual ao mesmo tempo conveniente e verificável: o **alocador de contexto**.

## O alocador de contexto trocável

Toda alocação — `New(T)`, e cada alocação implícita dentro de `string`, `List` e `Map` — vem do *alocador atual*, um valor mantido em um contexto por-programa. O padrão é um alocador simples baseado em `malloc` da libc, mas você pode instalar outro para uma região de código com `pushAllocator` / `popAllocator`. É isso que substitui o "qual GC gerencia este objeto": você decide *como* a memória é gerenciada escolhendo o alocador, não esperando que um coletor limpe depois.

```dlang
val prev: Allocator = pushAllocator(meuAlocador)
// ... toda alocação aqui usa meuAlocador ...
popAllocator(prev)
```

Como a escolha vive no nível do alocador, a estratégia de memória de um subsistema inteiro pode mudar sem tocar em um único ponto de alocação.

## Pegando vazamentos e liberações duplas

A conveniência que um GC normalmente vende — "você não vai vazar" — DLang fornece como uma ferramenta de *verificação* opcional, e não como um imposto de tempo de execução. `debugAllocator` envolve qualquer alocador de base, registra cada bloco vivo e reporta liberações duplas ou inválidas na hora que acontecem; `debugReport` lista o que ainda está vivo (vazado) ao final.

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))

val a: Ptr(int) = New(int)
Undo(a)
Undo(a)   // -> reportado: liberação inválida ou dupla

debugReport(context().value)      // -> alocações / liberações / vazadas / erros
popAllocator(prev)
```

Você instala o alocador de depuração enquanto desenvolve para pegar erros, e simplesmente não o instala em uma build de release — então as verificações custam exatamente nada quando você publica. É a abordagem "copiloto, não imposto": a ferramenta ajuda a achar bugs sem impor um custo permanente de execução.

## Segurança de memória estática (em tempo de compilação, custo zero)

O alocador de depuração pega as *suas* liberações duplas e vazamentos durante o desenvolvimento, mas não impede um ponteiro pendente, e é uma ferramenta de runtime. Além dele, DLang está ganhando um **modelo de segurança de memória estática**: use-after-free, liberação dupla e uso-após-move viram **erros de compilação** — rejeitados antes de o programa poder rodar, com **custo zero em runtime** em builds de release. `Ptr(T)` cru + `Undo` continua como uma válvula de escape explícita, mas os idiomas seguros tornam classes inteiras de bug *impossíveis de expressar* em vez de apenas detectáveis.

O modelo é um híbrido em camadas:

- **Tipos `nocopy`** são *afins*: movidos, não copiados. Usar um depois de ele ter sido consumido — ou liberá-lo duas vezes — é erro de compilação, e seu destrutor (`deinit`) roda automaticamente, exatamente uma vez, no último uso.
- **Convenções de parâmetro** (`borrow` / `sink` / `inout`) dizem se uma chamada consome um valor ou apenas o empresta, para você poder passar um recurso a um leitor sem abrir mão dele.
- **Blocos `region { … }`** são arenas lexicais: aloque um grafo inteiro — mesmo cíclico — dentro de uma região e ele é liberado em bloco no fim, com uma verificação estática de que nenhum ponteiro escapa da região.

Veja **[Segurança de Memória](14a-memory-safety.md)** para o modelo completo, com exemplos antes/depois.

## Por que sem coletor

A maioria das linguagens com coleta de lixo faz do GC o ar que você respira: toda alocação é oculta e gerenciada, e você não pode optar por sair. DLang inverte isso. A alocação é sempre explícita, e o alocador que você instala decide a estratégia. Isso mantém o caminho comum livre da sobrecarga e das pausas do coletor, enquanto o contexto trocável e o alocador de depuração recuperam a maior parte da ergonomia pela qual um GC é valorizado — redirecionar a memória de um subsistema e encontrar vazamentos — sem abrir mão da previsibilidade.

## Relacionados

- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Ponteiros e Referências](12-pointers-and-references.md)

[← Índice](README.md)
