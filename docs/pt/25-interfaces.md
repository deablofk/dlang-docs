# Interfaces e Classes Abstratas

DLang não tem classes nem herança, mas tem **contratos**. Uma `interface` declara um conjunto de assinaturas de métodos sem corpos; uma struct que fornece métodos correspondentes satisfaz a interface e pode ser usada onde quer que a interface seja esperada. É assim que DLang entrega polimorfismo em runtime — substituibilidade — sem uma hierarquia de classes. Não há uma noção separada de "classe abstrata", porque uma interface já desempenha esse papel: ela é o contrato puro, com o dado deixado inteiramente para a struct implementadora.

## Declarando uma interface

Uma interface lista os métodos que um implementador deve fornecer. Os corpos estão ausentes de propósito — a interface é o *requisito*, não a implementação.

```dlang
// Exige um método `desenhar` sem argumentos e sem retorno.
Desenhavel :: interface {
  desenhar :: ()
}
```

## Implementando uma interface

Uma struct implementa a interface fornecendo os métodos exigidos. A implementação usa a forma `as` para declarar qual contrato este método satisfaz, e o usual placeholder `_` para o self. O compilador verifica que todo método que a interface exige está presente e corresponde à assinatura — um método ausente ou incompatível é um erro de compilação apontando exatamente o que está errado.

```dlang
Circulo :: struct {
  raio: int
}

// `Circulo as Desenhavel.desenhar` diz: esta é a implementação de Circulo do
// método `desenhar` exigido pelo contrato Desenhavel.
Circulo as Desenhavel.desenhar :: () {
  println("Desenhando um círculo com raio ${_.raio}")
}
```

A correspondência é **estrutural**: `Circulo` satisfaz `Desenhavel` porque fornece os métodos que o contrato nomeia, não porque foi declarado para "estender" algo. Uma única struct pode satisfazer qualquer número de interfaces dessa forma, sem ambiguidade de diamante (veja [Herança Múltipla](24-multiple-inheritance.md)).

## Usando uma interface para polimorfismo

Uma função que recebe um tipo interface pode aceitar qualquer valor cujo tipo satisfaça aquele contrato. Dentro da função o compilador sabe que os métodos exigidos existem e permite que você os chame com segurança.

```dlang
renderizarTela :: (objeto: Desenhavel) {
  // O compilador garante que `objeto` possui `.desenhar`.
  objeto.desenhar()
}

executar :: () {
  val c = Circulo { raio: 10 }
  renderizarTela(c)        // funciona: Circulo satisfaz Desenhavel
}
```

## Como funciona: fat pointers

Quando você passa um valor concreto onde uma interface é esperada, o compilador constrói um **interface fat pointer**: um par formado por um ponteiro para os dados da struct e um ponteiro para a função que implementa o contrato para aquele tipo. Uma chamada como `objeto.desenhar()` então se torna uma única chamada indireta através do ponteiro de função no fat pointer.

Essa é a chave do projeto. Não há hierarquia de classes para percorrer, nem vtable para herdar, nem sobrecarga por objeto além do fat pointer de duas palavras que existe apenas enquanto o valor está sendo usado através da interface. A chamada indireta custa essencialmente o mesmo que uma chamada de [ponteiro de função](33-function-pointers.md), então o polimorfismo baseado em interface roda quase na velocidade de uma chamada de função pura — exatamente a propriedade que uma linguagem de sistema precisa do seu único mecanismo de polimorfismo em runtime.

## Por quê

Uma interface é a forma honesta e mínima de uma classe abstrata: ela carrega o contrato e nada mais, então nunca arrasta layout de dados ou identidade junto. Como a satisfação é estrutural e verificada em tempo de compilação, você obtém a substituibilidade que queria da herança — passar um `Circulo` onde um `Desenhavel` é esperado — sem acoplar tipos em uma árvore. E como a representação em runtime é um fat pointer transparente em vez de uma vtable escondida, o custo é visível e limitado: uma chamada indireta, duas palavras de ponteiro, sem surpresas.

## Relacionados

- [Estruturas de Dados Personalizadas](17-structs.md)
- [Polimorfismo](26-polymorphism.md)
- [Herança Simples](23-single-inheritance.md)
- [Herança Múltipla](24-multiple-inheritance.md)
- [Ponteiros de Função](33-function-pointers.md)
- [Generics](32-generics.md)

[← Índice](README.md)
