# Macros e Expansão de Código

Uma macro é uma função que roda **dentro do compilador**, recebe *código* (uma AST) como entrada e devolve *código* como saída. Ela é marcada com a anotação `@macro` na definição e invocada com `#` no ponto de uso. A distinção definidora em relação à avaliação de compile-time é nítida: `@comptime` avalia **valores**, enquanto `@macro` transforma **código** (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)).

## Construir código: `quote` e `$`

Dentro de uma macro você constrói novo código com `quote { ... }`, que produz uma AST, e injeta (splice) um pedaço de código existente com `$x`. O `$` espelha de propósito o `${}` da interpolação de string que a linguagem já usa — em ambos os casos `$` significa "coloque este valor aqui".

```dlang
@macro
debug :: (expr: Codigo) -> Codigo {
  // gera código que imprime a EXPRESSÃO e o seu VALOR
  return quote {
    println("${ texto($expr) } = ${ $expr }")   // texto() = forma textual da AST
  }
}

calcular :: () {
  val x = 10
  #debug(x * 2)        // expande em compile-time para: println("x * 2 = ", x * 2)
}
```

A macro recebe a expressão *não avaliada* `x * 2` como um valor `Codigo`. Ela pode renderizá-la como texto (`texto`) e também injetá-la de volta como código vivo, produzindo um print que mostra tanto o fonte quanto o resultado.

## Gerar declarações a partir de anotações

Como uma macro roda no compilador, ela pode ler reflexão (`infoDe`) e as anotações presas a um tipo (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)), e então emitir declarações inteiras. Aqui uma macro gera um método `serializarJson` para qualquer struct percorrendo seus campos e lendo suas anotações `@json`.

```dlang
@macro
derivarJson :: (T: type) -> Codigo {
  var corpo = quote { }
  for (campo : infoDe(T).campos) {
    val chave = campo.anotacao(json).nome       // lê o "max_conn" de @json("max_conn")
    corpo = quote {
      $corpo
      escrever($chave, _.${campo.nome})
    }
  }
  return quote {
    ${T}.serializarJson :: () -> string {
      $corpo
    }
  }
}

#derivarJson(Config)   // uma linha gera o método inteiro em compile-time, custo 0 runtime
```

O laço acumula código re-quotando: cada iteração injeta o `$corpo` anterior e adiciona mais uma linha `escrever`. O `quote` final envolve o corpo acumulado em uma declaração de método presa ao tipo `T`.

## Higiene e a fronteira de design

Macros são **higiênicas**: nomes introduzidos dentro de uma macro não vazam para o chamador, e não capturam por acidente as variáveis do chamador. Elas operam sobre uma **AST tipada**, não sobre texto bruto, então o compilador entende o que elas produzem. E elas só podem **gerar código** — uma macro não pode tocar em arquivos, ler entrada nem fazer I/O arbitrário no compilador.

Isso é o exato oposto das macros de texto do C: onde uma macro do C é substituição textual cega que pode produzir absurdos, uma macro de DLang é uma transformação de código tipada, higiênica e sem efeitos colaterais. Manter as macros restritas à geração pura de código mantém a compilação determinística e segura.

## Por quê

Separar o trabalho de compile-time em "avaliar um valor" (`@comptime`) e "transformar código" (`@macro`) dá a cada tarefa uma ferramenta limpa enquanto reusa um único sistema de anotações/diretivas (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)). Construir código com `quote`/`$` reusa a intuição de interpolação que você já tem, e restringir as macros a transformações higiênicas, tipadas e sem I/O mantém a metaprogramação poderosa sem tornar o compilador imprevisível.

## Relacionados

- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)
- [Compilação em Tempo de Execução](47-runtime-compilation.md)
- [Generics e Programação Paramétrica](32-generics.md)

[← Índice](README.md)
