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

# Módulo de Grupos

Ver docs/GRUPOS.md para a especificação completa do módulo. Liberado para
ADMIN, GERENCIA e RECEPCAO.

Lista de Grupos
│
├── Novo Grupo (sem tarifa — composição vem depois, na tela de detalhes;
│   agência/guia podem ser criados na hora, via modal — RN-G030, Fase 8.3)
├── Detalhes do Grupo (abas por query param, todas ativas desde a Fase 6)
│   ├── Dados Gerais
│   │   ├── Alertas não-bloqueantes (RN-G028/RN-G029, Fase 8.2: qtd.
│   │   │   prevista excedida; prazo de roomlist/deadline vencendo)
│   │   ├── Composição por Tipo de Apartamento (Fase 7.2, RN-G020)
│   │   │   ├── Adicionar Tipo (rejeita duplicata) → cria linhas vazias
│   │   │   │   na roomlist (RN-G032, Fase 8.4)
│   │   │   ├── Editar Linha (edição em linha) → sincroniza roomlist:
│   │   │   │   aumenta cria vazias, diminui remove só vazias, rejeita
│   │   │   │   por inteiro se exigir apagar hóspede já cadastrado
│   │   │   └── Remover Linha → mesma rejeição se houver hóspede
│   │   │       cadastrado na roomlist deste tipo
│   │   ├── Sobrescrever Valor Total Net/Sistema Manualmente
│   │   └── Recalcular Valor Total Net / Sistema (volta ao automático)
│   ├── Orçamentos
│   │   ├── Gerar Novo Orçamento (ação manual, nunca automática; snapshot
│   │   │   completo desde a Fase 7.3 — datas, status, prazos, composição
│   │   │   por tipo e pagamentos itemizados)
│   │   ├── Gerar PDF (logo + duas tarifas por tipo — RN-G022)
│   │   ├── Marcar como Enviado
│   │   ├── Aprovar (RN-G007: copia totais e **substitui a composição do
│   │   │   grupo** pela congelada na versão)
│   │   └── Recusar
│   ├── Pagamentos
│   │   └── Registrar Pagamento (correção = novo lançamento negativo)
│   ├── Roomlist (linhas geradas automaticamente pela composição —
│   │   │   RN-G032, Fase 8.4; linha vazia = "A definir")
│   │   ├── Adicionar/Editar/Remover Hóspede (tipo de apartamento por
│   │   │   select do cadastro — RN-G023)
│   │   ├── Exportar PDF / Exportar Excel (RN-G033, Fase 8.5 — agrupado
│   │   │   por tipo na ordem do cadastro)
│   │   └── Anexar Roomlist (RN-G024 — mesma rota de Anexos, tipo
│   │       pré-selecionado; aparece nas duas abas)
│   ├── Anexos (upload/download/soft delete)
│   └── Atividade (comentários + histórico, cada linha com identificador
│       específico e horário exato — RN-G026)
├── Editar Grupo
└── Alterar Status (cancelamento restrito a ADMIN/GERENCIA — RN-G010)

Lista de Agências
│
├── Nova Agência
├── Editar Agência
└── Desativar Agência

Lista de Guias
│
├── Novo Guia
├── Editar Guia
└── Desativar Guia

---

## Fluxo de Cadastro de Grupo

Novo Grupo
↓
Preencher Dados Gerais (sem tarifa)
↓
Salvar
↓
Detalhes do Grupo (aba Dados Gerais)
↓
Adicionar linhas de composição por tipo de apartamento (RN-G020)
↓
Totais do grupo sincronizados automaticamente

---

## Fluxo de Edição de Grupo

Listagem
↓
Selecionar Grupo
↓
Editar
↓
Salvar
↓
Detalhes do Grupo (aba Dados Gerais)

---

## Fluxo de Orçamentos

Detalhes do Grupo (aba Orçamentos)
↓
Gerar Novo Orçamento (motivo/validade/condições opcionais)
↓
Versão RASCUNHO criada com snapshot completo (RN-G013): totais, datas,
status, prazos, composição por tipo e pagamentos itemizados
↓
Marcar como Enviado (opcional) → ENVIADO
↓
Aprovar → APROVADO, totais copiados e composição do grupo substituída pela
congelada na versão (RN-G007)
    ou
Recusar → RECUSADO

Se o grupo mudar depois de uma versão gerada (quartos, tarifa por tipo,
apartamentos, pagamento): a versão vigente é marcada `desatualizado`
automaticamente — gerar a próxima versão continua sendo decisão do
usuário. Prazos não entram nessa verificação (RN-G021).

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

Grupos
├── Grupos (listagem/detalhe)
├── Agências
└── Guias

Cadastros
├── Passeios
├── Tipos de Passeio
├── Embarcações
└── Tipos de Apartamento

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
Grupos
Cadastros
Relatórios
Usuários

---

GERENCIA

Dashboard
Vendas
Grupos
Cadastros
Relatórios

---

RECEPCAO

Dashboard
Vendas
Grupos

Nota: a partir do Módulo de Grupos (ver docs/GRUPOS.md), RECEPCAO deixa de
ser limitado a Dashboard e Vendas — o módulo de Grupos (incluindo os
cadastros de Agências e Guias) é liberado para os três perfis. RECEPCAO
continua sem acesso a Cadastros (Passeios/Tipos/Embarcações), Relatórios e
Usuários.

---

# Breadcrumbs

Dashboard

Dashboard > Vendas

Dashboard > Vendas > Nova Venda

Dashboard > Vendas > Detalhes

Dashboard > Grupos

Dashboard > Grupos > Novo Grupo

Dashboard > Grupos > {código do grupo}

Dashboard > Grupos > Agências

Dashboard > Grupos > Guias

Dashboard > Cadastros > Passeios

Dashboard > Cadastros > Tipos de Apartamento

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
