# Sobrecarga de Operadores

DLang permite que você dê a operadores como `+` e `[]` um significado para os seus próprios tipos. Isto é **polimorfismo sintático**: o operador é apenas açúcar para um método com nome especial, e o compilador o resolve **inteiramente em tempo de compilação** (static dispatch). O resultado tem custo zero em runtime — operadores sobrecarregados rodam exatamente na mesma velocidade das chamadas de função escritas à mão nas quais eles se expandem.

## Sobrecarregando um operador aritmético

Você sobrecarrega um operador definindo o método reservado que corresponde a ele. Para `+`, esse método é `operator_add`. Ele recebe o operando da direita e retorna o resultado; `_` é o operando da esquerda (o self).

```dlang
Vetor2D :: struct {
  x, y: float
}

// Sobrecarrega `+` para Vetor2D.
Vetor2D.operator_add :: (outro: Vetor2D) -> Vetor2D {
  return Vetor2D {
    x: _.x + outro.x,
    y: _.y + outro.y
  }
}
```

Agora `+` funciona em valores `Vetor2D`, e o compilador traduz o símbolo em uma chamada direta ao método reservado:

```dlang
val v1 = Vetor2D { x: 1.0, y: 2.0 }
val v2 = Vetor2D { x: 3.0, y: 4.0 }
val resultadoVetor = v1 + v2     // o compilador reescreve para v1.operator_add(v2)
```

## Sobrecarregando os operadores de índice `[]`

Os operadores de subscrito são sobrecarregados com `operator_get` (leitura) e `operator_set` (escrita). São eles que fazem tipos de coleção da biblioteca padrão como `List` e `Map` se comportarem como arrays nativos — a sintaxe de colchetes não é mágica embutida no compilador, são esses dois métodos.

```dlang
List.operator_get :: (indice: int) -> T {
  return _.arrayInterno[indice]
}

List.operator_set :: (indice: int, valor: T) {
  _.arrayInterno[indice] = valor
}
```

Com isso definido, os colchetes leem e escrevem através dos métodos:

```dlang
var nomes: List(string) = List(string).empty()
nomes[0] = "Gabriel"             // reescreve para nomes.operator_set(0, "Gabriel")
val primeiro = nomes[0]          // reescreve para nomes.operator_get(0)
```

É por isso que `List` e `Map` são structs genéricas comuns na biblioteca padrão em vez de embutidos no compilador: a sobrecarga de operadores dá a um tipo definido pelo usuário a mesma sintaxe de indexação que a linguagem já usa para arrays nativos.

## Como a resolução funciona: static dispatch

Para a sobrecarga de operadores o polimorfismo é resolvido **inteiramente em tempo de compilação**. Quando o compilador vê um `+` ou um `[]`, ele intercepta o símbolo e busca o método reservado correspondente (`operator_add`, `operator_get`, `operator_set`, …) no tipo do operando. Ele então emite um salto direto para o código compilado daquela função — a mesma chamada em nível de máquina que emitiria se você tivesse escrito `v1.operator_add(v2)` você mesmo.

Não há busca em runtime, nem tabela de despacho, nem boxing. O operador sobrecarregado roda exatamente na mesma velocidade de uma chamada de função procedural pura. Esta é a extremidade oposta do espectro de custo em relação ao despacho por interface: interfaces decidem *qual* implementação em runtime (uma chamada via fat pointer), enquanto operadores são totalmente decididos em tempo de compilação e não custam nada a mais.

## Por quê

A sobrecarga de operadores merece seu lugar porque faz tipos matemáticos e parecidos com coleções serem lidos naturalmente — `v1 + v2`, `nomes[0]` — sem nunca introduzir um custo escondido em runtime. Ao resolver o símbolo para um método nomeado em tempo de compilação, DLang mantém a conveniência permanecendo honesta quanto à performance: o açúcar é puramente sintático, o despacho é puramente estático, e você sempre pode ver a função na qual ele se expande. Isso também unifica a linguagem com a sua própria biblioteca padrão, já que o mesmo mecanismo que permite escrever `Vetor2D + Vetor2D` é o que permite a `List` e `Map` oferecerem `[]` sem privilégio do compilador.

## Relacionados

- [Polimorfismo](26-polymorphism.md)
- [Estruturas de Dados Personalizadas](17-structs.md)
- [Arrays e Listas](07-arrays-and-lists.md)
- [Tabelas de Espelhamento e Dicionários](08-maps-and-dictionaries.md)
- [Generics](32-generics.md)

[← Índice](README.md)
