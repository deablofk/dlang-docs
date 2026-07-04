# Formatação de Código (dfmt)

A DLang inclui um único formatador canônico, o **dfmt**, para que todo programa DLang no mundo tenha a mesma aparência. Não há estilo para configurar nem opções para debater: uma entrada tem exatamente uma saída formatada. O formatador é um pretty-printer baseado em AST — ele faz o parse do código para a árvore de sintaxe não-tipada e o re-emite do zero — de modo que ele *impõe* o layout, em vez de apenas arrumar espaços em branco.

Como trabalha a partir da árvore de parse, o dfmt **se recusa a mexer em um arquivo que não faz parse**. Um erro de sintaxe é reportado e o arquivo é deixado intacto, em vez de arriscar corrompê-lo. A formatação é, portanto, sempre segura: ela só pode produzir código válido e equivalente.

## Executando o formatador

```bash
python -m tasty.format file.dlang            # imprime o código formatado no stdout
python -m tasty.format -i file.dlang ...     # reescreve os arquivos no lugar
python -m tasty.format --check file.dlang    # sai com código != 0 se um arquivo não estiver formatado
python -m tasty.format -                     # formata stdin -> stdout
```

Com múltiplos arquivos, `-i`/`--check` se aplicam a cada um; sem nenhum dos dois, o texto formatado de todos os arquivos é concatenado no stdout. `--check` é o que você conecta na CI — ele não escreve nada e falha se algum arquivo ainda não estiver formatado. `-i` e `--check` são mutuamente exclusivos.

## Garantias

O dfmt faz três promessas, cada uma verificada por sua suíte de testes (testes unitários mais uma passada de corpus sobre todo arquivo `*.dlang` do repositório):

- **Idempotente** — `format(format(x)) == format(x)`. Rodar duas vezes nunca muda nada que a primeira passada produziu.
- **Preserva comentários** — nenhum texto de comentário é jamais perdido. Os comentários são recuperados por uma varredura independente do código bruto (o lexer os descarta) e reanexados à declaração à qual pertencem.
- **Preserva semântica** — a saída sempre faz parse de novo, e a precedência é preservada por parênteses, então o significado nunca muda.

## O estilo

### Indentação e largura

Indentação de dois espaços, mirando uma largura de **120 colunas**. Construções que cabem ficam em uma linha; apenas as que ultrapassariam 120 colunas são quebradas.

### Controle de fluxo em blocos

Todo `if` / `else` / `while` / `for` / `match` / `try` em **posição de statement** é expandido para chaves em suas próprias linhas — o dfmt nunca emite um corpo de statement inline. O mesmo vale para `if` e `match` usados em **posição de valor**: eles expandem para a forma de bloco em vez de ficar em uma linha só.

```dlang
pick :: (a: int, b: int) -> int = if (a > b) {
  a
} else {
  b
}
```

Um corpo de função que é uma única expressão simples mantém a forma inline `= expr`; apenas valores de controle de fluxo expandem.

### Parâmetros agrupados expandem

Parâmetros que compartilham um tipo no código-fonte (`(a, b: int)`) são sempre escritos por extenso, para que cada nome carregue sua própria anotação:

```dlang
add :: (a: int, b: int) -> int = a + b
```

### Um membro por linha

Corpos de struct, enum e interface são dispostos com um membro por linha. Chamadas longas, arrays, tuplas, literais de struct, literais de map e listas de parâmetros que ultrapassariam 120 colunas quebram em **um elemento por linha**:

```dlang
build :: () = createWidget(
  titleText,
  widthInPixels,
  heightInPixels,
  backgroundColor,
  borderColor,
  isVisibleFlag,
  zIndexValue
)
```

### Literais e pequenos detalhes

- Literais folha — inteiros, doubles, chars, strings — são copiados **verbatim** do código, então separadores de dígitos (`1_000_000`), interpolação de string (`${x}`), escapes e strings com aspas triplas nunca são perturbados.
- Ranges são escritos justos: `0..count`, não `0 .. count`.
- Um trailing lambda descarta os parênteses vazios: `xs.map { ... }`, nunca `xs.map() { ... }`.
- As palavras-chave de ligação são normalizadas: `const` vira `const val` e `lazy` vira `lazy val`.

### Comentários

Uma única linha `//` é mantida como está. Uma **sequência de dois ou mais comentários `//` em linha própria vira um bloco `/* ... */`**, já que `//` fica melhor para uma única linha:

```dlang
/*
  first
  second
  third
*/
```

Blocos `/* */` existentes são preservados, e um comentário `//` no fim da linha permanece anexado à sua linha.

## Agrupando métodos sob seu tipo

Um método — uma definição cujo alvo é `Owner.name` — é **reordenado para ficar logo depois da definição do tipo ao qual pertence**, não importa onde você o escreveu no arquivo. Os métodos mantêm sua ordem relativa original, e cada um leva junto seu doc-comment. Isso significa que você pode adicionar um método em qualquer lugar enquanto edita, e o dfmt o arquiva no lugar certo.

Dada uma entrada em que a struct e seus métodos estão espalhados:

```dlang
Writer.close :: () -> throws (IOError)

Box :: struct { value: int }

Writer.write :: (n: int) -> throws (int, IOError)

Writer :: struct { fd: int }
```

o dfmt agrupa cada tipo com seus métodos:

```dlang
Box :: struct {
  value: int
}

Box.get :: () -> int

Writer :: struct {
  fd: int
}

Writer.close :: () -> throws (IOError)

Writer.write :: (n: int) -> throws (int, IOError)
```

Apenas métodos cujo tipo dono é definido **no mesmo arquivo** são realocados. Um método sobre um tipo declarado em outro lugar é deixado exatamente onde você o colocou (então métodos estilo extensão em outro módulo ficam parados).

A reordenação se aplica em *contextos de declaração* — o nível superior de um módulo e o corpo de um `namespace`. Ela nunca reordena statements dentro do corpo de uma função, onde a ordem importa.

## Alinhamento vertical

Definições consecutivas são alinhadas para que seus `::` fiquem em coluna, formando uma coluna limpa. O dfmt alinha uma **sequência (run)** de definições de função adjacentes que compartilham o mesmo dono e o mesmo formato (todas assinaturas, todas com corpo de expressão, ou todas com corpo de bloco). Uma definição que carrega seu próprio comentário anterior inicia uma nova sequência.

```dlang
read  :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
write :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
close :: (fileDescriptor: int) -> long
fsync :: (fileDescriptor: int) -> int
```

O mesmo alinhamento se aplica ao grupo de métodos de um tipo, e os parâmetros genéricos fazem parte do alvo alinhado:

```dlang
Writer.write       :: (bytes: Ptr(byte), count: int) -> throws (int, IOError)

Writer.writeString :: (str: string) -> throws (int, IOError)

Writer.writeByte   :: (byt: byte) -> throws (IOError)

Writer.print(T)    :: (x: T)

Writer.println(T)  :: (x: T)

Writer.flush       :: () -> throws (IOError)  // fsync

Writer.close       :: () -> throws (IOError)
```

O alinhamento não se limita a funções. Dentro do corpo de uma struct, enum ou interface, o dfmt alinha os membros quando a lista é uniforme:

- **campos de struct** alinham seus `:`
- **métodos de interface** alinham seus `::`
- **variantes de enum** com valores explícitos alinham seus `=`

```dlang
Token :: enum {
  Plus  = 1
  Minus = 2
  Star  = 3
}
```

## Linhas em branco entre definições

O espaçamento entre duas definições adjacentes é decidido pelo *tipo* de definição que elas são, não por quantas linhas em branco você digitou. Dentro de uma sequência de definições relacionadas:

| Tipo de definição | Espaçamento |
|---|---|
| Implementação com corpo de bloco (`f :: () { ... }`) | uma linha em branco entre cada |
| **Assinatura** de método (`Writer.write :: ...`, com dono) | uma linha em branco entre cada |
| **Assinatura** livre / externa (`read :: ...`, sem dono) | justo — sem linha em branco |
| Corpo de expressão (`f :: () = expr`) | justo — sem linha em branco |

Grupos não-relacionados — um tipo e seu bloco de métodos, ou dois donos diferentes — são sempre separados por uma única linha em branco. O efeito é que uma tabela de assinaturas externas de C fica compacta, enquanto os métodos de um tipo respiram:

```dlang
read  :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long
write :: (fileDescriptor: int, buffer: Ptr(byte), count: long) -> long

Writer :: struct {
  fileDescriptor: int
}

Writer.write       :: (bytes: Ptr(byte), count: int) -> throws (int, IOError)

Writer.writeString :: (str: string) -> throws (int, IOError)
```

## Limitações conhecidas

Algumas construções são intencionalmente deixadas como você as escreveu:

- Expressões **binárias / booleanas** longas não são quebradas; apenas contêineres quebráveis (chamadas, arrays, tuplas, literais de struct/map, listas de parâmetros) são.
- Um comentário que fica **dentro de uma expressão quebrada** se reancora à fronteira de statement mais próxima, em vez de permanecer no meio da expressão.
- **Lambdas com múltiplos statements** são mantidos inline.

## Justificativa de design

Um único formato canônico remove uma categoria inteira de decisões e diffs do trabalho do dia a dia: não há nada para discutir em code review, e uma reformatação nunca esconde uma mudança real sob ruído de espaços em branco. Construir o formatador sobre a árvore de parse — em vez de sobre tokens ou regexes — é o que permite que ele faça mais do que reindentar: ele pode, com segurança, reordenar métodos sob seu tipo e alinhar colunas, porque entende a estrutura que está imprimindo. As regras de agrupamento e alinhamento existem para que a forma do código espelhe a forma dos dados: um tipo e tudo que age sobre ele lêem-se como um bloco visual, e uma coluna de `::` alinhados transforma uma lista de declarações em uma tabela que você varre num relance.

## Relacionados

- [Funções e Procedimentos](09-functions.md)
- [Estruturas de Dados Customizadas (structs)](17-structs.md)
- [Enumerações](16-enumerations.md)
- [Interfaces e Classes Abstratas](25-interfaces.md)
- [Módulos e Namespaces](19-modules-and-namespaces.md)
- [Interoperabilidade com C (FFI)](50-c-interop.md)

[← Índice](README.md)
