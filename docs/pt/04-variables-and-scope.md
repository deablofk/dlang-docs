# Variáveis e Escopo

DLang traça uma linha nítida e deliberada entre três tipos de ligações: variáveis mutáveis, valores imutáveis de runtime e constantes verdadeiras de tempo de compilação. A palavra-chave que você escolhe comunica intenção tanto ao leitor quanto ao compilador, e essa intenção é imposta. Esta é a filosofia "explícito sobre implícito" da linguagem aplicada ao ato mais básico da programação — nomear um valor.

## As três ligações

```dlang
// variável: pode ser reatribuída
var a: int = 0

// valor imutável: ligado uma vez em runtime, nunca reatribuído
val b: int = 0

// constante: uma constante verdadeira de tempo de compilação
const val c: int = 0
```

Um `var` é uma ligação mutável. Você pode reatribuí-lo, e operadores como `++` podem alterá-lo no lugar. Use `var` apenas quando o valor realmente precisa mudar ao longo do tempo, como um contador de laço.

Um `val` é uma ligação imutável de runtime. Seu valor é computado quando o controle chega à declaração, mas, uma vez atribuído, nunca pode ser reatribuído. O dado ainda pode ser produzido por trabalho normal de runtime (uma chamada de função, um cálculo) — o que é fixo é a *ligação*, não o momento da computação. Esta é a forma que você deve usar por padrão.

Um `const val` é uma promessa mais forte: o valor é uma constante verdadeira conhecida em **tempo de compilação**. É a escolha certa para parâmetros fixos do seu programa — constantes matemáticas, números de versão, tamanhos fixos — e se conecta à maquinaria de compile-time da linguagem, onde constantes e tipos são ligados com `::` e computados antes mesmo de o programa rodar.

## `::` versus `val`

Vale contrastar essas ligações de runtime com a forma `::` que você verá por toda a documentação. `::` liga **constantes de tempo de compilação** — funções, tipos, namespaces — nomes totalmente resolvidos pelo compilador. `val` e `var`, em contraste, nomeiam dados de **runtime**. Assim, `somar :: (...)` define uma função (uma entidade de compile-time), enquanto `val resultado = somar(2, 3)` liga um valor de runtime. Manter isso em sintaxes separadas deixa imediatamente claro, ao ler o código, se um nome se refere a algo fixo na build ou a algo que vive durante a execução.

## Ligações no nível do arquivo

As três formas também podem aparecer no **escopo de arquivo**, fora de qualquer função. Um `const val` (ou `val` simples) no topo é uma constante de tempo de compilação sem armazenamento em execução — cada uso embute o valor. Já um `var` no topo é uma verdadeira **variável global**: tem armazenamento real que persiste por todo o programa e é compartilhado entre funções.

```dlang
var requestCount: int = 0        // um contador global mutável, compartilhado

bump :: () { requestCount += 1 }
```

Um `var` global é inicializado com zero por padrão (um inicializador escalar constante como `= 5` é honrado). Um inicializador não-constante **não** é executado no início do programa, então se um global precisa de configuração computada, inicialize-o preguiçosamente no primeiro uso, e não na declaração.

## Escopo

As ligações têm escopo léxico no bloco em que são declaradas, delimitado por chaves obrigatórias. Um nome introduzido dentro de um bloco é visível da sua declaração até o fim daquele bloco e não além. Como a linguagem é orientada a expressões, os próprios blocos podem produzir valores (veja [Estruturas Condicionais](05-conditionals.md)), mas a regra de visibilidade é a clássica regra léxica: escopos internos enxergam nomes externos, escopos externos não enxergam nomes internos.

## Por quê

A maioria das linguagens assume mutabilidade por padrão e faz da imutabilidade o caso especial; DLang o empurra para o outro lado, fazendo de `val` o padrão natural e de `var` uma escolha consciente. Isso reduz bugs de mutação acidental e facilita seguir o fluxo de dados. Separar `val` de `const val` distingue "não vou reatribuir isto" de "isto é uma constante de compile-time", o que importa numa linguagem de sistema onde a diferença decide se um valor ocupa armazenamento em runtime ou é embutido no binário. E manter `::` reservado para ligações de compile-time faz com que o leitor nunca tenha de adivinhar a qual mundo um nome pertence.

## Relacionados

- [Tipos Primitivos](01-primitive-types.md)
- [Operadores Aritméticos](03-arithmetic-operators.md)
- [Estruturas Condicionais](05-conditionals.md)
- [Funções e Procedimentos](09-functions.md)
- [Inferência de Tipos](31-type-inference.md)

[← Índice](README.md)
