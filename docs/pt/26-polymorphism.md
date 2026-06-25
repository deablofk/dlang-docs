# Polimorfismo

Polimorfismo — escrever código que funciona de modo uniforme sobre muitos tipos — existe em DLang, mas é dividido de forma limpa em dois mecanismos com custos bem diferentes, ambos visíveis ao programador. Há **polimorfismo em runtime** através de [interfaces](25-interfaces.md), resolvido com um fat pointer, e **polimorfismo em tempo de compilação** através de [sobrecarga de operadores](27-operator-overloading.md) e [generics](32-generics.md), resolvido inteiramente antes de o programa rodar. Não há, deliberadamente, polimorfismo baseado em herança nem despacho de métodos virtuais (veja [Métodos Virtuais](28-virtual-methods.md)).

## Polimorfismo em runtime via interfaces

Quando você precisa que um valor cujo tipo concreto só é conhecido em runtime se comporte de acordo com um contrato compartilhado, você usa uma interface. Uma função que recebe um parâmetro de interface aceita qualquer tipo que satisfaça o contrato, e chama os métodos do contrato através de um fat pointer.

```dlang
Desenhavel :: interface {
  desenhar :: ()
}

// `objeto` pode ser um Circulo, um Quadrado, qualquer coisa que satisfaça Desenhavel.
// O tipo concreto é escolhido em runtime; a chamada passa pelo fat pointer.
renderizarTela :: (objeto: Desenhavel) {
  objeto.desenhar()
}
```

Esta é a única forma de polimorfismo em DLang que tem um passo de despacho em runtime, e mesmo esse passo é apenas uma chamada indireta através da metade ponteiro-de-função do fat pointer — próxima do custo de uma chamada pura, sem percorrer hierarquia. O mecanismo completo é descrito em [Interfaces e Classes Abstratas](25-interfaces.md).

## Polimorfismo em tempo de compilação via sobrecarga de operadores

Operadores também são polimórficos: `+` significa uma coisa para `int` e outra para `Vetor2D`, e `[]` funciona tanto em arrays quanto em coleções definidas pelo usuário. Isto é **polimorfismo sintático**, e é resolvido inteiramente em tempo de compilação (static dispatch). O compilador vê o operador, busca o método reservado correspondente no tipo do operando, e emite uma chamada direta para ele.

```dlang
val v1 = Vetor2D { x: 1.0, y: 2.0 }
val v2 = Vetor2D { x: 3.0, y: 4.0 }
val soma = v1 + v2        // o compilador reescreve para v1.operator_add(v2)
```

Como a resolução acontece antes de o programa rodar, o custo em runtime é zero — a chamada é tão rápida quanto qualquer chamada de função pura. Os detalhes e a lista completa de operadores sobrecarregáveis estão em [Sobrecarga de Operadores](27-operator-overloading.md).

## Polimorfismo em tempo de compilação via generics

Uma terceira forma permite que um único trecho de código funcione sobre muitos tipos parametrizando sobre o próprio tipo. Um `max` genérico funciona para qualquer tipo comparável; uma `List(T)` genérica funciona para qualquer tipo de elemento. O compilador instancia uma versão especializada para cada tipo usado, então não há boxing nem despacho — o código gerado é como se você o tivesse escrito à mão para aquele tipo. Veja [Generics](32-generics.md).

```dlang
max(T) :: (a, b: T) -> T = if (a > b) a else b
val m = max(10, 20)       // T = int inferido; especializado em tempo de compilação
```

## Escolhendo um mecanismo

| Você precisa… | Use | Custo |
| --- | --- | --- |
| Comportamento escolhido em **runtime** a partir de um contrato compartilhado | [Interfaces](25-interfaces.md) | Uma chamada indireta (fat pointer) |
| Um símbolo como `+` ou `[]` funcionando no seu tipo | [Sobrecarga de operadores](27-operator-overloading.md) | Zero — static dispatch |
| Um algoritmo funcionando sobre muitos tipos | [Generics](32-generics.md) | Zero — especializado por tipo |

A regra norteadora é que você paga por despacho dinâmico apenas quando genuinamente precisa de uma decisão em runtime, e você o pede explicitamente tipando um parâmetro como interface. Todo o resto é resolvido em tempo de compilação.

## Por quê

Dividir o polimorfismo por custo é o que mantém DLang previsível. Numa linguagem OO, uma chamada de método pode ser estática, virtual ou despachada por interface, e a sintaxe não lhe diz qual — então você não consegue ler o custo na página. Aqui o mecanismo é sempre legível: um parâmetro tipado como interface significa uma chamada via fat pointer, um operador ou um generic significa que o trabalho foi feito em tempo de compilação. Você obtém toda a amplitude expressiva do polimorfismo, mas nunca paga por despacho dinâmico por acidente.

## Relacionados

- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Sobrecarga de Operadores](27-operator-overloading.md)
- [Métodos Virtuais](28-virtual-methods.md)
- [Generics](32-generics.md)
- [Ponteiros de Função](33-function-pointers.md)

[← Índice](README.md)
