# Ponteiros e Referências

Código de aplicação DLang **não tem ponteiros de primeira classe nem referências de primeira classe**. Essa frase é o design: sob Mutable Value Semantics puro (veja [Segurança de Memória](14a-memory-safety.md)), dado é valor, mutação passa pelo dono, e o aliasing que torna ponteiros perigosos é irrepresentável. Referências existem apenas em duas formas de segunda classe, controladas pelo compilador — convenções de parâmetro e projeções — e ponteiros crus existem apenas no *piso Builtin*, dentro das implementações auditadas dos tipos donos.

Esta página explica as três camadas: o que usar no lugar de um ponteiro, as duas formas seguras de referência, e o vocabulário cru `Ptr(T)` que você encontrará se implementar um handle dono ou fizer binding de C.

## O que substitui cada hábito de ponteiro

| Hábito de ponteiro | Substituto por valor |
|---|---|
| parâmetro de saída (`f(&result)`) | um parâmetro `set` — o chamado inicializa o slot do chamador in place |
| mutar a variável do chamador | um parâmetro `inout` — acesso exclusivo, com write-back |
| objeto de heap mutado à distância | um struct `nocopy` mutado pelos seus métodos |
| ponteiro para um elemento de contêiner | uma projeção — `xs.at(i).campo = v`, ou `inout e = xs.at(i)` |
| nós ligados, ciclos, grafos | `Pool(T)` + valores `Handle` copiáveis, ou índices `int` numa `List` append-only |
| acesso de leitura compartilhado | um struct de visão copiável |
| buffer de bytes passado adiante | um valor `string`, ou um `ByteBuf` dono (cruza FFI como `long` opaco) |

## Referências seguras nº 1 — convenções de parâmetro

`borrow` (o padrão), `inout`, `sink` e `set` criam as únicas referências que código comum toca, implicitamente, numa fronteira de chamada. Elas não podem ser armazenadas, retornadas nem sobreviver à chamada (`E_REF_ESCAPES`), e as mutáveis são exclusivas (`E_EXCLUSIVITY`). Deliberadamente não há `&` no call site — a assinatura do chamado carrega a convenção:

```dlang
rename :: (inout p: Pessoa, novo: string) { p.nome = novo }

var pessoa: Pessoa = Pessoa { nome: "Gabriel", idade: 25 }
rename(pessoa, "Bruno")     // sem &: a assinatura diz inout, o write-back é garantido
println(pessoa.nome)        // "Bruno"
```

Veja [Passagem de Parâmetros](10-parameter-passing.md) para a tabela completa de convenções.

## Referências seguras nº 2 — projeções (`yields`)

Uma projeção dá acesso in-place a um *elemento de um dono* — um slot de `List`, uma entidade de `Pool`, um campo de um dono aninhado — sem copiá-lo nem movê-lo. É produzida por um acessor `yields` e é agressivamente de segunda classe: use na expressão, ou segure brevemente num binding `inout` enquanto o compilador trava o dono.

```dlang
xs.at(i).hp = 99            // muta o elemento i in place (acesso a membro auto-dereferencia)

inout e = xs.at(i)          // segura a projeção por alguns statements
e.hp = e.hp - 10
e.nome = "ferido"
// xs fica travada enquanto e vive — usá-la aqui é E_EXCLUSIVITY,
// porque um crescimento poderia realocar e pender a projeção
```

Declare as suas com `yields`:

```dlang
Grid :: nocopy struct { cells: List(Cell)  width: int }
Grid.cell :: (x: int, y: int) yields Cell = _.cells.at(y * _.width + x).value

grid.cell(1, 1).v = 9      // escrita de membro com auto-deref, exatamente como List.at
```

Reter uma projeção de qualquer outro jeito — vinculá-la com `val`/`var`, armazená-la, retorná-la, passá-la a uma função comum — é `E_REF_ESCAPES`. Para ficar com um elemento, mova-o para fora (`xs.removeAt(i)`).

## O piso — `Ptr(T)`, `ref` e `.value` crus

Dentro do piso Builtin — os métodos de um handle dono `nocopy`+`deinit`, assinaturas extern C, a implementação da `string`, corpos `yields` e os hooks do runtime — o vocabulário cru está disponível, porque algo precisa implementar a `List` e conversar com C. Em qualquer outro lugar é `E_RAW_OUTSIDE_BUILTIN`. Veja [Memória Manual](13-manual-memory.md) para saber quando você tem permissão de estar aqui.

Um ponteiro é `Ptr(T)` — a mesma notação entre parênteses de `List(T)`. Você toma um endereço com `ref` e lê ou escreve o apontado através da única propriedade `.value`:

```dlang
// legal SOMENTE dentro dos métodos de um handle dono (ou no resto do piso):
val score: int = 99
val p: Ptr(int) = ref score     // endereço-de
p.value = 10                    // escreve através do ponteiro
println(p.value)                // 10
```

Afunilar toda dereferência por `.value` mantém cada acesso à memória explícito e dá ao piso um checkpoint visível por acesso — não há pontuação `*`/`&` nem dereferência implícita.

**Revincular versus mutar** continua sem ambiguidade: atribuição direta revincula o ponteiro, atribuição por `.value` muta o apontado.

```dlang
var a: int = 10
var b: int = 20
var pa: Ptr(int) = ref a
val pb: Ptr(int) = ref b
pa = pb          // revincula: pa agora aponta para b
pa.value = 50    // muta: escreve 50 em b
```

`null` é um valor válido de `Ptr(T)`, comparado direto com `==`/`!=`. `.value` encadeia em campos (`p.value.nome = "Gabriel"`) e `p[i]` indexa uma alocação de N elementos. **Não há verificação de limites nem de lifetime** no acesso cru — exatamente por isso a lei de fronteira o confina ao piso.

**FFI:** uma expressão `Ptr` pode fluir *diretamente* para um argumento extern C (um salto); qualquer coisa mais longeva cruza como `long` opaco (`ByteBuf.addr(i)`, `cast(long, s.cstr())`). Veja [Interop com C](50-c-interop.md).

## Ponteiros de função são diferentes

Um valor de função já carrega seu tipo chamável `(int, int) -> int`; não é um `Ptr(T)` e não se dereferencia com `.value`. Veja [Ponteiros de Função](33-function-pointers.md).

## Racional de design

Ponteiros ganham seu perigo de dois poderes: eles apelidam, e eles sobrevivem às coisas. DLang remove os dois do código de aplicação em vez de verificá-los — convenções e projeções dão os dois usos legítimos de uma referência (passar acesso para baixo, tocar um elemento in place) com escape e exclusividade impostos estaticamente, e todo ponteiro cru restante vive atrás da lei de fronteira, em código cujo trabalho é precisamente ser auditado. O resultado é layout de dados e FFI de nível C sem nenhum aliasing visível ao usuário.

## Relacionados

- [Segurança de Memória](14a-memory-safety.md)
- [Memória Manual — o piso Builtin](13-manual-memory.md)
- [Passagem de Parâmetros](10-parameter-passing.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Interop com C](50-c-interop.md)

[← Índice](README.md)
