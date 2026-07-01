# Documentação da DLang (Português)

**DLang** é uma linguagem de programação de sistema orientada a dados, inspirada
por Jai, Zig, Odin e Scala. Este é o índice completo de tópicos. _(Use o seletor
de idioma no topo para mudar para English.)_

## Filosofia de design

- **Orientada a dados, sem OOP** — sem classes, sem herança, sem vtables.
  Comportamento é *açúcar sintático sobre dados*; polimorfismo é feito com
  interfaces estruturais (fat pointers).
- **Explícito acima de implícito** — alocadores explícitos (`_alloc`, `_gcAlloc`),
  desreferência de ponteiro explícita via `.value`, executor de concorrência
  explícito (`_exec`), sem conversões numéricas implícitas, sem alocação de heap
  escondida.
- **Custo zero / static dispatch** — generics por monomorfização, interfaces como
  fat pointers, sobrecarga de operadores resolvida inteiramente em compile-time.
- **Ligações:** `::` liga uma constante de compile-time (função, tipo); `val` é uma
  ligação imutável de runtime; `var` é mutável; `const val` é constante verdadeira.
- **`_` é o placeholder universal** — `this`/`self` dentro de métodos, o argumento
  implícito em lambdas de um argumento, e o slot ignorado em padrões/desestruturação.
- **Superfície C-style, núcleo orientado a expressões** — `()` em condições e loops,
  chaves obrigatórias, mas `if`/`match` são expressões e funções podem ser `= expr`.
- **Concorrência library-first** — corrotinas, promises e canais vivem na biblioteca
  padrão; o compilador só expõe um intrínseco de troca de contexto e operações atômicas.
- **Metaprogramação unificada** — `@anotações` em declarações e `#diretivas` no ponto
  de uso dão poder a intrínsecos, execução em compile-time, reflexão e macros.

## Tópicos

### Fundamentos
1. [Tipos Primitivos](01-primitive-types.md)
2. [Literais de Texto](02-text-literals.md)
3. [Operadores Aritméticos](03-arithmetic-operators.md)
4. [Variáveis e Escopo](04-variables-and-scope.md)
5. [Estruturas Condicionais](05-conditionals.md)
6. [Loops e Iterações](06-loops.md)

### Estruturas de dados
7. [Arrays e Listas Nativas](07-arrays-and-lists.md)
8. [Tabelas e Dicionários](08-maps-and-dictionaries.md)
16. [Enumerações](16-enumerations.md)
17. [Estruturas de Dados Personalizadas (structs)](17-structs.md)

### Funções
9. [Funções e Procedimentos](09-functions.md)
10. [Passagem de Parâmetros](10-parameter-passing.md)
11. [Retorno de Múltiplos Valores](11-multiple-returns.md)
33. [Ponteiros de Função](33-function-pointers.md)
34. [Closures e Funções Anônimas](34-closures.md)
35. [Funções de Ordem Superior](35-higher-order-functions.md)
39. [Expressões Lambda](39-lambda-expressions.md)
50. [Interoperabilidade com C (FFI)](50-c-interop.md)

### Memória
12. [Ponteiros e Referências](12-pointers-and-references.md)
13. [Gerenciamento de Memória Manual](13-manual-memory.md)
14. [Coleta de Lixo Automática](14-garbage-collection.md)
18. [Alocação Dinâmica](18-dynamic-allocation.md)

### Tratamento de erros & módulos
15. [Tratamento de Erros](15-error-handling.md)
19. [Módulos e Namespaces](19-modules-and-namespaces.md)

### Tipos & contratos (o modelo "sem OOP")
20. [Classes e Objetos](20-classes-and-objects.md)
21. [Construtores e Destrutores](21-constructors-and-destructors.md)
22. [Encapsulamento e Modificadores de Acesso](22-encapsulation.md)
23. [Herança Simples](23-single-inheritance.md)
24. [Herança Múltipla](24-multiple-inheritance.md)
25. [Interfaces e Classes Abstratas](25-interfaces.md)
26. [Polimorfismo](26-polymorphism.md)
27. [Sobrecarga de Operadores](27-operator-overloading.md)
28. [Métodos Virtuais](28-virtual-methods.md)

### Sistema de tipos
29. [Tipagem Estática](29-static-typing.md)
30. [Tipagem Dinâmica](30-dynamic-typing.md)
31. [Inferência de Tipos](31-type-inference.md)
32. [Generics e Programação Paramétrica](32-generics.md)
48. [Sistema de Tipos Dependentes](48-dependent-types.md)
49. [Prova de Teoremas em Tempo de Compilação](49-theorem-proving.md)

### Programação funcional
36. [Avaliação Preguiçosa](36-lazy-evaluation.md)
37. [Casamento de Padrões](37-pattern-matching.md)
38. [Tuplas e Desestruturação](38-tuples-and-destructuring.md)
40. [Compreensão de Listas](40-list-comprehension.md)

### Concorrência
41. [Multithreading e Concorrência](41-concurrency.md)
42. [Corotinas e Promises](42-coroutines-and-promises.md)
43. [Programação Assíncrona (async/await)](43-async-await.md)
44. [Canais e Passagem de Mensagens](44-channels.md)

### Metaprogramação
45. [Metaprogramação e Reflexão](45-metaprogramming-and-reflection.md)
46. [Macros e Expansão de Código](46-macros.md)
47. [Compilação em Tempo de Execução](47-runtime-compilation.md)
