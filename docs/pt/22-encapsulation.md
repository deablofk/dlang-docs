# Encapsulamento e Modificadores de Acesso

> Status: Ausente de propósito

DLang não tem modificadores de acesso. Não existe `private`, nem `protected`, nem `public`, e nenhum getter ou setter gerado para proteger campos. Todo campo de uma [struct](17-structs.md) é diretamente legível e gravável onde quer que o tipo da struct esteja visível. Esta é uma decisão deliberada para uma linguagem de sistema orientada a dados, não uma funcionalidade que tenha sido esquecida.

## Por que não há `private`

O encapsulamento no sentido orientado a objetos existe para esconder dados atrás de um muro de métodos, de modo que o "estado interno" de um objeto só possa ser tocado através de uma interface aprovada. Esse modelo assume que o objeto é dono do seu dado e que o código externo não é confiável para mexer nele. Uma linguagem orientada a dados inverte essa suposição: o dado é a coisa primária, ele é feito para ser olhado, disposto e transformado diretamente, e o código que opera sobre ele é secundário. Envolver cada campo em uma barreira `private` com métodos acessores adiciona cerimônia, indireção e complexidade ao compilador sem nenhum benefício que esta linguagem valorize. Você acaba escrevendo `getNome()` e `setNome()` que não fazem nada além de ler e gravar um campo que o chamador poderia ter tocado diretamente.

Há também um argumento de custo. Métodos acessores que existem puramente para satisfazer o `private` ou são eliminados por inlining (caso em que eram pura cerimônia) ou são chamadas reais (caso em que custam algo por nada). Linguagens como Zig e Odin — os parentes mais próximos de DLang — adotam a mesma posição: num contexto de sistema, esconder o layout do seu dado do programador que precisa raciocinar sobre sua memória é uma barreira, não uma proteção.

## O que usar no lugar

Você comunica intenção através de **convenções de nomenclatura, módulos e documentação**, não através de muros impostos pelo compilador. Uma struct simplesmente expõe seus campos:

```dlang
Conta :: struct {
  titular: string
  saldo: int        // sem `private`; legível e gravável diretamente
}

// Comportamento que impõe um invariante é oferecido como uma função, não imposto
// escondendo o campo. Quem quer a checagem chama isto; o campo continua ali
// para código que legitimamente precisa de acesso cru.
Conta.depositar :: (valor: int) {
  if (valor <= 0) return
  _.saldo = _.saldo + valor
}

usar :: () {
  var c = Conta { titular: "Gabriel", saldo: 0 }
  c.depositar(100)      // o caminho protegido
  println(c.saldo)      // leitura direta — perfeitamente legal, nada está escondido
}
```

Quando você genuinamente quer limitar o que outro código pode alcançar, a unidade de fronteira é o **[módulo](19-modules-and-namespaces.md)**, não o campo. Um módulo escolhe quais nomes expõe quando importado; o que ele não exporta simplesmente não fica visível para quem importa. Isso lhe dá uma fronteira real e de granularidade grossa no nível em que ela importa — entre unidades de compilação — sem espalhar `private` por cada campo de cada struct.

## Por quê

O objetivo de recusar modificadores de acesso é manter o dado transparente. Num programa orientado a dados você frequentemente quer ver os mesmos bytes através de lentes diferentes — iterar um campo ao longo de um array de structs, serializar um registro, fazer cast de um ponteiro, inspecionar o layout com reflexão. Todo campo `private` é atrito contra essas operações legítimas. Ao confiar no programador com acesso direto aos campos e reservar fronteiras para o nível de módulo, DLang mantém as structs honestas: uma struct é exatamente os seus campos, sem nada escondido atrás deles, e o que você lê é o que realmente está ali na memória.

## Relacionados

- [Estruturas de Dados Personalizadas](17-structs.md)
- [Classes e Objetos](20-classes-and-objects.md)
- [Módulos e Namespaces](19-modules-and-namespaces.md)
- [Construtores e Destrutores](21-constructors-and-destructors.md)
- [Herança Simples](23-single-inheritance.md)

[← Índice](README.md)
