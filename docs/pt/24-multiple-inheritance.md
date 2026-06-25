# Herança Múltipla

> Status: Ausente de propósito

DLang não tem herança múltipla. Como a linguagem não tem [herança simples](23-single-inheritance.md) de modo algum, herdar de vários pais está duplamente fora de questão. Esta é a ausência mais clara de todo o capítulo orientado a objetos, e vale a pena declarar o raciocínio com clareza porque a herança múltipla é o exemplo canônico de uma funcionalidade que custa muito mais do que oferece.

## Por que não há herança múltipla

A herança múltipla herda todos os problemas da herança simples e os multiplica. O acoplamento de layout de dados e comportamento, a classe-base-frágil, a resolução de métodos difícil de ler — cada um deles piora quando um tipo tem mais de um pai. Além disso, a herança múltipla introduz sua própria patologia característica: o **problema do diamante**.

O problema do diamante surge quando um tipo herda de dois pais que, por sua vez, compartilham um ancestral comum:

```
        A
       / \
      B   C
       \ /
        D
```

Se tanto `B` quanto `C` herdam um campo ou método de `A` e então `D` herda de ambos, a linguagem precisa responder perguntas impossíveis de resolver de forma limpa: `D` contém uma cópia dos dados de `A` ou duas? Se `B` e `C` sobrescrevem um método de `A` de formas diferentes, qual sobrescrita `D` recebe? Toda linguagem que tentou suportar isso — C++ com herança virtual, Python com seu algoritmo de MRO — precisou acoplar regras intrincadas e surpreendentes para desambiguar, e os programadores ainda assim se machucam. A funcionalidade fabrica ambiguidade e depois pede que você memorize as regras de desempate.

DLang contorna tudo isso simplesmente por não ter herança para começar.

## O que usar no lugar

Duas necessidades se escondem atrás de "quero herdar de vários tipos": reaproveitar vários pedaços de dados e satisfazer vários contratos. DLang lida com elas usando duas ferramentas limpas e ortogonais.

**Para combinar dados de várias fontes, componha vários campos.** Não há ambiguidade porque cada struct embutida é alcançada através do seu próprio campo nomeado — duas cópias de `A` seriam simplesmente dois campos com nomes diferentes, e você escolhe a qual se refere.

```dlang
Posicao :: struct { x: float, y: float }
Saude   :: struct { vida: int, maxVida: int }

// Inimigo compõe ambos. Sem diamante, sem ambiguidade: cada parte tem seu nome.
Inimigo :: struct {
  posicao: Posicao
  saude: Saude
  nome: string
}

mover :: (e: Inimigo) {
  println("${e.nome} em ${e.posicao.x}, ${e.posicao.y}")
}
```

**Para satisfazer vários contratos, implemente várias interfaces.** Uma única struct pode implementar qualquer número de [interfaces](25-interfaces.md), porque uma interface é um contrato estrutural sobre quais métodos existem, não um pai cujos dados e identidade você absorve. Aqui também não há diamante: implementar duas interfaces que ambas exigem um método chamado `desenhar` significa apenas que você fornece um `desenhar` que satisfaz as duas.

```dlang
Desenhavel :: interface { desenhar :: () }
Serializavel :: interface { serializar :: () -> string }

Circulo :: struct { raio: int }

Circulo as Desenhavel.desenhar :: () {
  println("círculo de raio ${_.raio}")
}

Circulo as Serializavel.serializar :: () -> string {
  return "Circulo(${_.raio})"
}
// Circulo agora satisfaz AMBOS os contratos, com zero ambiguidade.
```

## Por quê

O problema do diamante não é um detalhe de implementação a ser contornado por engenharia — é evidência de que "herdar de muitos pais" é uma ideia mal especificada. Ao separar as duas necessidades reais em composição (para dados) e interfaces (para contratos), DLang lhe dá tudo o que a herança múltipla deveria prover, sem nenhuma das ambiguidades. Combinar dados é explícito e inequívoco porque cada parte tem um nome; combinar contratos é inequívoco porque uma interface não adiciona dado nem identidade, apenas um requisito verificado de que certos métodos existam.

## Relacionados

- [Herança Simples](23-single-inheritance.md)
- [Estruturas de Dados Personalizadas](17-structs.md)
- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Polimorfismo](26-polymorphism.md)
- [Classes e Objetos](20-classes-and-objects.md)

[← Índice](README.md)
