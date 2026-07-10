# Inferência de Tipos

DLang infere tipos, mas apenas *localmente* — dentro de corpos de função, para ligações `val` e `var`. Superfícies públicas nunca são inferidas: parâmetros de função, campos de struct e tipos de retorno são sempre escritos explicitamente. É a mesma fronteira traçada por Odin, Jai e Rust, e mantém toda API legível por si só, sem perseguir inferência por uma base de código.

## Inferência local para `val` e `var`

Quando você liga um valor com `val` ou `var` e omite o tipo, o compilador o lê a partir do inicializador.

```dlang
val idade = 25       // inferido int (literais inteiros são int por padrão)
val nome = "gabriel" // inferido string
val pi = 3.14        // inferido double (literais decimais são double por padrão)
val ativo = true     // inferido boolean
```

Um literal inteiro nu infere `int`; um literal decimal nu infere `double`. Esses são os padrões — o tipo que o compilador escolhe quando nada mais restringe o literal.

## Anotações refinam a inferência (bidirecional)

A inferência é bidirecional: o tipo de um literal é o padrão apenas na ausência de contexto. Quando você escreve uma anotação explícita, ela flui *para dentro* do literal e refina seu tipo.

```dlang
// a anotação continua valendo quando você quer fixar o tipo
val contador: long = 0 // força long em vez do int padrão
```

Aqui `0` inferiria `int` por conta própria, mas a anotação `: long` o refina, então o literal é interpretado como um `long`. A anotação e o literal cooperam em vez de conflitar — o contexto vence o padrão. (Note que isto é *refinamento do tipo de um literal*, não uma conversão numérica: não há alargamento implícito aqui, apenas um literal sendo lido na largura pedida. Conversões entre valores já tipados ainda exigem um `cast` explícito; veja [Tipagem Estática](29-static-typing.md).)

## Inferência em chamadas e fábricas

A inferência também lê o tipo do resultado de uma chamada, então construir um valor nunca obriga você a reafirmar seu tipo.

```dlang
val u = Pessoa("Gabriel", 25, true) // inferido Pessoa
val lista = List(int).empty()  // inferido List(int)
```

E a variável de laço num `for` é inferida a partir do que está sendo iterado — algo de que você já vinha dependendo implicitamente:

```dlang
for (nome : nomes) {
  // o tipo de nome é inferido do tipo de elemento de nomes
}
```

## Onde a inferência é proibida de propósito

Três lugares nunca permitem inferência, porque formam o contrato público do seu código:

```dlang
// - parâmetros de função -> sempre 'nome: Tipo'
// - campos de struct      -> sempre 'campo: Tipo'
// - retorno da função      -> sempre '-> Tipo'
somar :: (a, b: int) -> int = a + b
```

Um parâmetro é sempre `nome: Tipo`, um campo é sempre `campo: Tipo`, e um retorno é sempre `-> Tipo`. Proibir a inferência aqui é uma feature: quem chama, ou quem lê a definição de uma struct, vê a forma completa sem ter que reconstruí-la a partir de um corpo de função em outro lugar.

## Por quê

A inferência local remove as anotações ruidosas e redundantes — reafirmar `int` depois de um literal que obviamente é um `int` — enquanto as assinaturas permanecem explícitas para que o contrato entre partes do código seja sempre escrito na fronteira. Este é o ponto de equilíbrio para o qual Odin, Jai e Rust convergem: a inferência é uma *conveniência local*, nunca um *quebra-cabeça global*. Como literais inteiros são `int` por padrão e decimais são `double`, o caso comum não precisa de anotação nenhuma, e ainda assim a regra bidirecional permite que uma anotação fixe uma largura incomum sem um cast. E como a inferência nunca cruza para parâmetros, campos ou retornos, você sempre consegue ler os tipos de uma API direto da sua declaração — não há inferência a perseguir por arquivos para entender o que uma função espera ou devolve.

## Relacionados

- [Tipos Primitivos](01-primitive-types.md)
- [Variáveis e Escopo](04-variables-and-scope.md)
- [Tipagem Estática](29-static-typing.md)
- [Generics e Programação Paramétrica](32-generics.md)
- [Funções e Procedimentos](09-functions.md)

[← Índice](README.md)
