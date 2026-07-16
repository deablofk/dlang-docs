# Coleta de Lixo Automática

DLang **não tem coletor de lixo**, e isso é uma decisão de design deliberada, não uma funcionalidade faltando. Uma linguagem de sistemas deve tornar o custo da memória visível e previsível; um coletor em segundo plano que pode pausar seu programa em um momento imprevisível é o oposto disso.

O que DLang tem *no lugar* é mais forte que um coletor: **posse estática**. Toda alocação pertence a exatamente um valor dono, e o compilador insere a liberação no último uso desse dono — em tempo de compilação, com zero maquinaria de runtime. Você ganha as duas coisas pelas quais um GC é valorizado — "eu não escrevo frees" e "não tem como errar" — sem pausas, sem headers nos objetos e sem runtime.

## Como a memória realmente é liberada

Três mecanismos cobrem tudo, todos estáticos ([Segurança de Memória](14a-memory-safety.md) tem o modelo completo):

- **Destruição ASAP.** Um dono `nocopy` com `deinit` (todo contêiner: `List`, `Map`, `ByteBuf`, `Pool`, e seus próprios invólucros de recursos) é destruído **no seu último uso** — não no fim do escopo, não "eventualmente". Sem drop flags, sem contagem de referências; a análise prova o ponto de liberação por caminho de fluxo de controle.

```dlang
processar :: () {
  var xs: List(int) = List(int).empty()
  xs.add(1)
  xs.add(2)
  println("${xs.size()}")     // último uso de xs — o buffer é liberado bem aqui
  trabalhoCaroQuePrecisaDeMemoria()
}
```

- **Recuperação de strings.** Temporários de `string` — cadeias de concatenação, interpolação, argumentos de `println`, laços de acumulação `s = s + pedaço` — são liberados na hora por drops inseridos pelo compilador. O jeito natural de construir uma string também é o jeito correto para a memória.

- **Semântica de move.** Transferências de posse (`val ys = xs`, parâmetros `sink`, retornos) são moves, então nunca existe um segundo dono para "coletar" — e nunca um momento em que duas coisas poderiam liberar o mesmo buffer (`E_USE_AFTER_MOVE` guarda o binding de origem).

O efeito líquido é recuperação determinística e imediata: a pressão de memória acompanha os dados vivos do programa, os pontos de liberação se leem no código-fonte, e um profiler vê as suas alocações, não as de um coletor.

## O que um GC dá que a DLang recusa

Coletores por rastreamento existem para suportar **aliasing irrestrito** — qualquer objeto pode apontar para qualquer outro, e o runtime descobre a vivacidade. DLang deliberadamente não tem aliasing irrestrito: valores são valores, referências são de segunda classe, e identidade compartilhada passa por handles de `Pool(T)` ou índices ([Segurança de Memória](14a-memory-safety.md)). Uma vez que o aliasing é estruturado, a vivacidade é decidível em tempo de compilação e não sobra nada para o coletor fazer.

Ciclos — o argumento clássico de venda do GC — ilustram isso: entidades em um `Pool` podem se referenciar livremente através de valores `Handle` copiáveis, e o *pool* (um dono) morre no seu último uso. Nenhum detector de ciclos é necessário, porque handles são dados, não arestas que o runtime precise rastrear.

## Checagem de vazamento é ferramenta, não imposto

A garantia do compilador é por dono: todo dono é destruído exatamente uma vez. A pergunta que sobra para um desenvolvedor às vezes — "o que está vivo agora, e quem alocou?" — é respondida por ferramentas no *piso Builtin* (um `debugAllocator` usado pelos harnesses de prova do próprio compilador), não por um runtime que você entrega. Binários de release não carregam nenhuma maquinaria de rastreamento.

## Por que sem coletor — o resumo

| | GC por rastreamento | DLang |
|---|---|---|
| quem libera | o runtime, eventualmente | o compilador, no último uso |
| pausas | sim (ou maquinaria incremental complexa) | nenhuma |
| custo por objeto | headers, barreiras, varredura | zero |
| ciclos | rastreados em runtime | estruturados para fora (handles de `Pool`) |
| vazamento = | memória inalcançável-mas-retida | descartado por dono em tempo de compilação |
| quando a memória volta | imprevisível | determinístico, legível no código |

## Relacionados

- [Segurança de Memória](14a-memory-safety.md) — o modelo de posse completo
- [Memória Manual — o piso Builtin](13-manual-memory.md)
- [Alocação Dinâmica — valores donos](18-dynamic-allocation.md)

[← Índice](README.md)
