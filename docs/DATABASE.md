# DATABASE.md

# Visão Geral

O sistema será responsável por gerenciar:

* Usuários
* Passeios
* Tipos de Passeio
* Embarcações
* Vendas
* Comprovantes
* Comissões

---

# Convenções

## Chaves Primárias

Todas as tabelas utilizarão UUID como chave primária.

Exemplo:

id UUID PRIMARY KEY

---

## Auditoria

Todas as tabelas de cadastro possuirão:

criado_em TIMESTAMP NOT NULL

atualizado_em TIMESTAMP NOT NULL

deletado_em TIMESTAMP NULL

### Soft Delete

Registro ativo:

deletado_em = NULL

Registro removido:

deletado_em = 2026-06-10 14:30:00

Nenhum cadastro será removido fisicamente do banco.

---

# Tabela: usuarios

Controle de acesso ao sistema.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(150) |
| email         | VARCHAR(150) |
| senha_hash    | VARCHAR(255) |
| perfil        | VARCHAR(30)  |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

## Perfis

* ADMIN
* GERENCIA
* RECEPCAO

---

# Tabela: passeios

Cadastro dos passeios disponíveis.

| Campo               | Tipo         |
| ------------------- | ------------ |
| id                  | UUID         |
| nome                | VARCHAR(150) |
| descricao           | TEXT         |
| percentual_comissao | NUMERIC(5,2) |
| criado_em           | TIMESTAMP    |
| atualizado_em       | TIMESTAMP    |
| deletado_em         | TIMESTAMP    |

## Exemplos

* Maragogi
* Praia do Gunga
* Francês
* São Miguel dos Milagres

---

# Tabela: tipos_passeio

Classificação dos passeios.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(100) |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

## Exemplos

* Compartilhado
* Privativo
* Catamarã
* Lancha

---

# Tabela: embarcacoes

Cadastro das embarcações.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(150) |
| capacidade    | INTEGER      |
| observacao    | TEXT         |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

---

# Tabela: vendas

Tabela principal do sistema.

| Campo               | Tipo          |
| ------------------- | ------------- |
| id                  | UUID          |
| numero_venda        | VARCHAR(30)   |
| contratante         | VARCHAR(200)  |
| telefone            | VARCHAR(30)   |
| adultos             | INTEGER       |
| criancas            | INTEGER       |
| passeio_id          | UUID          |
| tipo_passeio_id     | UUID          |
| embarcacao_id       | UUID          |
| valor_total         | NUMERIC(10,2) |
| percentual_comissao | NUMERIC(5,2)  |
| valor_comissao      | NUMERIC(10,2) |
| data_saida          | DATE          |
| horario_saida       | TIME          |
| status              | VARCHAR(30)   |
| observacao          | TEXT          |
| usuario_id          | UUID          |
| criado_em           | TIMESTAMP     |
| atualizado_em       | TIMESTAMP     |

## Observações

* Não utilizar soft delete.
* Venda cancelada continua existindo.
* Histórico financeiro nunca deve ser removido.

---

## Status Permitidos

* PENDENTE
* AGUARDANDO_PAGAMENTO
* CONFIRMADO
* EMBARCADO
* FINALIZADO
* CANCELADO
* REEMBOLSADO

---

# Tabela: comprovantes

Arquivos anexados a uma venda.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| venda_id      | UUID         |
| nome_original | VARCHAR(255) |
| nome_arquivo  | VARCHAR(255) |
| caminho       | VARCHAR(500) |
| tipo_arquivo  | VARCHAR(50)  |
| tamanho_bytes | BIGINT       |
| enviado_em    | TIMESTAMP    |

## Observações

* Arquivos serão armazenados no servidor.
* O banco armazenará apenas metadados.

---

# Relacionamentos

usuarios (1)
└── vendas (N)

passeios (1)
└── vendas (N)

tipos_passeio (1)
└── vendas (N)

embarcacoes (1)
└── vendas (N)

vendas (1)
└── comprovantes (N)

---

# Índices Recomendados

## vendas

idx_vendas_numero

idx_vendas_contratante

idx_vendas_telefone

idx_vendas_status

idx_vendas_data_saida

idx_vendas_passeio

idx_vendas_usuario

idx_vendas_criado_em

## comprovantes

idx_comprovantes_venda

---

# Estrutura de Upload

/uploads
/2026
/06
comprovante_001.pdf
comprovante_002.jpg

---

# Regras de Negócio

RN001

O valor da comissão será calculado automaticamente utilizando o percentual configurado para o passeio.

RN002

O percentual utilizado na venda será armazenado na própria venda para preservar o histórico.

RN003

Uma venda poderá possuir múltiplos comprovantes.

RN004

Cadastros removidos via soft delete não deverão aparecer nas telas de seleção.

RN005

Relatórios históricos deverão considerar registros removidos via soft delete.

RN006

A exclusão física de registros será proibida para usuários do sistema.

RN007

Todas as ações financeiras deverão permanecer rastreáveis para auditoria futura.
