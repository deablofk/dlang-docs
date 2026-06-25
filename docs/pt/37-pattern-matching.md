# Casamento de Padrões

A [construção `match`](05-conditionals.md) já cobre *valores*: literais, ranges, guardas e enums simples. O casamento de padrões a estende com a capacidade de olhar **dentro** da estrutura de um valor — desestruturar structs, tuplas e enums-com-dados no próprio braço. Reaproveita o mesmo `match` e `->` que você já conhece.

## 1. Desestruturação de struct — o padrão espelha o literal

Um padrão de struct se parece exatamente com um literal de struct. Um campo escrito com um valor precisa *casar* com esse valor; um campo escrito apenas com um nome o *captura* como variável; campos que você não lista são simplesmente ignorados (um padrão parcial).

```dlang
match (pessoa) {
  Pessoa { nome: "Gabriel", idade } -> println("Gabriel tem ${idade}")  // fixa nome, captura idade
  Pessoa { nome, idade }            -> println("${nome}, ${idade}")     // captura ambos
  Pessoa { idade } if (idade < 18)  -> println("menor: ${idade}")       // parcial + guarda
}
```

- campo com valor (`nome: "Gabriel"`) -> precisa casar
- campo com nome só (`idade`) -> capturado como variável
- campos não listados -> ignorados (padrão parcial)

## 2. Wildcard e binding

Dentro de um padrão, `_` significa "há um campo aqui, ignore" — a mesma ideia de "coisa sem nome" do placeholder de lambda. Para ligar o valor **inteiro** ao mesmo tempo em que se desestrutura, use `@`:

```dlang
match (pessoa) {
  Pessoa { nome: _, idade } -> idade    // '_' = "há um campo aqui, ignore"
  p @ Pessoa { idade }      -> usar(p)  // '@' liga o valor INTEIRO a 'p' E desestrutura
}
```

Repare que o braço catch-all de um `match` continua sendo `else`, nunca `_`. O `_` ignora um *slot*; o `else` é o *braço* padrão.

## 3. Padrões de tupla

Tuplas casam posicionalmente. Isso é detalhado em [Tuplas e Desestruturação](38-tuples-and-destructuring.md):

```dlang
match (coord) {           // coord: (int, int), ex. de buscarCoordenadas()
  (0, 0) -> "origem"
  (x, 0) -> "sobre o eixo X"
  (0, y) -> "sobre o eixo Y"
  (x, y) -> "ponto (${x}, ${y})"
}
```

## 4. Aninhamento — padrões compõem recursivamente

Um padrão pode conter outro padrão, até o fim:

```dlang
match (retangulo) {
  Retangulo { canto: Ponto { x: 0, y: 0 } } -> "ancorado na origem"
  Retangulo { canto: Ponto { x, y } }       -> "ancorado em ${x},${y}"
}
```

## 5. Enums com dados (tagged unions) — onde o match brilha

Esse é o recurso que torna o casamento de padrões central na linguagem. Uma variante de enum pode carregar dados: uma tag mais um payload.

```dlang
Forma :: enum {
  Ponto,                                     // sem dados
  Circulo(raio: float),
  Retangulo(largura: float, altura: float)   // 2 campos
}

// criar
val f: Forma = Forma.Circulo(raio: 10.0)
```

Na memória isso é uma **tag mais o maior payload** — um layout compacto, de custo zero, orientado a dados. É isso que substitui hierarquias de classe em DLang. A propriedade-chave de segurança é que você só pode extrair o payload através de um `match`, o que torna o acesso seguro por construção:

```dlang
// extrair dados SÓ é possível via match -> seguro por construção
val area: float = match (f) {
  Forma.Ponto                         -> 0.0
  Forma.Circulo { raio }              -> 3.14159 * raio * raio
  Forma.Retangulo { largura, altura } -> largura * altura
}
```

### Garantias do compilador

- **Exaustividade.** Toda variante precisa ser coberta, ou precisa haver um `else`. Adicionar uma nova variante ao enum sem tratá-la vira um erro de compilação — o compilador aponta cada match que agora ficou incompleto.
- **Acesso seguro.** Você não pode ler `.raio` de um `Retangulo`. O único caminho para um payload é através de um `match` que o ligou, então um acesso a campo fora da variante simplesmente não pode ser escrito.

## Nota de sintaxe: `:` é o separador de campo

Tanto **literais** quanto **padrões** de struct usam `:` como separador de campo (`campo: valor`). Isso é consistente em toda a linguagem e é a forma canônica de nomear o valor de um campo.

## Por quê

Enums com dados (tagged unions) mais casamento exaustivo e seguro por construção dão a DLang uma alternativa compacta e orientada a dados às hierarquias de classe e ao despacho virtual. O compilador transforma "você tratou todos os casos?" em um erro de build em vez de uma surpresa em runtime, e torna a leitura do campo da variante errada irrepresentável em vez de apenas desencorajada.

## Relacionados

- [Estruturas condicionais](05-conditionals.md)
- [Enumerações](16-enumerations.md)
- [Tuplas e Desestruturação](38-tuples-and-destructuring.md)
- [Structs](17-structs.md)

[← Índice](README.md)
