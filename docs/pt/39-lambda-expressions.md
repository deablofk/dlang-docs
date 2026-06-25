# Expressões Lambda

Uma lambda é um literal de função: a mesma sintaxe de uma função nomeada, só que sem o `nome ::`. Há uma *escada* de três formas, da mais curta à mais explícita, de modo que você usa exatamente a quantidade de sintaxe que a situação exige.

## As três formas

```dlang
{ _ * 2 }                               // 1 argumento -> placeholder '_' implícito
{ acc, x -> acc + x }                   // N argumentos nomeados, tipos inferidos do contexto
(a: int, b: int) -> int { return a+b }  // forma completa, tipos explícitos
```

A primeira forma é para o caso de um argumento e usa o placeholder universal `_`. A segunda nomeia seus argumentos e deixa os tipos serem inferidos do contexto da chamada, separando argumentos do corpo com `->`. A terceira é o literal de função completo, com tipos de parâmetro e de retorno explícitos.

### Forma multilinha

Quando o corpo é um bloco, a **última expressão do bloco** é o seu valor de retorno — sem `return`:

```dlang
{ x ->
  val y = calcular(x)
  y * 2
}
```

## Trailing lambda

Quando uma lambda é o **último** argumento de uma função, ela sai dos parênteses e é escrita como um bloco depois da chamada. Se for o **único** argumento, os parênteses desaparecem por completo; quaisquer argumentos extras ficam dentro dos parênteses enquanto a lambda vai para fora:

```dlang
nums.map { _ * 2 }                    // único argumento -> sem parênteses algum
nums.reduce(0) { acc, x -> acc + x }  // args extras ficam no (), a lambda vai pra fora
```

Isso mantém um pipeline limpo:

```dlang
val resultado = nums
  .filtrar { _ > 0 }
  .map      { _ * 2 }
  .reduce(0) { acc, x -> acc + x }
```

## Funções que recebem bloco parecem nativas

A consequência da regra do trailing lambda é que *qualquer* função cujo último parâmetro seja uma função se lê como um bloco embutido — sem nenhuma mágica de compilador. Você pode escrever suas próprias construções com cara de controle de fluxo:

```dlang
repetir :: (vezes: int, corpo: () -> ()) {
  var i = 0
  while (i < vezes) { corpo(); i++ }
}

repetir(3) {
  println("olá")
}

comArquivo("dados.txt") { arq ->
  println(arq.ler())
}
```

`repetir(3) { ... }` e `comArquivo("dados.txt") { arq -> ... }` são chamadas de função comuns que apenas *parecem* blocos nativos.

## Nota: `for` e `while` continuam nativos

Um trailing lambda apenas *imita* a aparência de um bloco de controle — ele não substitui os laços nativos. `for` e `while` continuam sendo construções do compilador porque precisam de `break` e `continue` e se beneficiam de otimização própria, que uma chamada de função recebendo uma closure não pode oferecer. Use o trailing lambda para construir APIs *de biblioteca* com forma de bloco; use os laços nativos para iteração de verdade.

## Por quê

Uma regra — uma lambda é uma função nomeada menos o nome — produz a escada inteira, e o placeholder `_` reaproveitado do laço `for` torna o caso comum de um argumento o mais curto possível. A regra do trailing lambda então permite que autores de biblioteca ofereçam APIs com forma de bloco sem nenhum suporte especial do compilador, enquanto a decisão deliberada de manter `for`/`while` nativos preserva `break`/`continue` e o controle do otimizador sobre os laços reais.

## Relacionados

- [Ponteiros de Função](33-function-pointers.md)
- [Closures e Funções Anônimas](34-closures.md)
- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Loops e iterações](06-loops.md)

[← Índice](README.md)
