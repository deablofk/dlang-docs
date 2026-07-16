# Construtores e Destrutores

DLang não tem construtores mágicos — construção é uma **função fábrica** comum que você chama pelo nome, sem fluxo de controle escondido. A destruição, por outro lado, *é* automática, mas de um jeito muito específico e visível: um tipo que possui algo declara um método **`deinit`**, e o compilador o chama **exatamente uma vez, no último uso do valor**. Você nunca agenda a limpeza e não tem como esquecê-la — e como o ponto de liberação é o *último uso*, não uma fronteira de escopo escondida, dá para lê-lo direto no código.

## Construção: funções fábrica

Um literal de struct já dá um valor com todos os campos preenchidos. Quando você precisa encapsular o trabalho de construir uma instância válida — escolher padrões, inicializar uma lista interna — você escreve uma função fábrica. A convenção é `Tipo.new` (ou um nome mais específico), retornando um valor completo:

```dlang
Jogador :: nocopy struct {
  nome: string
  vida: int
  inventario: List(string)
}

// Fábrica: constrói e retorna um Jogador válido. Não há `new` escondido.
Jogador.new :: (nome: string) -> Jogador {
  return Jogador {
    nome: nome,
    vida: 100,
    inventario: List(string).empty()
  }
}
```

Como a fábrica é só uma função, você pode ter quantas quiser com nomes diferentes (`Jogador.newVazio`, `Jogador.fromArquivo`), cada uma retornando o mesmo tipo. Não há "o construtor" privilegiado nem resolução de overload para entender — você chama a que o nome diz o que faz. (O struct acima é `nocopy` porque contém uma `List` — um struct com um campo dono é ele próprio um dono, por contágio.)

Para inicializar um slot do chamador *in place* — o padrão que C resolve com um ponteiro de saída — use um parâmetro `set` em vez de um retorno; veja [Passagem de Parâmetros](10-parameter-passing.md).

## Destruição: `deinit`, automático e ASAP

Um tipo `nocopy` que possui um recurso declara `deinit`. O compilador insere a chamada no **último uso estático** do valor — assim que o valor está provadamente morto, em todo caminho de fluxo de controle, exatamente uma vez. Não há drop flags nem contabilidade de runtime; a análise é inteiramente estática ([Segurança de Memória](14a-memory-safety.md)).

```dlang
Jogador.deinit :: () {
  println("${_.nome} foi limpo da memória")
  // campos donos (como _.inventario) são derrubados automaticamente depois deste corpo
}

jogar :: () {
  var player: Jogador = Jogador.new("Gabriel")
  player.inventario.add("espada longa")
  println(player.nome)          // último uso — o deinit roda bem aqui
  coisaCaraSemRelacaoComPlayer()
}
```

Três propriedades valem internalizar:

- **Exatamente uma vez, em todo caminho.** `return` antecipado, `break`, fall-through — o compilador prova uma liberação por caminho. Liberação dupla não é uma classe de bug de runtime; uma forma que causaria uma é `E_USE_AFTER_MOVE` em tempo de compilação.
- **ASAP, não fim de escopo.** O valor morre no seu último *uso*, então memória e recursos voltam o mais cedo que o programa permite.
- **Posse compõe.** Um corpo de `deinit` libera o que o *próprio struct* segura cru (um fd, um recurso de C); **campos** donos (uma `List`, um `ByteBuf`, outro dono) são derrubados recursivamente sem você escrever nada.

Se a posse é transferida — o valor é movido para um parâmetro `sink`, guardado num contêiner ou retornado — a responsabilidade pelo destrutor se move junto; o binding antigo está morto (`E_USE_AFTER_MOVE` se tocado) e nenhuma liberação dupla pode ocorrer.

## E o `defer`?

`defer statement` continua existindo e continua rodando em toda saída da função — mas não é mais como valores são destruídos. Use-o para efeitos que *não* são posse: logar uma conclusão, dar flush no fim de uma fase, teardown de teste. Se você se pegar escrevendo `defer x.release()`, o tipo deveria ser um dono `nocopy` com `deinit` — aí o compilador faz isso, corretamente, em todo caminho.

## Racional de design

A velha objeção a destrutores automáticos — "código invisível rodando em horas invisíveis" — é respondida de um jeito diferente do C++. A construção continua uma função nomeada: sem alocação escondida, sem conversões implícitas, você vê cada custo. A destruição é automática mas *determinística e legível*: `deinit` é código comum que você escreveu, e roda no último uso do valor, um ponto que se acha lendo a função. O que a DLang remove não é visibilidade, é o *agendamento manual* — a única parte que humanos erram com consistência (o free esquecido, o free duplo num return antecipado). O compilador é simplesmente melhor em posicionar a chamada do que um `defer` que você tinha que lembrar de escrever.

## Relacionados

- [Structs](17-structs.md)
- [Segurança de Memória](14a-memory-safety.md)
- [Memória Manual — o piso Builtin](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Passagem de Parâmetros](10-parameter-passing.md)

[← Índice](README.md)
