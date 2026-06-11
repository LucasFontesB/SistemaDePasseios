# SCREEN_FLOW.md

# Fluxo Geral

Login
↓
Dashboard
↓
Vendas
Cadastros
Relatórios
Administração

---

# Fluxo de Autenticação

Login
↓
Validar Credenciais
↓
Dashboard

Em caso de erro:

Login
↓
Mensagem de Erro
↓
Login

---

# Dashboard

Dashboard
│
├── Nova Venda
├── Listagem de Vendas
├── Próximos Embarques
├── Relatório de Vendas
└── Relatório de Comissões

---

# Módulo de Vendas

Listagem de Vendas
│
├── Nova Venda
├── Visualizar Venda
├── Editar Venda
└── Cancelar Venda

---

## Fluxo de Cadastro

Nova Venda
↓
Preencher Dados
↓
Salvar
↓
Detalhes da Venda

---

## Fluxo de Edição

Listagem
↓
Selecionar Venda
↓
Editar
↓
Salvar
↓
Detalhes da Venda

---

## Fluxo de Status

Detalhes da Venda
↓
Alterar Status
↓
Salvar
↓
Atualizar Histórico

---

## Fluxo de Comprovantes

Detalhes da Venda
↓
Enviar Comprovante
↓
Upload Realizado
↓
Atualizar Tela

---

# Módulo de Passeios

Lista de Passeios
│
├── Novo Passeio
├── Editar Passeio
└── Desativar Passeio

---

## Cadastro

Novo Passeio
↓
Preencher Dados
↓
Salvar
↓
Lista de Passeios

---

# Módulo de Tipos de Passeio

Lista de Tipos
│
├── Novo Tipo
├── Editar Tipo
└── Desativar Tipo

---

# Módulo de Embarcações

Lista de Embarcações
│
├── Nova Embarcação
├── Editar Embarcação
└── Desativar Embarcação

---

# Módulo de Usuários

Lista de Usuários
│
├── Novo Usuário
├── Editar Usuário
└── Desativar Usuário

---

# Relatórios

Relatórios
│
├── Relatório de Vendas
└── Relatório de Comissões

---

## Relatório de Vendas

Selecionar Filtros
↓
Gerar Relatório
↓
Visualizar Resultado

---

## Relatório de Comissões

Selecionar Filtros
↓
Gerar Relatório
↓
Visualizar Resultado

---

# Estrutura do Menu

Dashboard

Vendas
├── Listagem
└── Nova Venda

Cadastros
├── Passeios
├── Tipos de Passeio
└── Embarcações

Relatórios
├── Vendas
└── Comissões

Administração
└── Usuários

---

# Permissões

ADMIN

Dashboard
Vendas
Cadastros
Relatórios
Usuários

---

GERENCIA

Dashboard
Vendas
Cadastros
Relatórios

---

RECEPCAO

Dashboard
Vendas

---

# Breadcrumbs

Dashboard

Dashboard > Vendas

Dashboard > Vendas > Nova Venda

Dashboard > Vendas > Detalhes

Dashboard > Cadastros > Passeios

Dashboard > Relatórios > Comissões

---

# Fluxo Futuro (V1.1)

Dashboard
↓
Detalhes da Venda
↓
Histórico de Alterações

---

# Fluxo Futuro (V1.2)

Dashboard
↓
Agenda de Embarques
↓
Detalhes da Venda
