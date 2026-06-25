# Loops e Iterações

DLang oferece duas construções de laço — `while` para repetição guiada por condição e `for` para iterar sobre uma coleção — além de uma forma ergonômica com placeholder do `for` para o caso comum de "fazer algo com cada elemento". Como os condicionais, os laços mantêm a superfície ao estilo C: cabeçalhos entre parênteses e chaves obrigatórias.

## `while`

Um laço `while` repete o corpo enquanto a condição entre parênteses se mantiver. Esta é a ferramenta para repetição guiada por uma condição que muda, em vez de por uma coleção fixa:

```dlang
var contador: int = 0
while (contador < 10) {
  contador++
}
```

Note que o contador é um `var`, porque é mutado a cada passagem; um `val` imutável não poderia ser incrementado. Veja [Variáveis e Escopo](04-variables-and-scope.md) para as regras de mutabilidade.

## `for` sobre uma coleção

A forma `for (x : coll)` liga cada elemento de uma coleção a um nome, por vez, e executa o corpo uma vez por elemento. O tipo do elemento é inferido da coleção, então você não o anota:

```dlang
val nomes: []string = ["gabriel", "bruno"]   // implicitamente [2]string
for (nome : nomes) {
  println(nome)
}
```

A cada iteração, `nome` é ligado ao próximo elemento de `nomes`. Esta é a forma idiomática de percorrer arrays e listas. Ao iterar um mapa chave-valor, a variável do laço desestrutura em um par `(chave, valor)` — essa variante é coberta em [Tabelas e Dicionários](08-maps-and-dictionaries.md).

## A forma com placeholder automático

Para o caso muito comum em que o corpo simplesmente usa cada elemento uma vez, DLang oferece uma forma mais curta: `for (coll)` sem variável explícita. Dentro de um laço assim, o elemento fica disponível como o placeholder universal `_`. O placeholder é passado automaticamente — comporta-se como uma lambda de um argumento `x -> ...` cujo parâmetro é `_`:

```dlang
for (nomes) {
  println(_)
}
```

Isso se lê como "para cada um de `nomes`, imprima-o." É exatamente equivalente a `for (x : nomes) { println(x) }`, apenas sem nomear a variável descartável. Esta forma é fornecida pela biblioteca padrão em vez de ser mágica do compilador, e reaproveita o mesmo placeholder `_` que você vê em lambdas e corpos de método — uma ideia, aplicada de forma consistente.

## Por quê

Duas construções de laço cobrem as duas necessidades genuinamente diferentes — repetir enquanto uma condição se mantém e visitar cada elemento de uma coleção — sem empilhar variantes. A forma `for` com placeholder existe porque o corpo de laço mais frequente usa seu elemento exatamente uma vez, e nomear uma variável só para consumi-la em seguida é ruído. Fazer `_` significar "o elemento atual" aqui é a mesma convenção usada para o argumento implícito de lambda e para `this`/`self` em métodos, então quem conhece o `_` em um lugar já o conhece em todos. Manter a forma com placeholder como recurso de biblioteca, e não como palavra-chave, reforça a postura da linguagem de que comportamento é açúcar sobre dados, não um privilégio embutido.

## Relacionados

- [Variáveis e Escopo](04-variables-and-scope.md)
- [Estruturas Condicionais](05-conditionals.md)
- [Arrays e Listas Nativas](07-arrays-and-lists.md)
- [Tabelas e Dicionários](08-maps-and-dictionaries.md)
- [Expressões Lambda](39-lambda-expressions.md)

[← Índice](README.md)
