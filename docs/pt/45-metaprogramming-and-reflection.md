# Metaprogramação e Reflexão

O poder em tempo de compilação de DLang flui por **um sistema unificado** em vez de um saco disperso de features especiais. Tudo que o compilador faz por você é expresso como uma *anotação* ou uma *diretiva* — o mesmíssimo mecanismo que `@intrinsic` já usa para concorrência (ver [Multithreading e Concorrência](41-concurrency.md)).

## Anotações (`@`) e diretivas (`#`)

As duas metades do sistema são fáceis de distinguir pelo lugar onde vão e pelo que fazem:

- **`@nome(args)` — uma anotação.** Metadado preso a uma *declaração* (função, struct, campo, parâmetro). É *declarativo*: não faz nada sozinho, apenas rotula a declaração para que o compilador e a reflexão possam lê-la depois.
- **`#nome(args)` — uma diretiva.** Uma *ação* realizada em tempo de compilação, no *ponto de uso*. É *imperativo*, e inclui a invocação de macros (ver [Macros e Expansão de Código](46-macros.md)).

Anotações embutidas: `@intrinsic`, `@inline`, `@naoInline`, `@comptime`, `@macro`, `@externo("C")`, `@reflete`, `@anotacao`, `@depreciado("msg")`.

Diretivas embutidas: `#rodar`, `#se`, `#assert`, `#<macro>`.

## Tipos são valores de compile-time

Um tipo é um valor comum que existe em tempo de compilação, então pode ser guardado, comparado e computado — o mesmo fato que alimenta os generics (`T: type`, `N: int`).

```dlang
val t: type = int
val ehNumerico: boolean = (t == int || t == float)
```

## Rodar código no compilador: `@comptime` + `#rodar`

Anote uma função com `@comptime` para dizer que ela *pode* rodar durante a compilação, e então force uma chamada específica a rodar lá com a diretiva `#rodar`. O resultado é gravado no binário com custo zero em runtime.

```dlang
@comptime                                  // a função PODE rodar na compilação
fatorial :: (n: int) -> int = if (n <= 1) 1 else n * fatorial(n - 1)

const val TABELA: int = #rodar fatorial(10) // 3628800 gravado no binário, custo 0 runtime
```

A diretiva `#se` seleciona código em tempo de compilação — compilação condicional, resolvida antes do programa rodar:

```dlang
#se (PLATAFORMA == "linux") {              // escolhido em compile-time
  abrirArquivo :: (caminho: string) -> int = syscallLinux(caminho)
}
```

## Reflexão em compile-time: sempre disponível

`infoDe(T)` devolve um `TipoInfo` descrevendo um tipo — seu nome, seus campos (cada um com nome, tipo e anotações), e assim por diante. Isso está disponível para qualquer tipo, sem opt-in, porque é consumido inteiramente em tempo de compilação e não deixa nada para trás em runtime.

```dlang
imprimirCampos :: (T: type) {
  for (campo : infoDe(T).campos) {
    println("${campo.nome}: ${campo.tipo}")
  }
}
imprimirCampos(Pessoa)                      // nome: string / idade: int / ativo: boolean
```

## Reflexão em runtime: opt-in com `@reflete`

Por padrão **não há RTTI** — a informação de tipo não existe em runtime, então não custa nada (orientado a dados, peso zero). Quando você realmente precisa inspecionar tipos durante a execução, anote o tipo com `@reflete` e o compilador embute seu `TipoInfo` no binário.

```dlang
// Sem @reflete, a info de tipo simplesmente não está presente em runtime -> custo zero.
@reflete
Pessoa :: struct { nome: string, idade: int, ativo: boolean }
```

## Anotações de usuário com `@anotacao`

Você pode declarar suas próprias anotações. Uma anotação é em si uma declaração sem corpo marcada com `@anotacao`; depois disso você pode prendê-la a declarações, e macros ou funções `@comptime` a leem de volta via reflexão.

```dlang
@anotacao
json :: (nome: string)                      // declara a anotação 'json'

Config :: struct {
  @json("max_conn") maxConexoes: int        // usa a anotação num campo
  @json("host")     host: string
}
```

Uma macro ou função `@comptime` lê essas anotações via reflexão e gera, por exemplo, um serializador — sem RTTI e sem custo em runtime. Ver [Macros e Expansão de Código](46-macros.md) para o lado da geração.

## Por quê

Dobrar toda capacidade de compile-time em duas construções — anotações declarativas e diretivas imperativas — significa um único modelo mental a aprender em vez de uma dúzia de features ad hoc, e esse modelo é o mesmo usado para intrínsecos e macros. Tornar a reflexão compile-time-first com RTTI opcional mantém intacta a promessa orientada a dados: você paga por informação de tipo em runtime só quando a pede pelo nome com `@reflete`.

## Relacionados

- [Macros e Expansão de Código](46-macros.md)
- [Compilação em Tempo de Execução](47-runtime-compilation.md)
- [Generics e Programação Paramétrica](32-generics.md)
- [Multithreading e Concorrência](41-concurrency.md)

[← Índice](README.md)
