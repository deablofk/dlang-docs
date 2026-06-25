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

## Por quê

Argumentos nomeados mais padrões substituem deliberadamente a sobrecarga de funções. Em vez de declarar três versões de `configurar` para cobrir os casos opcionais, você declara uma função e deixa o ponto de chamada expressar a intenção. Isso mantém a tabela de símbolos pequena e a resolução trivial — existe exatamente um `configurar`, então não há nada a desambiguar. Também se encaixa na filosofia **explícito > implícito**: um argumento nomeado afirma exatamente qual parâmetro ele preenche, sem deixar dúvida no ponto de chamada. Como tudo o mais em DLang, nenhuma conversão oculta acontece com os argumentos; valores são passados como seus tipos declarados, e uma incompatibilidade é um erro de compilação em vez de uma coerção silenciosa.

## Relacionados

- [Funções e procedimentos](09-functions.md)
- [Retorno de múltiplos valores](11-multiple-returns.md)
- [Ponteiros e referências](12-pointers-and-references.md)
- [Tipagem estática](29-static-typing.md)

[← Índice](README.md)
