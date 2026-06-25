# Retorno de Múltiplos Valores

Uma função em DLang pode retornar mais de um valor. O tipo de retorno é escrito como uma lista de tipos entre parênteses, e a função retorna uma lista de valores separados por vírgula. Por baixo dos panos não há maquinaria especial de "retorno múltiplo" — um retorno múltiplo é simplesmente uma função que retorna uma **tupla**, e tuplas são o agregado anônimo e posicional da linguagem.

## Declarando e retornando

Você declara múltiplos resultados escrevendo o tipo de retorno como `(T1, T2, ...)`:

```dlang
buscarCoordenadas :: () -> (int, int) = {
  return 10, 10
}
```

O `return 10, 10` constrói uma tupla de dois elementos `(10, 10)` e a devolve. A forma com vírgula sem parênteses é um atalho: `return 10, 10` significa exatamente `return (10, 10)`, porque dentro de um `return` a palavra-chave já delimita a expressão, então os parênteses são opcionais. O mesmo vale do lado da ligação, como veremos abaixo.

## Consumindo retornos múltiplos

A maneira natural de consumir um retorno múltiplo é **desestruturá-lo** no ponto de chamada, ligando cada componente a seu próprio nome:

```dlang
val (cx, cy) = buscarCoordenadas()
```

Aqui `cx` torna-se `10` e `cy` torna-se `10`. Como a palavra-chave `val` já delimita a ligação, os parênteses são novamente opcionais — `val cx, cy = buscarCoordenadas()` significa a mesma coisa. Se você só se importa com alguns dos resultados, o placeholder `_` descarta um espaço:

```dlang
val (_, cy) = buscarCoordenadas()   // mantém apenas o segundo valor
```

## Retornos são apenas tuplas

Vale interiorizar que um retorno múltiplo não é um recurso especial sobreposto às funções — ele *é* um retorno de tupla. É por isso que o mesmo tipo `(int, int)` que aparece em uma assinatura de retorno também aparece como um tipo de tupla comum para variáveis, e por isso que a mesma sintaxe de desestruturação funciona em ambos os lugares. A convenção de tratamento de erros da linguagem depende exatamente disso: uma função falível retorna `(valor, erro)`, e quem chama desestrutura as duas metades. Veja [Tratamento de erros](15-error-handling.md) para esse padrão, e [Tuplas e desestruturação](38-tuples-and-destructuring.md) para as regras completas sobre tuplas.

O casamento de padrões também opera diretamente sobre tuplas retornadas, permitindo ramificar pela forma do resultado:

```dlang
match (buscarCoordenadas()) {
  (0, 0) -> "origem"
  (x, 0) -> "no eixo X"
  (x, y) -> "ponto (${x}, ${y})"
}
```

## Por quê

Dobrar o retorno múltiplo no conceito de tupla significa que há uma ideia para aprender em vez de duas. O compilador não precisa de uma convenção de chamada sob medida para "funções com várias saídas" — ele retorna uma tupla, um tipo de valor que vive na pilha a custo zero, sem alocador e sem heap oculta. A desestruturação no ponto de chamada mantém o fluxo de dados explícito: todo valor retornado é nomeado (ou deliberadamente descartado com `_`), de modo que nada é silenciosamente perdido. E como tuplas, desestruturação e casamento de padrões são um mecanismo unificado, o retorno múltiplo se compõe de forma limpa com `match`, com a iteração `for (chave, valor : ...)` e com a convenção de erro `(valor, erro)`.

## Relacionados

- [Tuplas e desestruturação](38-tuples-and-destructuring.md)
- [Funções e procedimentos](09-functions.md)
- [Tratamento de erros](15-error-handling.md)
- [Casamento de padrões](37-pattern-matching.md)
- [Passagem de parâmetros](10-parameter-passing.md)

[← Índice](README.md)
