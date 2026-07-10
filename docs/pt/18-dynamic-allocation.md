# Alocação Dinâmica

A alocação dinâmica reserva memória na heap em tempo de execução, para dados cujo tamanho ou tempo de vida não é conhecido em tempo de compilação. Em DLang não há `new` oculto nem boxing implícito — mas você também não passa um alocador por cada chamada. Em vez disso, a alocação é **ambiente**: toda alocação na heap vem do *alocador atual*, um valor trocável mantido em um contexto por-programa. Esse é o modelo popularizado por Jai.

## Alocando um único valor

Para colocar um valor na heap, chame `New(T)`. Ele retorna um `Ptr(T)` — um ponteiro cujo conteúdo você acessa por `.value`:

```dlang
Pessoa :: struct {
  nome: string
  idade: int
}

criarInimigo :: () {
  val inimigo: Ptr(Pessoa) = New(Pessoa)
  defer Undo(inimigo)

  inimigo.value.nome = "Orc"
  inimigo.value.idade = 150
}
```

`New(T, n)` aloca `n` valores contíguos em vez de um. `defer Undo(p)` agenda a liberação correspondente quando a função encerra, mantendo alocação e liberação visivelmente pareadas. (`New` / `Undo` são as escritas legíveis de `_alloc.alloc(T)` / `_alloc.free(p)` de baixo nível; ambas passam pelo alocador atual.)

## Contêineres que crescem

Tipos de contêiner como `List(T)` e `Map(K, V)` alocam seu armazenamento de base dinamicamente, mas cuidam da contabilidade para você. Você **não** entrega um alocador a eles — eles puxam do mesmo contexto ambiente que toda alocação usa:

```dlang
gerenciarInventario :: () {
  var itens: List(string) = List(string).empty()

  itens.add("Espada")
  itens.add("Escudo")
  itens.add("Poção")
}
```

`List(string).empty()` cria uma lista vazia que cresce na heap conforme você faz `add`; `Map(K, V).empty()` se comporta do mesmo jeito. O crescimento interno flui por qualquer que seja o alocador atual, então redirecioná-los é questão de instalar um alocador diferente — não de editar seus pontos de chamada.

## O alocador atual

Um `Allocator` é um único procedimento mais seus dados privados:

```dlang
Allocator :: struct {
  proc: (Ptr(byte), AllocationType, long, Ptr(byte)) -> Ptr(byte)
  data: Ptr(byte)
}
```

`context()` retorna o alocador ativo. `mallocAllocator()` é o padrão (baseado na libc). Você instala outro para uma região de código e o restaura depois:

```dlang
val prev: Allocator = pushAllocator(meuAlocador)
// ... toda alocação de New / string / List / Map aqui usa meuAlocador ...
popAllocator(prev)
```

Como o alocador é ambiente, uma função auxiliar que você chama aloca no alocador que estiver ativo na chamada — sem um parâmetro de alocador a repassar. Essa é a diferença chave do estilo "passe o alocador explicitamente": a estratégia vive em um único lugar, não espalhada por cada assinatura.

## O alocador de depuração

`debugAllocator` envolve qualquer alocador de base, rastreia cada bloco vivo, reporta liberações duplas / inválidas na hora, e deixa `debugReport` listar vazamentos. Instale-o enquanto desenvolve; omita-o em release para custo zero:

```dlang
val prev: Allocator = pushAllocator(debugAllocator(mallocAllocator()))

val a: Ptr(int) = New(int)
Undo(a)
Undo(a)   // reportado como liberação dupla

debugReport(context().value)      // alocações / liberações / vazadas / liveBytes / erros
popAllocator(prev)
```

## Escrevendo seu próprio alocador

Qualquer valor do tipo `Allocator` funciona — um `proc` que trata `AllocationType.ALLOCATE` (retornar `size` bytes) e `AllocationType.FREE` (liberar `oldPtr`), mais o `data` de que seu alocador precisar. Isso deixa você encaixar uma arena, um pool ou um alocador contador e fazer o programa inteiro — biblioteca padrão incluída — usá-lo, apenas empurrando-o no contexto.

## Justificativa de design

A alocação ambiente mantém as duas coisas que um programador de sistemas quer em tensão — controle e conveniência — ambas satisfeitas. Controle: toda alocação continua explícita (`New`, ou um método de contêiner que claramente aloca), e você sempre pode ver e substituir o alocador. Conveniência: você não polui cada assinatura de função com um parâmetro de alocador, e pode mudar a estratégia de memória de um subsistema inteiro a partir de um só lugar. Contêineres como `List` e `Map` não precisam de suporte especial do compilador — são structs genéricos comuns que alocam pelo mesmo contexto que todo o resto.

## Relacionados

- [Memória manual](13-manual-memory.md)
- [Coleta de lixo](14-garbage-collection.md)
- [Ponteiros e referências](12-pointers-and-references.md)
- [Structs](17-structs.md)
- [Arrays e listas](07-arrays-and-lists.md)

[← Índice](README.md)
