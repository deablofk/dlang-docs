# Compilação em Tempo de Execução

> Status: Ausente de propósito.

Compilar código em tempo de execução — compilação JIT, `eval` ou gerar código de máquina enquanto o programa roda — **não é uma feature de DLang**. O núcleo da linguagem é AOT (ahead-of-time): um programa é totalmente compilado antes de rodar.

## Por que o núcleo é só AOT

Duas razões tornam a compilação em runtime um mau encaixe para uma linguagem de sistema:

1. **Tamanho do binário e custo previsível.** Embutir um compilador no binário final contradiz o objetivo de um executável pequeno com custo previsível e visível. Uma linguagem de sistema não deveria embarcar um gerador de código dentro de cada programa.
2. **A maioria da "geração de código" pertence ao compile-time.** Os casos para os quais as pessoas recorrem à compilação em runtime são resolvidos *antes* — em tempo de compilação — por `@comptime`, `#rodar` e macros (ver [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md) e [Macros e Expansão de Código](46-macros.md)). Esse trabalho tem custo zero em runtime.

## Não confundir compile-time com runtime

Vale ser preciso sobre as duas categorias, porque elas soam parecidas mas são opostas:

- **`#rodar` / `@comptime`** rodam no **compilador** (compile-time). São totalmente **suportados** — são como DLang gera código e dobra constantes antecipadamente.
- **JIT / `eval(string)`** compilam em **runtime**. **Não** são nativos da linguagem.

A presença de uma forte avaliação em compile-time é exatamente o que remove a necessidade de um compilador em runtime no caso comum.

## Um possível escape hatch futuro

Se um programa genuinamente precisar de compilação em runtime, o caminho é um **módulo opt-in da biblioteca padrão** que embute o compilador e expõe algo explícito — por exemplo um `Compilador.compilar(fonte)` que devolve um ponteiro de função gerado em runtime. Isso seria uma biblioteca pesada e claramente marcada, **jamais** parte do núcleo, e a imensa maioria dos programas nunca tocaria nisso.

```dlang
exemploHipotetico :: () {
  // val fn = Compilador.compilar("somar :: (a,b:int)->int = a+b")  // via lib, não núcleo
  // fn.value()
}
```

## Por quê

Manter o núcleo estritamente AOT preserva as duas propriedades que uma linguagem de sistema vende: binários pequenos e custo previsível. Como DLang já roda código arbitrário no compilador via `@comptime`, `#rodar` e macros, "gerar código a partir de dados" é resolvido antes do programa começar — sem custo em runtime. A compilação em runtime, portanto, é deixada de fora do núcleo de propósito, disponível, se algum dia for necessária, apenas como uma biblioteca explícita e pesada.

## Relacionados

- [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)
- [Macros e Expansão de Código](46-macros.md)

[← Índice](README.md)
