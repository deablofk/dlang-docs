# Funções e Procedimentos

Em DLang uma função é apenas uma constante de tempo de compilação ligada com `::`. Não há uma palavra-chave `def` ou `func` separada — você nomeia o valor e o liga a um literal de função, exatamente como ligaria um tipo ou qualquer outra constante de compile-time. Esse é o modelo "tudo é uma declaração" no estilo Jai, e é o que permite que funções, tipos e namespaces compartilhem uma sintaxe uniforme.

## A forma básica

Uma declaração de função nomeia a função, lista seus parâmetros entre parênteses, dá um tipo de retorno após `->` e fornece um corpo entre chaves:

```dlang
somar :: (a, b: int) -> int {
  val resultado: int = a + b
  return resultado
}
```

Dois detalhes merecem destaque. Primeiro, o `::` liga `somar` como uma constante de tempo de compilação — a identidade da função é fixada na compilação, o que habilita a monomorfização e o despacho estático no restante da linguagem. Segundo, parâmetros que compartilham um tipo podem ser agrupados: `(a, b: int)` declara tanto `a` quanto `b` como `int`, em vez de forçar você a repetir a anotação.

## Forma de linha única (expressão)

DLang é orientada a expressões no sentido de Scala, então quando o corpo de uma função é uma única expressão você pode dispensar as chaves e o `return` e escrever o corpo após `=`:

```dlang
somar :: (a, b: int) -> int = a + b
```

Isso não é um tipo diferente de função — é a mesma declaração com o corpo escrito como uma expressão. A forma `=` e a forma `{ ... }` são intercambiáveis; escolha a que ler melhor. A forma de expressão brilha para auxiliares pequenos e puros, enquanto a forma de bloco serve para lógica de múltiplas instruções.

## Procedimentos

Um "procedimento" em DLang é simplesmente uma função cujo tipo de retorno é omitido (não retorna nada). Você o escreve exatamente como qualquer outra função, apenas sem o `-> T`:

```dlang
saudar :: (nome: string) {
  println("Olá, ${nome}")
}
```

Não há palavra-chave especial distinguindo procedimentos de funções; a ausência de um tipo de retorno é a história inteira. Isso mantém o modelo mínimo — um procedimento é apenas o caso degenerado de uma função sem resultado.

## Valores padrão de parâmetros

Um parâmetro pode declarar um valor padrão com `=`. Se quem chama omitir esse argumento, o padrão é usado:

```dlang
somar :: (a, b: int = 0) -> int = a + b
```

Aqui `b` assume `0` por padrão, então `somar(5)` é equivalente a `somar(5, 0)`. Padrões tornam o comportamento opcional explícito no ponto de definição, em vez de exigir sobrecargas. Como os padrões interagem com argumentos posicionais e nomeados no ponto de chamada está coberto em [Passagem de parâmetros](10-parameter-passing.md).

## Por quê

Ligar funções com `::` em vez de uma palavra-chave dedicada é uma unificação deliberada: uma função é um valor conhecido em tempo de compilação, em nada diferente de uma constante ou um tipo. Essa regra única compensa em todo lugar — ponteiros de função, generics e namespaces a reutilizam sem nova sintaxe. A forma de expressão (`= expr`) mantém funções pequenas concisas e honestas sobre serem mapeamentos puros de entradas para uma saída, enquanto a forma de bloco escala para lógica real. E como não há maquinaria oculta — sem `this` implícito, sem resolução de sobrecarga além de padrões e generics — uma chamada de função compila para um salto direto e previsível.

## Relacionados

- [Passagem de parâmetros](10-parameter-passing.md)
- [Retorno de múltiplos valores](11-multiple-returns.md)
- [Ponteiros de função](33-function-pointers.md)
- [Expressões lambda](39-lambda-expressions.md)
- [Generics](32-generics.md)
- [Módulos e namespaces](19-modules-and-namespaces.md)

[← Índice](README.md)
