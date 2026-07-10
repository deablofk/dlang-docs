# Gerenciamento de Memória Manual

DLang nunca aloca memória na heap pelas suas costas. Quando você quer memória que sobreviva ao quadro de pilha atual, você a pede explicitamente com `New(T)`, e a devolve explicitamente com `_alloc.free(...)`. Não há coletor de lixo: os tempos de vida são seus para gerenciar.

O que torna isso ergonômico em vez de tedioso é que a alocação é **ambiente** — toda alocação vem do *alocador atual*, um valor trocável mantido em um contexto por-programa. Você não passa um alocador por cada função; você o define uma vez (ou aceita o padrão) e tudo abaixo o utiliza. Esse é o modelo popularizado por Jai, e é detalhado em [Alocação Dinâmica](18-dynamic-allocation.md).

## Alocando um valor tipado

`New(T)` reserva exatamente a memória necessária para um `T` e retorna um `Ptr(T)` para ela. Como é um ponteiro para dados, você acessa o conteúdo através de `.value` (veja [Ponteiros e Referências](12-pointers-and-references.md)).

```dlang
val pessoaPtr: Ptr(Pessoa) = New(Pessoa)
pessoaPtr.value.nome = "Gabriel"   // altera um campo dentro do struct
```

O compilador conhece o tamanho exato de `Pessoa`, então reserva precisamente aquela quantidade de bytes — nem mais. Para um bloco de `n` valores, use `New(T, n)`, que retorna um `Ptr(T)` para `n` posições contíguas indexadas com `p[i]`.

Por baixo dos panos, `New(T)` é a escrita de alto nível da primitiva de baixo nível `_alloc.alloc(T)`; ambas alocam através do alocador atual, então são intercambiáveis. `New` lê melhor em código comum.

## Liberando com `defer`

A memória que você aloca precisa ser devolvida. O padrão idiomático é parear cada alocação com um `defer _alloc.free(...)`, colocado logo depois dela. `defer` agenda a liberação para rodar quando a função encerra, não importa por qual caminho.

```dlang
criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = New(Pessoa)
  defer _alloc.free(cast(Ptr(byte), inimigo))   // devolvida ao fim da função

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

Colocar o `defer` logo abaixo da alocação torna vazamentos fáceis de auditar: cada alocação tem sua liberação correspondente visível uma linha abaixo, e `defer` garante que ela rode mesmo em retornos antecipados ou erros. Liberar é *explícito* — a linguagem nunca libera por você, mas também nunca impede você de escolher exatamente quando um tempo de vida termina.

## De onde vem a memória

`New` não fixa o `malloc` da libc. Ele chama qualquer alocador atualmente instalado no contexto. Por padrão esse é o alocador baseado em malloc, então o exemplo acima se comporta como um `malloc`/`free` clássico. Mas você pode trocar o alocador para uma região de código — por exemplo, para um **alocador de depuração** que rastreia cada bloco vivo e reporta liberações duplas e vazamentos enquanto você desenvolve:

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))
// ... alocações aqui são rastreadas ...
debugReport(context().value)   // alocações / liberações / vazadas / erros
popAllocator(prev)
```

Toda alocação entre o push e o pop — incluindo as implícitas dentro de `string`, `List` e `Map` — flui pelo alocador instalado. Veja [Alocação Dinâmica](18-dynamic-allocation.md) para a API completa de alocadores.

## Justificativa de design

Memória manual é o padrão porque uma linguagem de sistemas deve oferecer controle previsível e de custo zero sobre a heap. Rotear a alocação por um alocador visível e trocável significa que não há alocação surpresa *e* não há cerimônia: você lê `New(T)` e sabe que uma alocação na heap acontece, e pode redirecionar tudo — o seu e o da biblioteca padrão — instalando um alocador diferente, sem reescrever uma única chamada. Parear alocação com `defer free` torna o gerenciamento de tempo de vida um padrão local e visível; e rotear derreferenciações por `.value` mantém cada acesso à memória explícito.

## Relacionados

- [Ponteiros e Referências](12-pointers-and-references.md)
- [Coleta de Lixo](14-garbage-collection.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)

[← Índice](README.md)
