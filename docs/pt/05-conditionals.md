# Estruturas Condicionais

DLang mantém uma superfície ao estilo C — condições entre parênteses e corpos com chaves obrigatórias — mas é orientada a expressões como Scala: tanto `if` quanto `match` podem ser usados como instruções *ou* como expressões que produzem um valor. Essa única escolha de design elimina a necessidade de um operador ternário separado e faz o código de ramificação ficar limpo de ler.

## `if` como instrução

Na posição de instrução, o `if` funciona exatamente como você espera. A condição vem entre parênteses e o corpo entre chaves:

```dlang
// condicional simples, não associado a um valor
if (c) {
  a()
}

// if / else
if (c) {
  a()
} else {
  b()
}
```

Você pode encadear `else if` para testar várias condições em sequência. As chaves são sempre obrigatórias, mesmo para uma única instrução — não existe forma de corpo sem chaves.

## `if` como expressão (o ternário)

Como o `if` também é uma expressão, você pode ligar seu resultado diretamente. Usado assim, ele é o ternário da linguagem: precisa ter um ramo `else`, porque uma expressão deve sempre produzir um valor.

```dlang
// inline: ambos os ramos presentes -> ok
val x = if (c) a else b

// sem else ao ser usado como valor -> erro de compilação
val y = if (c) a
```

A primeira linha lê-se "x é a se c, caso contrário b." A segunda é rejeitada pelo compilador: sem um `else`, a expressão não tem valor a produzir quando `c` é falso. A regra é simples e vale internalizar — **um `if` usado como valor deve ser exaustivo.**

## `match`

`match` é a construção de despacho por padrão e valor de DLang, o equivalente a um `switch`, mas muito mais capaz. Cada braço usa `->` para mapear um padrão a um resultado, e `else` é o caso padrão geral.

```dlang
match (statusCode) {
  200 -> println("OK")
  404 -> println("Não Encontrado")
  500 -> println("Erro interno")
  else -> println("Desconhecido")
}
```

### `match` como expressão

Coerente com o `if`, o `match` também é uma expressão e pode ser ligado a um valor:

```dlang
val texto: string = match (statusCode) {
  200 -> "OK"
  404 -> "Não encontrado"
  else -> "Desconhecido"
}
```

### Múltiplos valores por braço

Um braço pode listar vários valores separados por vírgula; ele dispara se o sujeito casar com qualquer um deles:

```dlang
match (codigo) {
  200, 201, 204 -> "Sucesso"
  400, 404 -> "Erro do cliente"
  else -> "Outro"
}
```

### Faixas (ranges)

Usando `..` você pode casar uma faixa inclusiva de valores. Isso reaproveita a mesma notação de faixa que depois serve para slices:

```dlang
match (nota) {
  0..59 -> "Reprovado"
  60..100 -> "Aprovado"
  else -> "Nota inválida"
}
```

### Guardas com binding

Um braço pode ligar o sujeito a um nome e então filtrá-lo com uma condição de guarda entre parênteses — `n if (...)`. Isso é coerente com as condições parentesadas de `if` e `while`:

```dlang
match (pessoa.idade) {
  n if (n < 18) -> "menor de idade"
  n if (n < 65) -> "adulto"
  else -> "idoso"
}
```

### Braços com bloco

O corpo de um braço pode ser um bloco completo. Como em todo lugar da linguagem, a última expressão do bloco é o seu valor:

```dlang
match (x) {
  1 -> {
    val y = calcular()
    println(y)
    y * 2
  }
  else -> 0
}
```

### Casando com enums

`match` combina naturalmente com enums, permitindo ramificar por cada variante pelo nome:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("arquivo sumiu")
  Erro.PermissaoNegada -> println("acesso negado")
  else -> println("ok")
}
```

Esta página cobre casar com valores, faixas, múltiplos valores, guardas e variantes de enum. Olhar *dentro* de uma estrutura — desestruturar uma struct, tupla ou enum-com-dados no próprio braço — é **casamento de padrões**, coberto separadamente em [Casamento de Padrões](37-pattern-matching.md).

## Por quê

Fazer de `if` e `match` expressões elimina uma categoria inteira de código repetitivo: não há operador ternário a aprender, nenhum `var` temporário atribuído em cada ramo, e a inicialização condicional se lê como uma única ligação. Exigir `else` quando um `if` é usado como valor é o preço da solidez — o compilador se recusa a deixar uma expressão silenciosamente sem resultado. O `match` então generaliza a mesma ideia: faixas, braços de múltiplos valores e guardas deixam uma construção expressar o que de outra forma seria um emaranhado de `if`s aninhados, mantendo a sintaxe de superfície familiar ao C e os corpos explicitamente entre chaves.

## Relacionados

- [Variáveis e Escopo](04-variables-and-scope.md)
- [Loops e Iterações](06-loops.md)
- [Enumerações](16-enumerations.md)
- [Casamento de Padrões](37-pattern-matching.md)

[← Índice](README.md)
