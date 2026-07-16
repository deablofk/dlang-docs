# Passagem de Parâmetros

Uma vez definida uma função (veja [Funções e procedimentos](09-functions.md)), você a chama fornecendo argumentos. DLang suporta argumentos **posicionais**, argumentos **nomeados** e valores **padrão**, e esses três se combinam para dar pontos de chamada flexíveis e legíveis sem precisar de sobrecarga de funções.

## Argumentos posicionais

A chamada mais simples passa os argumentos na ordem de declaração. Cada valor é casado com o parâmetro na mesma posição:

```dlang
val a: int = 10

funcaoNome :: (parametroUm: int) -> int = parametroUm

funcaoNome(a)
```

O argumento `a` cai em `parametroUm` porque está na primeira (e única) posição. A chamada posicional é concisa e é a escolha certa quando a ordem dos parâmetros é óbvia pelo contexto.

## Argumentos nomeados

Em vez disso, você pode endereçar um parâmetro pelo nome usando `parametroNome = valor` no ponto de chamada. Isso é valioso quando uma função tem parâmetros opcionais e você quer definir um sem fornecer os outros, ou simplesmente para tornar a chamada autodocumentada:

```dlang
funcaoNome :: (parametroUm: int = 10, parametroDois: int) -> int = parametroUm + parametroDois

funcaoNome(parametroDois = a)
```

Aqui `parametroUm` já tem um padrão de `10`, e quem chama só precisa fornecer `parametroDois`. Ao nomeá-lo explicitamente, a chamada pula direto para o parâmetro que importa — `parametroUm` mantém seu padrão, e o resultado é `10 + a`. Sem argumentos nomeados você não conseguiria "pular por cima" do parâmetro com padrão.

## Combinando padrões, posicionais e nomeados

Valores padrão (cobertos em [Funções e procedimentos](09-functions.md)) são o que torna os argumentos nomeados poderosos. Um parâmetro com padrão pode ser omitido por completo; um parâmetro sem padrão deve ser fornecido, seja posicionalmente ou por nome. Um padrão comum e legível é passar os argumentos obrigatórios posicionalmente e recorrer a argumentos nomeados apenas ao sobrescrever um parâmetro opcional específico:

```dlang
configurar :: (host: string, porta: int = 8080, tls: boolean = false)

configurar("localhost")                 // porta=8080, tls=false
configurar("localhost", tls = true)     // pula porta, nomeia tls
configurar("localhost", 9090)           // porta=9090 posicionalmente
```

## Convenções de parâmetro — o que o chamado pode FAZER com o argumento

Independente de *como* um argumento é casado (por posição ou por nome), uma palavra-chave opcional antes do nome do parâmetro declara o que a função faz com ele. Essa é toda a história de referências da DLang — não há `&` no call site, e a convenção é imposta pelo compilador ([Segurança de Memória](14a-memory-safety.md)):

| Convenção | Acesso do chamado | Posse |
|---|---|---|
| `borrow` (padrão, não escrito) | só leitura | o chamador mantém |
| `inout` | leitura-escrita exclusiva, **com write-back** | o chamador mantém e vê a mutação |
| `sink` | total | transfere-se ao chamado (o argumento é consumido) |
| `set` | escreve-primeiro: começa **não inicializado**, deve ser atribuído em todo caminho | o chamador fica com o resultado inicializado |

```dlang
peek    :: (p: Pessoa) -> string = p.nome            // borrow: só leitura
rename  :: (inout p: Pessoa, novo: string) { p.nome = novo }
adopt   :: (sink xs: List(int)) -> int = xs.size()   // consome a lista
split   :: (s: string, set head: string, set tail: string) { ... }  // slots de saída

var pessoa: Pessoa = Pessoa { nome: "Gabriel", idade: 25 }
rename(pessoa, "Bruno")      // pessoa.nome é "Bruno" depois da chamada
```

As regras, em resumo (cada uma é erro de compilação, não surpresa de runtime):

- Um parâmetro simples é **imutável** — atribuir a ele ou através dele é `E_IMMUTABLE`. Valores copiáveis chegam como cópias por valor; valores `nocopy` chegam como borrows só-leitura.
- Um argumento `inout` precisa ser um lvalue mutável enraizado num `var`, e dois argumentos `inout` não podem apelidar o mesmo armazenamento (`E_EXCLUSIVITY` — a Lei da Exclusividade).
- Um argumento `sink` é um **move**: para um tipo `nocopy` o binding do chamador é consumido, e usá-lo depois é `E_USE_AFTER_MOVE`.
- Um slot `set` deve ser atribuído em todo caminho do chamado (`E_SET_UNASSIGNED`) e não pode ser lido antes da primeira atribuição (`E_SET_BEFORE_ASSIGN`). Ele substitui o hábito C de passar um ponteiro para o chamado preencher.
- Nenhuma convenção deixa uma referência escapar: retornar ou guardar um parâmetro emprestado é `E_REF_ESCAPES`.

## Por quê

Argumentos nomeados mais padrões substituem deliberadamente a sobrecarga de funções. Em vez de declarar três versões de `configurar` para cobrir os casos opcionais, você declara uma função e deixa o ponto de chamada expressar a intenção. Isso mantém a tabela de símbolos pequena e a resolução trivial — existe exatamente um `configurar`, então não há nada a desambiguar. Também se encaixa na filosofia **explícito > implícito**: um argumento nomeado afirma exatamente qual parâmetro ele preenche, sem deixar dúvida no ponto de chamada. Como tudo o mais em DLang, nenhuma conversão oculta acontece com os argumentos; valores são passados como seus tipos declarados, e uma incompatibilidade é um erro de compilação em vez de uma coerção silenciosa. As convenções completam o quadro tornando o *efeito* sobre cada argumento parte da assinatura: um call site nunca precisa de `&` nem de comentário para dizer quais argumentos podem mudar — a declaração da função já disse, e o compilador a mantém fiel a isso.

## Relacionados

- [Funções e procedimentos](09-functions.md)
- [Retorno de múltiplos valores](11-multiple-returns.md)
- [Ponteiros e referências](12-pointers-and-references.md)
- [Segurança de Memória](14a-memory-safety.md)
- [Tipagem estática](29-static-typing.md)

[← Índice](README.md)
