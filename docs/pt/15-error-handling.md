# Tratamento de Erros

DLang não tem exceções no sentido de lançar-e-desempilhar. Erros são valores comuns retornados ao lado do resultado. Uma função falível é marcada com `throws` na assinatura e, por convenção, o erro é sempre o *último* valor que ela retorna; um erro `null` significa "deu tudo certo". Isso mantém o tratamento de erros explícito e orientado a dados — um erro é apenas dado fluindo de volta por um retorno, nunca um salto de fluxo de controle escondido para fora da função.

Há duas formas de consumir uma chamada falível: a checagem manual, e um bloco `try`/`catch` que é puro açúcar sintático sobre essa checagem manual.

## Definindo os erros

Erros são tipicamente modelados como um [enum](16-enumerations.md), então o conjunto de modos de falha é uma lista fechada e nomeada sobre a qual o compilador pode raciocinar.

```dlang
// definição dos erros
Erro :: enum {
  ArquivoNaoEncontrado,
  PermissaoNegada
}
```

## Uma função que pode falhar

A palavra-chave `throws` na assinatura de retorno marca uma função como falível. Como o erro é o último valor, a leitura natural de `-> throws (string, Erro)` é "retorna uma string em caso de sucesso, com `Erro` como seu canal de erro". No sucesso você retorna o valor mais `null`; na falha você retorna um valor de preenchimento mais o erro.

```dlang
// função com retorno de erro
// erro é sempre a ultima variavel por causa do 'throws'
lerArquivo :: (caminho: string) -> throws (string, Erro) {
  if (caminho == "") {
    return "", Erro.ArquivoNaoEncontrado
  }

  return "conteudo do arquivo aqui", null
}
```

O par `(string, Erro)` é exatamente uma tupla — o mesmo mecanismo descrito em [Retorno de Múltiplos Valores](11-multiple-returns.md) e [Tuplas e Desestruturação](38-tuples-and-destructuring.md). O tratamento de erros reaproveita essa maquinaria em vez de inventar uma nova.

## Forma 1: checagem manual

O estilo mais direto desestrutura a tupla retornada em um valor e um erro, depois testa o erro contra `null`. É ideal quando você quer tratar uma falha isolada, bem onde ela acontece.

```dlang
// Forma 1: Checagem Manual (útil para tratar erros isolados)
val conteudo, err = lerArquivo("config.txt")

if (err != null) {
  println("Nao foi possivel ler o arquivo: ${err}")
  return
}
println(conteudo)
```

Nada está escondido aqui: o erro é uma variável normal, o `if` é um condicional normal, e o fluxo de controle é totalmente visível. O custo é a verbosidade quando você encadeia várias chamadas falíveis em sequência.

## Forma 2: o bloco `try`/`catch`

Quando você quer encadear muitas operações sem um `if` depois de cada uma, o bloco `try`/`catch` oferece açúcar sobre o padrão manual. O compilador sabe que cada função chamada tem `throws`, então dentro do `try` ele extrai automaticamente o valor de sucesso para sua variável e gera invisivelmente a checagem de erro nos bastidores. Se qualquer chamada retornar um erro diferente de nulo, a execução pula direto para o `catch`.

```dlang
// Forma 2: o bloco Try-Catch Híbrido (Açúcar Sintático)
// Útil para encadear várias operações sem poluir o código com 'ifs'
try {
  // O compilador sabe que a função tem 'throws'.
  // Ele extrai o valor de sucesso diretamente para 'config'
  // e gera o 'if' de checagem do erro invisivelmente nos bastidores.
  val config = lerArquivo("config.txt")
  val extra  = lerArquivo("theme.txt")

  // Se qualquer chamada acima retornar um Erro diferente de null,
  // a execução pula imediatamente para o bloco catch.
  println("Configurações carregadas com sucesso!")
  println(config)

} catch (err) {
  // A variável 'err' é injetada automaticamente aqui pelo compilador
  println("Um erro interrompeu o bloco try: ${err}")
}
```

Note que `val config = lerArquivo("config.txt")` dentro do `try` liga o valor de *sucesso* diretamente, não a tupla `(valor, erro)` — a desaçucaração do `try` descasca o erro por você e curto-circuita para o `catch` no primeiro não-nulo. O parâmetro `err` do `catch` é injetado pelo compilador.

Como a Forma 2 compila exatamente para o padrão da Forma 1, as duas são semanticamente idênticas; `try`/`catch` é apenas a escolha ergonômica quando vários passos falíveis precisam acontecer em sequência.

## Casando com o erro

Como `Erro` é um enum, um erro recuperado pareia naturalmente com [`match`](05-conditionals.md) para ramificar conforme a falha específica:

```dlang
match (err) {
  Erro.ArquivoNaoEncontrado -> println("arquivo sumiu")
  Erro.PermissaoNegada      -> println("acesso negado")
  else -> println("ok")
}
```

## Por quê

Erros-como-valores mantêm DLang honesta: a assinatura de uma função conta toda a verdade sobre como ela pode falhar, e a convenção `throws`/último-valor torna o canal de erro inconfundível sem inventar uma disciplina de tipos separada. Ao construir sobre tuplas e enums — recursos que a linguagem já tem para [retornos múltiplos](11-multiple-returns.md) e [enumerações](16-enumerations.md) — o tratamento de erros não adiciona nova maquinaria de runtime nem desempilhamento de pilha escondido. O bloco `try`/`catch` então adiciona conveniência por cima *apenas como açúcar*, então você ganha encadeamento legível sem jamais abrir mão da garantia de que o fluxo de controle é explícito e inspecionável.

## Relacionados

- [Enumerações](16-enumerations.md)
- [Retorno de Múltiplos Valores](11-multiple-returns.md)
- [Tuplas e Desestruturação](38-tuples-and-destructuring.md)

[← Índice](README.md)
