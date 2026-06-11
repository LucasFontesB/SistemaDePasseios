# PROJECT_STRUCTURE.md

# Objetivo

Definir a estrutura física do projeto, responsabilidades de cada camada e convenções de desenvolvimento.

---

# Estrutura Geral

project-root/

├── app/
├── docs/
├── migrations/
├── tests/
├── uploads/
├── .env
├── .env.example
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md

---

# Diretório app

app/

├── controllers/
├── services/
├── repositories/
├── models/
├── schemas/
├── templates/
├── static/
├── core/
├── database/
├── middleware/
└── main.py

---

# Camadas da Aplicação

Request
↓
Controller
↓
Service
↓
Repository
↓
Database

---

# Controllers

Responsáveis por:

* Receber requisições
* Validar entrada básica
* Chamar services
* Retornar resposta

Não devem conter:

* SQL
* Regras de negócio

Exemplo:

sale_controller.py

tour_controller.py

user_controller.py

---

# Services

Responsáveis por:

* Regras de negócio
* Validações complexas
* Cálculos

Exemplos:

calculate_commission()

change_sale_status()

generate_sale_number()

---

# Repositories

Responsáveis por:

* Consultas ao banco
* Persistência

Exemplos:

sale_repository.py

tour_repository.py

user_repository.py

---

# Models

Modelos SQLAlchemy.

Exemplo:

User

Sale

Tour

Boat

Receipt

---

# Schemas

Modelos Pydantic.

Utilizados para:

* Validação
* Serialização

Exemplos:

SaleCreate

SaleUpdate

SaleResponse

---

# Core

Configurações globais.

core/

├── config.py
├── security.py
├── permissions.py
└── constants.py

---

## config.py

Carrega:

* DATABASE_URL
* SECRET_KEY
* UPLOAD_PATH

---

## security.py

Responsável por:

* Hash de senha
* Verificação de senha
* Sessão

---

## permissions.py

Controle de acesso.

ADMIN

GERENCIA

RECEPCAO

---

# Database

database/

├── connection.py
├── base.py
└── seed.py

---

## connection.py

Criação da conexão PostgreSQL.

---

## base.py

Base declarativa SQLAlchemy.

---

## seed.py

Dados iniciais.

Exemplo:

* Usuário administrador
* Tipos de passeio padrão

---

# Middleware

middleware/

├── auth.py
└── logging.py

---

## auth.py

Verificação de sessão.

---

## logging.py

Registro de acessos.

---

# Templates

templates/

├── layouts/
├── components/
├── dashboard/
├── sales/
├── tours/
├── boats/
├── users/
└── reports/

---

# Layouts

layouts/

base.html

---

## base.html

Estrutura principal:

Header

Sidebar

Content

Footer

---

# Components

components/

header.html

sidebar.html

breadcrumbs.html

alerts.html

pagination.html

modal.html

---

# Dashboard

dashboard/

index.html

---

# Sales

sales/

list.html

create.html

edit.html

details.html

---

# Tours

tours/

list.html

create.html

edit.html

---

# Boats

boats/

list.html

create.html

edit.html

---

# Users

users/

list.html

create.html

edit.html

---

# Reports

reports/

sales.html

commissions.html

---

# Static

static/

├── css/
├── js/
├── img/

---

# CSS

css/

app.css

dashboard.css

tables.css

forms.css

---

# JavaScript

js/

app.js

sales.js

reports.js

---

# Uploads

uploads/

2026/
├── 01/
├── 02/
└── 03/

---

# Migrations

migrations/

Arquivos Alembic.

Nunca editar manualmente.

---

# Tests

tests/

├── unit/
├── integration/
└── fixtures/

---

# Unit

Testes de:

* Comissão
* Status
* Permissões

---

# Integration

Testes de:

* Login
* Cadastro
* Banco

---

# Convenções

## Controllers

Nome:

*_controller.py

Exemplo:

sale_controller.py

---

## Services

Nome:

*_service.py

Exemplo:

sale_service.py

---

## Repositories

Nome:

*_repository.py

Exemplo:

sale_repository.py

---

## Models

Nome:

Singular

Exemplo:

Sale

Tour

Boat

User

---

## Tabelas

Nome:

Plural

Exemplo:

sales

tours

boats

users

---

# Fluxo Exemplo

Usuário cria venda

↓

SaleController

↓

SaleService

↓

Commission Calculation

↓

SaleRepository

↓

PostgreSQL

↓

Resposta para usuário
