# Coleta de Lixo Automática

DLang oferece um segundo alocador para quando você preferir não rastrear tempos de vida na mão: `_gcAlloc`. Ele tem a mesma forma do alocador manual — `_gcAlloc.alloc(T)` retorna um `Ptr(T)` — mas a memória que entrega é gerenciada para você. Não há `free` correspondente, e nenhum `defer` é necessário. O coletor de lixo observa o ponteiro e recupera o objeto quando nada mais o referencia.

Crucialmente, a coleta de lixo é *opcional por alocação*. A linguagem não tem GC global escondido: a memória só vira coletada porque você a pediu com `_gcAlloc` em vez de [`_alloc`](13-manual-memory.md). Os dois estilos coexistem no mesmo programa.

## Alocando com o GC

Você usa `_gcAlloc` exatamente como o alocador manual, depois acessa o resultado através de `.value` (veja [Ponteiros e Referências](12-pointers-and-references.md)).

```dlang
// alocando usando o alocador do garbage collector
val p: Ptr(Pessoa) = _gcAlloc.alloc(Pessoa)
p.value.nome = "Bruno"

// não precisa de 'defer _gcAlloc.free(p)'.
// o gc rastreia 'p' e o apaga da heap quando a função acaba.
```

A única diferença visível em relação à alocação manual é a ausência do `defer free`. O `Ptr(Pessoa)` se comporta de forma idêntica: mesmo acesso via `.value`, mesmo ponto de controle seguro com checagem de nulo.

## Como a coleta funciona

O coletor de DLang combina dois mecanismos. O principal é a **contagem de referência** no estilo Swift e Wren: cada objeto alocado pelo GC carrega um contador interno que rastreia quantas referências apontam para ele. Quando o contador chega a zero, o objeto é liberado prontamente.

A contagem de referência sozinha não recupera *ciclos de referência* — objetos que apontam um para o outro mas estão inalcançáveis pelo resto do programa. Para tratar esses, uma **varredura em segundo plano** roda de tempos em tempos, procurando objetos órfãos e limpando todos de uma vez.

```dlang
// Contagem de referência estilo Swift/Wren: cada objeto guarda um contador
// interno. Além disso, o rastreamento ocorre em segundo plano de tempos em
// tempos, procurando objetos órfãos e limpando todos de uma vez.
```

Esse híbrido mantém o caso comum barato e determinístico (um incremento/decremento de contador) e ao mesmo tempo garante que o lixo cíclico eventualmente desapareça.

## Escolhendo entre `_alloc` e `_gcAlloc`

Os dois alocadores produzem o mesmo tipo `Ptr(T)`, então a escolha é puramente sobre quem é dono do tempo de vida:

- Recorra a [`_alloc`](13-manual-memory.md) quando quiser controle determinístico e de custo zero e estiver disposto a escrever `defer free`. É o padrão para caminhos quentes e orçamentos apertados de recursos.
- Recorra a `_gcAlloc` quando o grafo de posse for complicado ou os tempos de vida difíceis de fixar, e a conveniência da recuperação automática superar o custo do contador.

Como a decisão mora no ponto de chamada, um único programa pode usar memória manual para seu núcleo crítico de performance e o GC para seus dados mais bagunçados e menos quentes, com os dois tipos de ponteiro interoperando livremente.

## Por quê

A maioria das linguagens com coleta de lixo torna o GC o ar que você respira: toda alocação é escondida e gerenciada, e você não pode optar por sair. DLang inverte isso. A alocação é sempre explícita, e *qual* alocador você nomeia decide o modelo de tempo de vida. Manter `_gcAlloc` simétrico com `_alloc` — mesmo `alloc`, mesmo `Ptr(T)`, mesmo `.value` — significa que as duas estratégias são intercambiáveis no nível de tipo, então você paga pela coleta de lixo só exatamente onde escreve `_gcAlloc`, e em nenhum outro lugar.

## Relacionados

- [Ponteiros e Referências](12-pointers-and-references.md)
- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)

[← Índice](README.md)
