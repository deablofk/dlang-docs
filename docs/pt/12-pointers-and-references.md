# Ponteiros e Referências

Um ponteiro é um valor que guarda o endereço de memória de outro valor. Em DLang os ponteiros são um tipo comum e de primeira classe, escrito `Ptr(T)` — a mesma notação entre parênteses usada por `List(T)` e `cast(T, x)`. Não há pontuação especial `*` ou `&`: você toma uma referência com a palavra-chave `ref` e lê ou escreve o conteúdo apontado através de uma única propriedade, `.value`.

Esse desenho é deliberado. Centralizar todo acesso à memória em `.value` dá ao compilador um ponto de validação de segurança perfeito (como checagem de nulo), que é o principal mecanismo que DLang usa para evitar as falhas de segmentação repentinas que assolam C e C++.

## Tomando uma referência

Você obtém um ponteiro para uma variável existente com `ref`. O resultado tem o tipo `Ptr(T)`, onde `T` é o tipo daquilo para o qual você apontou.

```dlang
val score: int = 99

// equivalente ao antigo sintaxe C *int = &score
val ponteiroScore: Ptr(int) = ref score
```

`ref score` não copia `score`; ele produz o endereço dele. `ponteiroScore` agora se refere à mesma célula de armazenamento.

## Lendo e escrevendo através de `.value`

Todo `Ptr` tem uma propriedade `.value`. Essa é a única forma de desreferenciar — de ler ou alterar aquilo que o ponteiro aponta.

```dlang
// para mudar o valor do ponteiro usa .value, todo Ptr tem o .value
ponteiroScore.value = 10
println(ponteiroScore.value) // 10
```

Como o acesso é canalizado por `.value`, o compilador sempre sabe exatamente onde ocorre uma desreferência. Se um ponteiro for nulo, o compilador pode emitir um erro seguro e bem definido no acesso a `.value` em vez de deixar o programa quebrar com um segfault imprevisível.

## Rebind versus mutação

A distinção mais importante de todas com ponteiros é entre *mudar para qual célula um ponteiro se refere* e *mudar o conteúdo da célula a que ele se refere atualmente*. DLang torna isso completamente sem ambiguidade: a atribuição simples faz rebind do ponteiro, enquanto a atribuição via `.value` altera o conteúdo apontado.

```dlang
var a: int = 10
var b: int = 20

val ptrA: Ptr(int) = ref a
val ptrB: Ptr(int) = ref b

// rebind: ptrA agora guarda o mesmo endereço que ptrB
ptrA = ptrB      // mesmo endereço para os dois ('b')

// mutação: escreve através do ponteiro na célula original
ptrA.value = 50  // muda o valor da gaveta original que ele aponta
```

Depois de `ptrA = ptrB`, os dois ponteiros são apelidos do mesmo armazenamento. O `ptrA.value = 50` seguinte, portanto, escreve `50` na célula que ambos agora referenciam. Ler o nome puro do ponteiro compara ou copia endereços; recorrer a `.value` sempre toca os dados subjacentes.

## Ponteiros para structs

`.value` encadeia naturalmente no acesso a campos, então um ponteiro para uma struct permite alterar campos no lugar:

```dlang
val pessoaPtr: Ptr(Pessoa) = _alloc.alloc(Pessoa)
pessoaPtr.value.nome = "Gabriel" // altera o campo dentro da struct
```

Aqui `_alloc.alloc(Pessoa)` retorna um `Ptr(Pessoa)` apontando para memória recém-reservada. Veja [Gerenciamento de Memória Manual](13-manual-memory.md) para como essa alocação é pareada com `defer _alloc.free(...)`.

## Ponteiros de função são diferentes

Um ponteiro para uma função *não* é um `Ptr(T)` e *não* é desreferenciado com `.value`. Um valor de função já carrega seu tipo chamável `(int, int) -> int`, então você o chama diretamente. Só ponteiros para *dados* usam `.value`. Esse tópico é coberto em Ponteiros de Função.

## Por quê

DLang trata ponteiros como dados puros, coerente com sua filosofia orientada a dados: sem indireção escondida, sem desreferência implícita. A palavra-chave `ref` torna visível a tomada de endereço, e `.value` torna visível a desreferência. Ao forçar toda leitura e escrita por uma propriedade, a linguagem ganha um lugar único e barato para validar segurança — transformando a operação mais perigosa da programação de sistemas em um ponto de controle que o compilador domina. Rebind versus mutação, que é silencioso e propenso a erros em C, torna-se duas operações visivelmente diferentes.

## Relacionados

- [Gerenciamento de Memória Manual](13-manual-memory.md)
- [Coleta de Lixo Automática](14-garbage-collection.md)
- [Alocação Dinâmica](18-dynamic-allocation.md)
- [Estruturas de Dados](17-structs.md)

[← Índice](README.md)
