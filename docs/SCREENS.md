# SCREENS.md

# Tela 01 - Login

## Objetivo

Permitir autenticação dos usuários.

## Campos

* E-mail
* Senha

## Ações

* Entrar

## Regras

* Apenas usuários ativos podem acessar o sistema.

---

# Tela 02 - Dashboard

## Objetivo

Apresentar visão geral das vendas.

## Indicadores

### Hoje

* Quantidade de vendas
* Valor vendido
* Total de passageiros

### Mês Atual

* Quantidade de vendas
* Valor vendido
* Valor de comissão

### Próximos Embarques

* Data
* Horário
* Passeio
* Contratante

### Pendências

* Pagamentos pendentes
* Passeios sem comprovante

---

# Tela 03 - Listagem de Vendas

## Objetivo

Consultar vendas cadastradas.

## Filtros

* Contratante
* Telefone
* Passeio
* Status
* Data Inicial
* Data Final

## Colunas

* Número
* Contratante
* Passeio
* Data Saída
* Valor
* Comissão
* Status

## Ações

* Visualizar
* Editar
* Cancelar

---

# Tela 04 - Nova Venda

## Objetivo

Cadastrar venda de passeio.

## Campos

### Contratante

* Nome
* Telefone

### Passageiros

* Adultos
* Crianças

### Passeio

* Passeio
* Tipo de Passeio
* Embarcação

### Financeiro

* Valor Total

### Saída

* Data
* Horário

### Outros

* Observação

## Campos Calculados

* Percentual Comissão
* Valor Comissão

## Ações

* Salvar
* Salvar e Anexar Comprovante

---

# Tela 05 - Detalhes da Venda

## Objetivo

Visualizar informações completas.

## Exibir
 
* Todos os dados da venda
* Comprovantes anexados
* Histórico de alterações
* Histórico de pagamentos (data, valor, forma de pagamento, observação,
  quem registrou)
* Resumo financeiro: valor total, valor pago, saldo restante
* Status de pagamento: NÃO PAGO / PARCIAL / PAGO

## Ações
 
* Editar
* Alterar Status
* Anexar Comprovante
* Registrar Pagamento
## Regras
 
* O campo forma_pagamento do cadastro da venda é legado e não é mais
  exigido — cada pagamento individual define sua própria forma de
  pagamento.
* A comissão exibida continua sendo calculada sobre o valor total da
  venda, independente do quanto já foi pago.

---

# Tela 06 - Cadastro de Passeios

## Objetivo

Gerenciar passeios.

## Campos

* Nome
* Descrição
* Percentual Comissão

## Ações

* Novo
* Editar
* Desativar

---

# Tela 07 - Cadastro de Tipos de Passeio

## Objetivo

Gerenciar tipos de passeio.

## Campos

* Nome

## Ações

* Novo
* Editar
* Desativar

---

# Tela 08 - Cadastro de Embarcações

## Objetivo

Gerenciar embarcações.

## Campos

* Nome
* Capacidade
* Observação

## Ações

* Novo
* Editar
* Desativar

---

# Tela 09 - Relatório de Vendas

## Filtros

* Período
* Passeio
* Status
* Recepcionista

## Indicadores

* Total Vendido
* Total de Comissões
* Quantidade de Passageiros

---

# Tela 10 - Relatório de Comissões

## Filtros

* Período
* Recepcionista

## Exibir

* Total Vendido
* Total de Comissão
* Quantidade de Vendas

---

# Tela 11 - Usuários

## Objetivo

Gerenciar acesso ao sistema.

## Campos

* Nome
* E-mail
* Perfil

## Ações

* Novo
* Editar
* Desativar

---

# Navegação Principal

Dashboard

Vendas
├── Listagem
├── Nova Venda

Cadastros
├── Passeios
├── Tipos de Passeio
├── Embarcações

Relatórios
├── Vendas
├── Comissões

Administração
├── Usuários
