# Herança Simples

> Status: Ausente de propósito

DLang não tem herança. Uma [struct](17-structs.md) não pode estender outra struct, não existe relação de `extends` ou classe-base, e não existe `super`. Isso vale para o caso mais simples — um tipo herdando de um único pai — e é uma escolha deliberada, não uma funcionalidade ausente. O reaproveitamento em DLang é obtido através de **composição**.

## Por que não há herança

A herança clássica solda à força duas coisas que na verdade são independentes: o **layout dos dados na memória** e o **comportamento** (os métodos). Quando `Cachorro` herda de `Animal`, ele herda tanto os campos *quanto* os métodos, e herda uma identidade "é-um" que o amarra a uma hierarquia de tipos. Para uma linguagem orientada a dados esse acoplamento é um passivo. Você frequentemente quer reaproveitar um pedaço de layout de dados sem arrastar comportamento junto, ou compartilhar comportamento entre tipos que não têm nada a ver entre si estruturalmente. A herança não lhe dá nenhuma maneira de levar um sem o outro.

A herança também torna o custo e o layout mais difíceis de ler. O layout de memória de um tipo derivado depende de uma cadeia de ancestrais que você pode não ter diante de si, e uma chamada de método pode resolver para uma sobrescrita vários níveis acima ou abaixo na hierarquia. Ambos os problemas pioram quanto mais funda a árvore cresce. DLang recusa a árvore por completo.

## O que usar no lugar: composição

Para reaproveitar dados, você **embute uma struct dentro de outra, explicitamente**. A struct interna é um campo nomeado; você alcança seus dados através desse campo. Nada está escondido, e o layout é exatamente o que você escreveu.

```dlang
Animal :: struct {
  nome: string
  vida: int
}

Animal.respirar :: () {
  println("${_.nome} está respirando")
}

// Cachorro NÃO herda Animal. Ele o COMPÕE: Animal é um campo.
Cachorro :: struct {
  base: Animal        // dado embutido, alcançado através de `.base`
  raca: string
}

// Comportamento específico de Cachorro é apenas uma função em Cachorro.
Cachorro.latir :: () {
  println("${_.base.nome} faz au au")
}

usar :: () {
  var rex = Cachorro {
    base: Animal { nome: "Rex", vida: 100 },
    raca: "Vira-lata"
  }

  rex.base.respirar()   // reaproveita o comportamento de Animal, explicitamente, via campo
  rex.latir()           // comportamento próprio de Cachorro
  println(rex.base.vida)
}
```

A relação é visível: um `Cachorro` *tem um* `Animal`, ele não *é um* `Animal`. Quando você quer o comportamento compartilhado, você o chama através do campo (`rex.base.respirar()`), o que torna o reaproveitamento explícito e o caminho do dado óbvio. Se você também quer que valores de `Cachorro` sejam usáveis polimorficamente onde quer que um contrato no estilo `Animal` seja esperado, esse é o trabalho de uma [interface](25-interfaces.md), não de uma classe-base — a composição fornece o dado, a interface fornece a substituibilidade.

## Por quê

A composição mantém as duas metades do "reaproveitamento" separadas, que é exatamente o que a herança funde. Você decide independentemente quais dados embutir e qual comportamento chamar, e ambas as decisões estão escritas no código-fonte. Não há layout de base escondido, nem sobrescrita que dispara de um ancestral que você esqueceu, nem o problema da classe-base-frágil em que mudar um pai quebra silenciosamente os filhos. Quando você precisa de substituibilidade — a parte genuinamente útil da herança — você recorre a [interfaces](25-interfaces.md) estruturais, que lhe dão polimorfismo com custo visível e limitado e sem arrastar uma hierarquia inteira de layout atrás.

## Relacionados

- [Estruturas de Dados Personalizadas](17-structs.md)
- [Classes e Objetos](20-classes-and-objects.md)
- [Herança Múltipla](24-multiple-inheritance.md)
- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Polimorfismo](26-polymorphism.md)

[← Índice](README.md)
