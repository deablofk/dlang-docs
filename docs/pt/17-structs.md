# Estruturas de Dados Personalizadas

Uma struct é a ferramenta fundamental de DLang para agrupar dados relacionados sob um tipo nomeado. É um agregado simples de campos — uma descrição de layout de memória — sem herança, sem vtables e sem maquinaria oculta. Comportamento pode ser anexado a uma struct, mas, como você verá, esse comportamento é puro açúcar sintático sobre funções, não orientação a objetos.

## Definindo uma struct

Você liga um tipo struct com `::`, listando cada campo com uma anotação `nome: Tipo`:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
  ativo: boolean
}
```

Isso declara `Pessoa` como um tipo com três campos dispostos na memória na ordem escrita. Não há mais nada nisso — uma struct é exatamente seus campos. Os tipos dos campos são sempre anotados explicitamente; inferência não é permitida em uma definição de struct, assim como não é em uma assinatura de função.

## Métodos são açúcar sobre funções

Você pode anexar um método a uma struct usando a forma `Tipo.metodo :: (...)`. Dentro do método, o placeholder `_` representa a instância sobre a qual se opera — o equivalente ao `this` ou `self` de outras linguagens, mas sem nenhuma da bagagem orientada a objetos:

```dlang
Pessoa.falar :: (mensagem: string) {
  println("${_.nome} diz: ${mensagem}")
}
```

Isto é importante: `Pessoa.falar` é apenas uma função que por acaso recebe uma `Pessoa` (ligada a `_`) mais uma `mensagem`. Não há vtable, nem despacho dinâmico, nem herança. A sintaxe de ponto é uma conveniência para agrupar uma função com o tipo sobre o qual ela trabalha, e as chamadas são resolvidas estaticamente — `usuario.falar("oi")` compila para uma chamada direta, exatamente tão rápida quanto uma função livre.

## Construindo e acessando

Um valor de struct é criado chamando o nome do tipo com os valores dos campos em ordem:

```dlang
val usuario: Pessoa = Pessoa("Gabriel", 25, true)
```

Isso produz uma `Pessoa` com `nome = "Gabriel"`, `idade = 25`, `ativo = true`. O valor vive onde quer que você o declare — aqui na pilha — sem nenhuma alocação na heap envolvida. Campos são lidos e escritos através do ponto:

```dlang
println(usuario.nome)
```

Você também pode construir com nomes de campo explícitos usando a sintaxe de chaves (`Pessoa { nome: "Gabriel", idade: 25, ativo: true }`), que é a forma usada no casamento de padrões e é útil quando você quer os nomes dos campos visíveis no ponto de construção.

## Por quê

Uma struct é apenas um layout de dados, e esse é exatamente o ponto: manter dados e comportamento separados é o coração do modelo orientado a dados. Não há classe, nem herança, nem `private` — esconder campos adicionaria complexidade para o compilador e barreiras para a performance sem render muito numa linguagem de sistema. Quando você quer reusar dados, você compõe: coloque uma struct dentro de outra explicitamente, em vez de herdar. Quando você quer comportamento compartilhado entre tipos, usa uma interface estrutural (um fat pointer), não uma classe base. Métodos existem puramente como açúcar ergonômico — `Tipo.metodo` com `_` como a instância — de modo que o ponto de chamada se lê naturalmente enquanto o código gerado permanece uma chamada de função comum, de despacho estático, com custo zero.

## Relacionados

- [Alocação dinâmica](18-dynamic-allocation.md)
- [Construtores e destrutores](21-constructors-and-destructors.md)
- [Enumerações](16-enumerations.md)
- [Interfaces](25-interfaces.md)
- [Sobrecarga de operadores](27-operator-overloading.md)
- [Casamento de padrões](37-pattern-matching.md)
- [Generics](32-generics.md)

[← Índice](README.md)
