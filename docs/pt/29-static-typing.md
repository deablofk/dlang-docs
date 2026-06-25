# Tipagem Estática

DLang é estaticamente tipada: todo valor tem um tipo conhecido e fixo em tempo de compilação, e o compilador rejeita qualquer programa que tente usar um valor como um tipo que ele não tem. Não há coerção de tipo em tempo de execução acontecendo nas suas costas. E, igualmente importante, DLang **não faz conversão numérica implícita** — diferente de C, um inteiro mais estreito nunca se alarga silenciosamente para um mais largo. Toda mudança de tipo é escrita explicitamente com `cast(Tipo, valor)`.

## Tipos são checados, não coagidos

Atribuir um valor do tipo errado é um erro de compilação, não uma conversão silenciosa nem um cast em tempo de execução.

```dlang
val idade: int = 25
idade = "vinte" // erro de compilação: string não é int
```

A checagem acontece antes de o programa rodar. Uma `string` e um `int` são tipos diferentes, e nenhum contexto torna um aceitável onde o outro é exigido.

## Sem conversão numérica implícita

Esta é a regra que mais distingue DLang de C. Mesmo quando uma conversão é *de alargamento* e sem perda — `int` para `long`, por exemplo — DLang não a fará por você.

```dlang
// sem conversão numérica implícita (diferente de C)
val pequeno: int = 10
val grande: long = pequeno            // ERRO: int não vira long sozinho
val grande: long = cast(long, pequeno) // OK: conversão explícita
```

A razão é consistência e visibilidade. Se o compilador alargasse `int` para `long` silenciosamente aqui, também seria tentador estreitar `long` para `int` silenciosamente em outro lugar — e *isso* perde dados e informação de sinal, exatamente a classe de bug que assombra o C. Em vez de recortar um "subconjunto seguro" de conversões implícitas e pedir que você memorize suas bordas, DLang torna a regra uniforme: números nunca mudam de tipo por conta própria.

## Convertendo com `cast(Tipo, valor)`

Todas as conversões usam a mesma forma `cast(Tipo, valor)`. A notação entre parênteses é proposital: rima com `Ptr(T)`, `List(T)` e as instanciações genéricas no resto da linguagem, então "aplicar um tipo" sempre parece igual.

```dlang
// conversão usa cast(Tipo, valor) — coerente com a notação Ptr(T)/List(T)
val n: int = cast(int, 3.9)   // trunca para 3
val f: float = cast(float, n)
```

Como o cast é explícito, o leitor sempre enxerga onde ocorre uma operação com perda ou que muda a representação. Truncar `3.9` para `3` é uma decisão que você escreveu, não algo que aconteceu com você.

Casts de ponteiro seguem a mesma regra — reinterpretar um tipo de ponteiro como outro também é escrito com `cast`:

```dlang
// cast de ponteiro também é explícito
val bruto: Ptr(byte) = cast(Ptr(byte), pessoaPtr)
```

## `as` é reservado

DLang deliberadamente mantém `as` fora da história dos casts. `as` é reservado para declarar que um tipo implementa uma interface (veja [Interfaces](25-interfaces.md)), então ele nunca compete com `cast`. Uma palavra-chave, um significado: `cast` converte valores, `as` conecta contratos.

## Por quê

Tipagem estática numa linguagem de sistema se justifica tornando custo e representação previsíveis. Como nenhuma conversão acontece implicitamente, o tipo escrito numa declaração é a representação de máquina exata que você obtém, sem alargamento, estreitamento ou empacotamento escondido. Funilar toda conversão por `cast(Tipo, valor)` transforma cada uma num ponto visível e auditável no código — você lê uma função e sabe precisamente onde o dado muda de largura ou sinal. É o mesmo impulso por trás de ler memória só através de `.value` e alocar só através de um alocador visível: as operações perigosas nunca são invisíveis. O ganho é que categorias inteiras de bugs de C — truncamento silencioso, extensão de sinal inesperada, promoção acidental em aritmética — simplesmente não podem ocorrer sem que você tenha escrito o `cast` que as causa.

## Relacionados

- [Tipos Primitivos](01-primitive-types.md)
- [Tipagem Dinâmica](30-dynamic-typing.md)
- [Inferência de Tipos](31-type-inference.md)
- [Generics e Programação Paramétrica](32-generics.md)
- [Interfaces](25-interfaces.md)

[← Índice](README.md)
