# Módulos e Namespaces

DLang organiza código com duas ideias complementares. Um **módulo** é um arquivo inteiro: todo arquivo `.dlang` é automaticamente um módulo, sem boilerplate nem declaração especial. Um **namespace** é um agrupamento nomeado de declarações *dentro* de um arquivo, criado com um bloco `namespace`. Juntos, eles permitem dividir um programa entre arquivos e ainda recortar agrupamentos lógicos dentro de um único arquivo.

## Arquivos são módulos automaticamente

Você não declara um módulo — o arquivo *é* o módulo. Declarações de nível superior em um arquivo são simplesmente os membros do módulo.

```dlang
// arquivo com módulo automático
// o nome do arquivo: matematica.dlang

// uma função constante normal do seu sistema
somar :: (a, b: int) -> int = a + b
```

A ligação constante `::` introduz `somar` como uma função conhecida em tempo de compilação (veja Funções). Como o arquivo é um módulo, `somar` torna-se um membro que outros arquivos podem importar.

## Importando um módulo

`import("caminho")` carrega outro módulo e retorna seu namespace como um valor. Você liga esse valor a um nome e alcança seus membros através do acesso por ponto.

Os caminhos são **relativos à raiz**: a raiz do projeto é o diretório mais próximo acima do seu arquivo que contém um marcador `project.dlang`, e toda importação é resolvida em relação a ela — nunca relativa ao arquivo importador. Não há **`..`** nem **sufixo `.dlang`** (ele é implícito):

```dlang
// project.dlang marca a raiz; isto resolve para <raiz>/matematica.dlang
val mat = import("matematica")

principal :: () {
  val resultado = mat.somar(10, 5)
  println(resultado)
}
```

`import` é uma expressão que produz um valor de namespace de primeira classe, então `mat` é uma ligação comum — não há sintaxe especial de importação para memorizar, e os nomes importados vivem **somente** atrás de `mat.`, nunca despejados no seu escopo. Isso mantém as origens explícitas: ler `mat.somar` diz exatamente de onde `somar` veio. A regra é imposta — um `somar` puro de outro módulo é um erro de compilação. Vale também para tipos: um tipo de `mat` é escrito `mat.Tipo`, usável onde um tipo é esperado (anotações, literais `mat.Tipo { .. }`, `mat.Tipo.factory()`).

## Importações inline

O acesso com prefixo é o padrão porque mantém as origens rastreáveis, mas às vezes os membros de um módulo são usados com tanta frequência que o prefixo é só ruído — os utilitários `util` do próprio projeto, por exemplo. Para isso, `inline import("caminho")` insere os membros de nível superior do módulo alvo **diretamente no escopo atual**, e você os chama sem qualificação:

```dlang
// util.dlang define `shout :: (s: string) -> string`

// com prefixo: cada chamada carrega o nome do módulo
val util = import("util")
saudar :: () { println(util.shout("oi")) }

// inline: os membros caem no escopo, sem prefixo
inline import("util")
saudar :: () { println(shout("oi")) }
```

As duas formas são os *únicos* dois modos de alcançar outro módulo — deliberadamente não há um terceiro. `inline import` não liga nome algum (não há `util` para escrever), e valem as mesmas regras de caminho: relativo à raiz, sem `..`, sem sufixo `.dlang`. `inline` é uma palavra-chave **contextual** — só é especial imediatamente antes de `import`, então `inline` continua sendo um ótimo nome de variável ou campo em qualquer outro lugar.

O que é inserido são exatamente os membros públicos de nível superior do módulo — funções, tipos, constantes — o mesmo conjunto que você alcançaria através de uma ligação. Um tipo importado assim é usável puro, como um local:

```dlang
inline import("shapes")            // shapes.dlang define `Point`

origem :: (p: Point) -> int = p.x + p.y   // `Point`, não `shapes.Point`
```

**Os nomes devem permanecer únicos.** Um programa compartilha um único espaço de nomes plano de nível superior, então um nome importado inline não pode colidir com um nome que você já declara, nem com um nome que uma *outra* importação inline fornece. Uma colisão é um erro de compilação — nunca um encobrimento silencioso — de modo que a ambiguidade é pega na definição, não deixada para aparecer depois:

```dlang
inline import("greet")             // greet.dlang define `resposta :: () -> int = 1`

resposta :: () -> int = 2          // error[E_DUPLICATE]: "resposta" já foi
                                   // trazida por inline import("greet")
```

A correção é manter a ligação com prefixo para o módulo cujo nome conflita (`val g = import("greet")`, e então `g.resposta()`), de modo que exista exatamente uma `resposta` sem qualificação. Essa é a mesma regra que já governa os nomes de nível superior de um programa; a importação inline apenas a torna explícita no ponto da importação.

Ambas as formas podem mirar o *mesmo* módulo ao mesmo tempo — alcance um membro com prefixo num lugar e puro em outro:

```dlang
inline import("greet")
val g = import("greet")

a :: () -> string = shout("x")     // sem qualificação, via a importação inline
b :: () -> string = g.shout("y")   // com prefixo, via a ligação
```

Use `inline import` quando um módulo é o vocabulário do arquivo e o prefixo não acrescenta nada; use uma ligação quando a origem merece ser soletrada a cada chamada. Como uma importação inline é uma inserção em tempo de compilação sem valor em runtime, ela não custa nada em tempo de execução.

## Namespaces internos

Dentro de um arquivo você pode agrupar declarações relacionadas sob um nome usando `Nome :: namespace { ... }`. Os membros são então alcançados com `Nome.membro`, exatamente como os membros de um módulo importado.

```dlang
// criando namespace interno no mesmo arquivo
Geometria :: namespace {
    const val PI: float = 3.14159

    areaQuadrado :: (lado: int) -> int = lado * lado
}

// para usar no mesmo arquivo:
val area = Geometria.areaQuadrado(4)
```

Note a simetria: `Geometria.areaQuadrado` (um namespace interno) e `mat.somar` (um módulo importado) são acessados de forma idêntica. Um bloco de namespace pode conter quaisquer declarações — constantes como `PI` ligadas com `const val`, funções, structs — e as agrupa sob um único prefixo pontuado.

## Módulos e namespaces têm a mesma forma

A razão de `import` e `namespace` parecerem intercambiáveis é que produzem o mesmo tipo de coisa: um saco nomeado de membros acessado com um ponto. Um arquivo importado *é* um valor de namespace; um bloco interno `namespace { ... }` *é* um valor de namespace. Quer um agrupamento viva em seu próprio arquivo ou dentro de um maior, você o consome da mesma forma.

## Por quê

Tratar todo arquivo como um módulo automático remove cerimônia: não há nada para declarar e nada para manter sincronizado entre o nome de um arquivo e o nome de seu módulo. Fazer `import` retornar um valor de namespace de primeira classe, em vez de injetar nomes no escopo atual, mantém toda referência externa rastreável até sua origem e evita colisões de nome por padrão — esse é o padrão seguro. `inline import` é a única saída explícita para quando os membros de um módulo são tão difundidos que o prefixo só vira ruído; torná-lo uma palavra-chave distinta faz o trade-off (rastreabilidade por concisão) sempre visível no código, e não há um *terceiro* modo que corroeria a regra do caminho único e óbvio. Reaproveitar o *mesmo* conceito de namespace para agrupamento dentro do arquivo significa que há exatamente um modelo mental — um saco pontuado de membros — quer você esteja alcançando entre arquivos ou organizando um só. Nada aqui precisa de suporte em runtime; é puramente como declarações são nomeadas e resolvidas em tempo de compilação.

## Relacionados

- [Funções](09-functions.md)
- [Estruturas de Dados](17-structs.md)
- [Tipagem Estática](29-static-typing.md)

[← Índice](README.md)
