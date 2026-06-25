# Construtores e Destrutores

DLang não tem construtores mágicos nem destrutores mágicos, porque não tem [classes](20-classes-and-objects.md). Não existe um método que roda automaticamente quando um valor nasce, nem um método que roda automaticamente quando ele morre. Em vez disso, a construção é uma **função fábrica** comum que você chama pelo nome, e a destruição é um método comum que você agenda com `defer`. Ambos são código ordinário que você pode ler, e nenhum dos dois esconde fluxo de controle.

## Construção: funções fábrica

Um literal de struct já lhe dá um valor com todos os campos preenchidos. Quando você precisa encapsular o trabalho de construir uma instância válida — escolher padrões, inicializar uma lista dinâmica interna, falar com um alocador — você escreve uma função fábrica. A convenção é `Tipo.criar`, que retorna um valor completamente formado do tipo.

```dlang
Jogador :: struct {
  nome: string
  vida: int
  inventario: List(string)
}

// Fábrica: constrói e retorna um Jogador válido. Não há um `new` escondido.
Jogador.criar :: (nome: string) -> Jogador {
  return Jogador{
    nome: nome,
    vida: 100,
    inventario: List(string).init(_alloc)
  }
}
```

Como a fábrica é apenas uma função, você pode ter quantas quiser, com nomes diferentes (`Jogador.criarVazio`, `Jogador.criarDeArquivo`), cada uma retornando o mesmo tipo. Não há um "construtor" privilegiado nem resolução de sobrecarga para raciocinar — você chama aquele cujo nome diz o que ele faz.

## Destruição: um método comum mais `defer`

Alguns valores possuem recursos que precisam ser liberados: uma lista dinâmica guarda memória da heap, um handle de arquivo guarda um recurso do SO. DLang expressa a limpeza como um método ordinário — por convenção `Tipo.destruir` — que libera o que quer que o valor possua. Nada o chama por você; **você o agenda explicitamente com `defer`**, que garante que ele rode quando o escopo envolvente terminar, não importa como (retorno normal, retorno antecipado ou erro).

```dlang
// Destrutor: libera tudo o que este valor possui.
Jogador.destruir :: () {
  _.inventario.deinit()                 // libera a lista dinâmica interna
  println("${_.nome} foi limpo da memória")
}
```

## Juntando tudo

O ciclo de vida idiomático emparelha a fábrica e o destrutor no topo do escopo, de modo que a limpeza fica visível bem ao lado da criação:

```dlang
jogar :: () {
  // 1. Cria os dados.
  var player = Jogador.criar("Gabriel")

  // 2. Garante que o destrutor rode quando este escopo terminar.
  defer player.destruir()

  // 3. Usa os dados normalmente.
  player.inventario.add("espada longa")
  println(player.nome)

  // Quando `jogar` retorna, o player.destruir() adiado roda automaticamente.
}
```

Esse é o mesmo padrão que você já usa para memória crua (`defer _alloc.free(p)`) e coleções dinâmicas (`defer itens.deinit()`), descrito em [Alocação Dinâmica](18-dynamic-allocation.md) e [Gerenciamento de Memória Manual](13-manual-memory.md). O par fábrica/`defer destruir()` é simplesmente esse padrão aplicado a uma struct que possui recursos.

## Por quê

Construtores e destrutores automáticos são convenientes justamente por serem invisíveis — e invisibilidade é a inimiga de uma linguagem de sistema. Um construtor escondido pode alocar sem que você veja; um destrutor escondido pode rodar uma limpeza cara em uma fronteira de escopo na qual você não pensou. Ao tornar a construção uma função nomeada e a destruição um `defer` explícito, DLang mantém o custo e o momento do ciclo de vida de um valor à plena vista. Você sempre sabe o que roda, e sempre sabe exatamente quando. O mecanismo `defer` lhe dá a segurança da limpeza garantida — ele dispara em todo caminho de saída — sem abrir mão da visibilidade que destrutores escondidos no estilo RAII tiram de você.

## Relacionados

- [Estruturas de Dados Personalizadas](17-structs.md)
- [Classes e Objetos](20-classes-and-objects.md)
- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Arrays e Listas](07-arrays-and-lists.md)

[← Índice](README.md)
