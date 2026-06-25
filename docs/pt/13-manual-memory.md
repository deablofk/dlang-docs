# Gerenciamento de Memória Manual

DLang nunca aloca memória na heap pelas suas costas. Quando você quer memória que sobreviva ao quadro de pilha atual, você a pede explicitamente a um *alocador*. O alocador manual se chama `_alloc`: você chama `_alloc.alloc(T)` para reservar espaço e `_alloc.free(...)` para devolvê-lo. O alocador faz parte do código que você enxerga, então o custo de cada alocação é visível no ponto de chamada.

Esta página cobre o modelo manual, onde *você* é dono do tempo de vida da memória. Para a alternativa automática, veja [Coleta de Lixo Automática](14-garbage-collection.md).

## Alocando um valor tipado

`_alloc.alloc(T)` reserva exatamente memória suficiente para guardar um `T` e retorna um `Ptr(T)` para ele. Como é um ponteiro para dados, você alcança o conteúdo através de `.value` (veja [Ponteiros e Referências](12-pointers-and-references.md)).

```dlang
// para tipos especificos de structs
val pessoaPtr: Ptr(Pessoa) = _alloc.alloc(Pessoa)
pessoaPtr.value.nome = "Gabriel" // altera o campo dentro da struct
```

O compilador conhece o tamanho exato de `Pessoa`, então reserva precisamente esse número de bytes na heap — nada além.

## Por que `.value` importa para segurança

Rotear toda desreferência por `.value` não é só ergonomia, é estratégia de segurança. O acesso a `.value` é um ponto único e centralizado onde o compilador pode validar o ponteiro.

```dlang
// Ao centralizar o acesso à memória na propriedade .value, o compilador ganha
// um ponto centralizado perfeito para validação de segurança do código.
// Se o ponteiro for nulo (null), o compilador pode gerar um erro seguro ao
// acessar .value, impedindo as falhas de segmentação comuns em C/C++.
```

Em vez de uma desreferência selvagem derrubar o processo, um ponteiro nulo aparece como um erro bem definido exatamente onde é tocado.

## Liberando com `defer`

Memória que você aloca manualmente deve ser devolvida manualmente. O padrão idiomático é parear todo `alloc` com um `defer free`, colocado logo após a alocação. `defer` agenda a liberação para rodar quando a função envolvente terminar, não importa por qual caminho.

```dlang
criarInimigo :: () {
  // o Compilador reserva o tamanho exato de Pessoa na heap
  val inimigo: Ptr(Pessoa) = _alloc.alloc(Pessoa)

  // garante que a memória dinâmica será devolvida ao sistema no fim da função
  defer _alloc.free(inimigo)

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

Colocar o `defer` logo abaixo do `alloc` torna vazamentos fáceis de auditar: toda alocação tem seu `free` correspondente visível uma linha abaixo, e o `defer` garante que ele rode mesmo em retornos antecipados ou erros.

## Alocando contêineres dinâmicos

Contêineres da biblioteca padrão como `List(T)` não são mágica do compilador — são structs genéricas comuns que recebem um alocador na construção. Eles seguem a mesma disciplina: `init(_alloc)` para adquirir, `deinit()` (rodado via `defer`) para liberar.

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).init(_alloc)
  defer itens.deinit()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

A `List` guarda o alocador que você deu e o usa para qualquer crescimento interno, então todo o tráfego de heap dela flui pelo mesmo `_alloc` visível. Veja [Alocação Dinâmica](18-dynamic-allocation.md) para mais sobre contêineres que crescem.

## Por quê

Memória manual é o padrão porque uma linguagem de sistema precisa oferecer controle previsível e de custo zero sobre a heap. Tornar o alocador um valor explícito (`_alloc`) significa que não há alocador global escondido nem alocação surpresa: você pode ler uma função e saber exatamente o que ela toca. Parear `alloc` com `defer free` transforma o gerenciamento de tempo de vida num padrão local, visível e verificável mecanicamente, enquanto `.value` dá ao compilador o ponto de controle único de que precisa para manter a memória manual segura.

## Relacionados

- [Ponteiros e Referências](12-pointers-and-references.md)
- [Coleta de Lixo Automática](14-garbage-collection.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)

[← Índice](README.md)
