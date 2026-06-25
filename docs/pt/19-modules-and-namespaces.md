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

`import("arquivo.dlang")` carrega outro arquivo e retorna seu namespace como um valor. Você liga esse valor a um nome e alcança seus membros através do acesso por ponto.

```dlang
// importação nominativa; retorna o namespace utilizavel (ou bloco, se for namespace { ... })
val mat = import("matematica.dlang")

principal :: () {
  val resultado = mat.somar(10, 5)
  println(resultado)
}
```

`import` é uma expressão que produz um valor de namespace de primeira classe, então `mat` é uma ligação comum — não há sintaxe especial de importação para memorizar, e os nomes importados vivem atrás de `mat.` em vez de serem despejados no seu escopo. Isso mantém as origens explícitas: ler `mat.somar` diz exatamente de onde `somar` veio.

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

Tratar todo arquivo como um módulo automático remove cerimônia: não há nada para declarar e nada para manter sincronizado entre o nome de um arquivo e o nome de seu módulo. Fazer `import` retornar um valor de namespace de primeira classe, em vez de injetar nomes no escopo atual, mantém toda referência externa rastreável até sua origem e evita colisões de nome por padrão. Reaproveitar o *mesmo* conceito de namespace para agrupamento dentro do arquivo significa que há exatamente um modelo mental — um saco pontuado de membros — quer você esteja alcançando entre arquivos ou organizando um só. Nada aqui precisa de suporte em runtime; é puramente como declarações são nomeadas e resolvidas em tempo de compilação.

## Relacionados

- [Funções](09-functions.md)
- [Estruturas de Dados](17-structs.md)
- [Tipagem Estática](29-static-typing.md)

[← Índice](README.md)
