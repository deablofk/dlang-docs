# Classes e Objetos

> Status: Ausente de propósito

DLang não é uma linguagem orientada a objetos. Não existe a palavra-chave `class`, não há objetos no sentido da OO, não há herança, não há vtables e não há despacho virtual. Isso não é uma omissão à espera de ser preenchida — é uma escolha de projeto deliberada para uma linguagem de sistema orientada a dados.

## Por que não há classes

A classe é a abstração central da programação orientada a objetos, e ela empacota três coisas distintas em um só construto: o **layout dos dados na memória**, o **comportamento** (métodos) que opera sobre esses dados, e uma **identidade** que amarra instâncias a uma hierarquia de tipos. Para uma linguagem cujo propósito inteiro é tornar o layout de memória e o custo de execução óbvios, fundir essas preocupações é exatamente o movimento errado. Uma classe esconde onde o dado vive, qual o seu tamanho e quanto custa chamar um método sobre ele — justamente as coisas que um programador de sistema precisa enxergar.

DLang mantém essas preocupações separadas. **O dado é descrito por uma `struct`**, que é um registro simples e transparente de campos com layout previsível. **O comportamento são funções comuns** anexadas a um tipo por açúcar sintático — `Tipo.metodo :: (...)` com `_` como o self implícito — que compilam para chamadas de função ordinárias, sem tabela de despacho escondida. Não existe uma terceira coisa chamada "objeto"; existem valores de um tipo struct, e existem funções que os recebem.

## O que usar no lugar

Quando você recorreria a uma classe, você descreve o dado com uma [struct](17-structs.md) e anexa comportamento como métodos:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
  ativo: boolean
}

// Comportamento é açúcar sintático sobre dados. Isto NÃO é um método preso a um
// objeto, e NÃO passa por uma vtable. `_` é o placeholder para o self.
Pessoa.falar :: (mensagem: string) {
  println("${_.nome} diz: ${mensagem}")
}

val usuario: Pessoa = Pessoa("Gabriel", 25, true)
usuario.falar("olá")          // resolve para uma chamada de função direta e estática
println(usuario.nome)         // campos são lidos diretamente, sem cerimônia de acessor
```

O ponto em `usuario.falar(...)` parece uma chamada de método de uma linguagem OO, mas o compilador simplesmente o reescreve em uma função normal aplicada a `usuario`. Não há despacho dinâmico, a menos que você opte explicitamente por ele através de uma [interface](25-interfaces.md), e mesmo assim o custo é uma única chamada indireta através de um fat pointer — nunca uma caminhada por hierarquia de classes.

## Como o ferramental da OO mapeia para DLang

| Ideia orientada a objetos | Substituto em DLang |
| --- | --- |
| Classe (dados + métodos) | [`struct`](17-structs.md) + funções `Tipo.metodo` |
| Construtor | [Função fábrica](21-constructors-and-destructors.md) `Tipo.criar :: (...)` |
| Herança | [Composição](23-single-inheritance.md) — embutir uma struct em outra |
| Interface / classe abstrata | [`interface`](25-interfaces.md) (estrutural, fat pointer) |
| Polimorfismo em runtime | [Interfaces](26-polymorphism.md) e sobrecarga de operadores |
| Encapsulamento (`private`) | [Inexistente](22-encapsulation.md) — o dado é transparente por projeto |

## Por quê

Remover as classes é o que torna o resto da linguagem honesto. Uma vez que dado e comportamento estão desacoplados, você pode dispor arrays de structs para iteração amigável ao cache, pode enxergar cada alocação e pode raciocinar sobre o custo de cada chamada apenas lendo-a. O reaproveitamento acontece por composição explícita em vez de herança implícita, e o polimorfismo — quando você genuinamente precisa dele — é uma interface estrutural opt-in com custo visível e limitado. A classe não desapareceu por ser difícil de implementar; desapareceu porque o modelo orientado a dados é mais simples e mais previsível sem ela.

## Relacionados

- [Estruturas de Dados Personalizadas](17-structs.md)
- [Construtores e Destrutores](21-constructors-and-destructors.md)
- [Encapsulamento e Modificadores de Acesso](22-encapsulation.md)
- [Herança Simples](23-single-inheritance.md)
- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Polimorfismo](26-polymorphism.md)

[← Índice](README.md)
