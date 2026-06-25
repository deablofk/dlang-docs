# Alocação Dinâmica

A alocação dinâmica reserva memória na heap em tempo de execução, para dados cujo tamanho ou tempo de vida não é conhecido em tempo de compilação. Em DLang toda alocação na heap passa por um **alocador explícito** — não há `new` oculto, nem boxing implícito. Você sempre pode apontar para o alocador que produziu um pedaço de memória, e você é responsável por devolvê-lo. A instrução `defer` torna essa limpeza confiável.

## Alocando uma única struct

Para colocar uma struct na heap, chame `alloc(Tipo)` em um alocador. O alocador manual padrão é `_alloc`. Ele retorna um `Ptr(Tipo)` — um ponteiro cujo valor você alcança através de `.value`:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
}

criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = _alloc.alloc(Pessoa)
  defer _alloc.free(inimigo)

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

O compilador reserva exatamente o tamanho de `Pessoa` na heap. O `defer _alloc.free(inimigo)` agenda a liberação correspondente para rodar quando a função terminar, não importa como ela termine — esse é o idioma que mantém alocação e desalocação visivelmente pareadas no mesmo lugar do código. O acesso a campos passa por `.value` (por exemplo `inimigo.value.nome`), que é o único ponto centralizado onde o compilador pode inserir uma verificação de segurança contra ponteiro nulo antes de você tocar nos dados. Veja [Memória manual](13-manual-memory.md) para o modelo completo de ponteiros e alocadores.

## Alocando um contêiner que cresce

Tipos de contêiner como `List(T)` também alocam seu armazenamento de apoio dinamicamente, mas envolvem a contabilidade para você. Você inicializa um entregando-lhe um alocador com `.init(_alloc)`, e o libera com `.deinit()`:

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).init(_alloc)
  defer itens.deinit()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

`List(string).init(_alloc)` cria uma lista vazia que crescerá na heap conforme você faz `add` de elementos, extraindo toda a sua memória de `_alloc`. O `defer itens.deinit()` pareado devolve essa memória quando a função termina. O mesmo ritmo `init(alocador)` / `defer deinit()` se aplica a outros contêineres de biblioteca como `Map(K, V)`.

## Escolhendo um alocador

O alocador é um parâmetro, não um padrão global embutido na linguagem. Passar `_alloc` significa que você gerencia o tempo de vida por conta própria com `free`/`deinit`. Se você preferir deixar o coletor de lixo rastrear o objeto, aloque com `_gcAlloc` em vez disso e omita o `defer free` — o GC o recupera quando ele se torna inalcançável. Essa escolha está coberta em [Coleta de lixo](14-garbage-collection.md). De qualquer forma, a decisão é explícita no ponto de alocação.

## Por quê

Rotear toda alocação na heap por um alocador visível é o cerne da filosofia de memória de DLang: a linguagem nunca aloca pelas suas costas, então o custo de qualquer pedaço de dado é sempre rastreável até um `_alloc` ou `_gcAlloc` que você pode ver. Parear cada alocação com um `defer free` (ou `defer deinit`) mantém aquisição e liberação lado a lado, o que é muito mais difícil de errar do que rastreá-las através de caminhos de `return` distantes. Centralizar o acesso a ponteiros em `.value` dá ao compilador um lugar bem definido para impor a segurança contra nulos, evitando as falhas de segmentação que atormentam C e C++. E como contêineres como `List` e `Map` são structs de biblioteca comuns que recebem um alocador, eles não precisam de suporte especial do compilador — seguem exatamente a mesma disciplina de alocador explícito que um `alloc` feito à mão.

## Relacionados

- [Memória manual](13-manual-memory.md)
- [Coleta de lixo](14-garbage-collection.md)
- [Ponteiros e referências](12-pointers-and-references.md)
- [Estruturas de dados](17-structs.md)
- [Arrays e listas](07-arrays-and-lists.md)
- [Construtores e destrutores](21-constructors-and-destructors.md)

[← Índice](README.md)
