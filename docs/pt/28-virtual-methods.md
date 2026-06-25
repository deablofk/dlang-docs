# Métodos Virtuais

> Status: Ausente de propósito

DLang não tem métodos virtuais. Não existe a palavra-chave `virtual`, nem `override`, nem vtable, nem mecanismo pelo qual uma chamada de método despacha silenciosamente para uma implementação sobrescrita escolhida pelo tipo dinâmico de um objeto. Como a linguagem não tem [classes](20-classes-and-objects.md) nem [herança](23-single-inheritance.md), não há, para começar, hierarquia pela qual um método virtual pudesse despachar. Esta ausência é uma consequência direta de ser uma linguagem de sistema orientada a dados.

## Por que não há métodos virtuais

Um método virtual é o coração de despacho em runtime da programação orientada a objetos: cada objeto carrega um ponteiro escondido para uma vtable, e uma chamada como `obj.metodo()` segue esse ponteiro para encontrar a implementação certa para o tipo real do objeto. Isso lhe compra polimorfismo, mas impõe custos que uma linguagem de sistema não quer pagar silenciosamente:

- **Um ponteiro escondido por objeto.** Todo objeto de uma classe polimórfica carrega um ponteiro de vtable, inflando seu tamanho e perturbando o layout justo e previsível do qual o código orientado a dados depende. Um array desses objetos deixa de ser um array limpo de dados.
- **Uma chamada indireta que você não enxerga.** `obj.metodo()` parece idêntico a uma chamada de método comum, mas secretamente realiza uma indireção de ponteiro, que a CPU não consegue prever tão bem quanto uma chamada direta e que o compilador geralmente não consegue fazer inline. O custo é invisível na sintaxe.
- **Acoplamento à herança.** O despacho virtual só faz sentido dentro de uma hierarquia de classes, e DLang rejeitou essa hierarquia pelas razões dadas em [Herança Simples](23-single-inheritance.md) e [Classes e Objetos](20-classes-and-objects.md).

Em resumo, um método virtual esconde tanto um custo de memória quanto um custo de despacho atrás de uma sintaxe de aparência comum. Toda a postura de DLang é que tais custos devem ser visíveis e opt-in.

## O que usar no lugar

DLang oferece dois substitutos, cada um tornando seu custo legível.

**Quando você precisa de despacho em runtime, use uma [interface](25-interfaces.md).** Esta é a versão explícita e opt-in de um método virtual. Você declara o contrato, uma struct o implementa, e uma função que recebe a interface despacha através de um fat pointer:

```dlang
Desenhavel :: interface {
  desenhar :: ()
}

Circulo :: struct { raio: int }

Circulo as Desenhavel.desenhar :: () {
  println("círculo de raio ${_.raio}")
}

// O despacho em runtime acontece AQUI, e é visível: o parâmetro é tipado como
// a interface, então você sabe que `desenhar` passa pelo fat pointer.
renderizarTela :: (objeto: Desenhavel) {
  objeto.desenhar()
}
```

A diferença em relação a um método virtual é a honestidade. O custo de despacho aparece exatamente onde um parâmetro é tipado como interface — nunca escondido dentro de um `obj.metodo()` de aparência inocente sobre um tipo concreto. O fat pointer carrega o ponteiro de função ao lado do dado apenas enquanto o valor é usado através da interface; a própria struct permanece um bloco de dados limpo e livre de vtable.

**Quando você não precisa de despacho em runtime, use um método comum.** Uma chamada `Tipo.metodo` sobre um tipo concreto é sempre uma chamada direta e resolvida estaticamente, sem indireção — o caso comum não paga nada.

## Por quê

Remover métodos virtuais é o ponto final natural de remover classes e herança. A capacidade útil que eles forneciam — escolher comportamento em runtime com base no tipo de um valor — sobrevive como a interface, mas com duas diferenças cruciais: o dado permanece livre de qualquer ponteiro de vtable embutido, e o custo de despacho é anunciado pelo tipo do parâmetro em vez de sepultado numa chamada que parece comum. Você obtém polimorfismo em runtime exatamente quando o pede, paga uma chamada indireta visível quando o usa, e não paga nada no resto do tempo.

## Relacionados

- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Polimorfismo](26-polymorphism.md)
- [Classes e Objetos](20-classes-and-objects.md)
- [Herança Simples](23-single-inheritance.md)
- [Ponteiros de Função](33-function-pointers.md)

[← Índice](README.md)
