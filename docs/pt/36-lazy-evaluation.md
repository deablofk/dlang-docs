# Avaliação Preguiçosa

> Status: Parcial (apenas `lazy val` está implementado).

A avaliação preguiçosa em DLang tem duas faces. Uma é implementada e é o único mecanismo de preguiça ativo da linguagem: `lazy val`. A outra — iteradores lazy sobre coleções — é um desenho deliberadamente *parqueado* e está documentado aqui apenas como nota de referência futura. As coleções permanecem totalmente eager (ansiosas).

## Face 1 — `lazy val` (suportado)

Um `lazy val` não é calculado na sua declaração. Sua expressão de inicialização roda no **primeiro acesso** e, a partir daí, o resultado fica em cache (memoizado): leituras seguintes apenas devolvem o valor guardado.

```dlang
lazy val config = carregarConfig()   // carregarConfig() NÃO roda aqui

usar :: () {
  println(config.tema)     // <- carregarConfig() executa AGORA (primeiro acesso)
  println(config.idioma)   // <- já cacheado: não reexecuta, só lê
}
```

### Custo

O valor vive na pilha ao lado de uma flag interna "já-calculado?". No primeiro acesso a expressão roda, o resultado é guardado e a flag é marcada. Todo acesso posterior consulta a flag e lê o valor cacheado. Não há alocação na heap nem coletor de lixo envolvido — a preguiça aqui é um valor residente na pilha mais um booleano.

Isso faz do `lazy val` a ferramenta certa para um valor caro que talvez você não precise em todos os caminhos: você paga por ele uma única vez, somente se e quando ele for de fato lido.

## Face 2 — iteradores lazy (parqueado / não implementado)

> Status: Parcial — esta face é uma nota de design parqueada, não comportamento ativo.

`List`, `Map` e arrays permanecem **100% eager**. Nada nesta seção está ativo; é mantido apenas como registro do desenho para uma eventual reabertura futura.

### Como a distinção eager vs lazy funcionaria

A diferença entre eager e lazy *não* é uma palavra-chave. É ter ou não ter o **laço dentro do método**.

Um método **eager** — o comportamento atual de `List` — roda o `for` na hora e materializa um resultado:

```dlang
// EAGER (comportamento atual de List): o 'for' roda na hora e materializa
List(T).map(R) :: (f: (T) -> R) -> List(R) {
  var saida = List(R).init(_.alloc)
  for (item : _) saida.add(f(item))   // <- o trabalho acontece AQUI, na hora
  return saida
}
```

Um método **lazy** não teria laço algum. Ele apenas embrulharia a fonte e a função em uma pequena struct, adiando todo o trabalho para uma chamada `proximo()` que puxa um elemento de cada vez:

```dlang
// LAZY (parqueado): map NÃO tem laço. Só embrulha fonte + função numa struct.
Iter(T) :: interface {
  proximo :: () -> (T, boolean)   // (valor, temProximo)
}

Iter(T).map(R) :: (f: (T) -> R) -> Iter(R) {
  return MapIter(R) { fonte: _, f: f }   // <- zero trabalho, só guarda
}

MapIter(T, R).proximo :: () -> (R, boolean) {
  val (item, temMais) = _.fonte.proximo()   // puxa UM elemento da fonte
  if (!temMais) return (zero(R), false)
  return (f(item), true)                      // transforma só ESSE um
}
```

Como seria usado: `.iter()` entra no modo lazy, os estágios intermediários só *compõem*, e `.collect(alloc)` materializa uma vez, com uma única alocação:

```dlang
val resultado = nums
  .iter()                // entra no modo lazy — custo zero, nada alocado
  .filtrar { _ > 0 }     // só COMPÕE
  .map      { _ * 2 }    // idem
  .collect(_alloc)       // AQUI tudo é materializado, de uma vez
```

### Por que está parqueado

1. **Sem marcador explícito de preguiça.** O único sinal de que uma cadeia é lazy seria seu tipo de retorno (`Iter` vs `List`) — implícito demais para uma linguagem cujo princípio é "explícito sobre implícito".
2. **O "custo zero" depende do otimizador.** Fundir a cadeia de `proximo()` num único laço depende de monomorfização mais inlining. Sem um inlining maduro há overhead real de uma chamada de função por elemento — uma dívida que mora no backend do compilador, não no desenho de superfície.

Reabrir isso depois exigiria um marcador explícito `Lazy(T)` no tipo de retorno *e* um inliner maduro. Nunca seria o padrão, e nunca tocaria a API eager de `List`/`Map`.

## Por quê

`lazy val` ganha seu lugar porque seu custo é totalmente visível e residente na pilha: uma expressão, calculada no máximo uma vez, cacheada atrás de uma flag, sem heap. Os iteradores lazy foram contidos precisamente porque esconderiam tanto sua preguiça (atrás de um tipo de retorno) quanto sua garantia de desempenho (atrás de um passe do otimizador) — dois custos implícitos que a linguagem se recusa a entregar por padrão.

## Relacionados

- [Funções de Ordem Superior](35-higher-order-functions.md)
- [Arrays e listas](07-arrays-and-lists.md)
- [Variáveis e escopo](04-variables-and-scope.md)
- [Generics](32-generics.md)

[← Índice](README.md)
