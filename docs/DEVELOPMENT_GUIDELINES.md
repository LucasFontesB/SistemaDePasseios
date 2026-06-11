# DEVELOPMENT_GUIDELINES.md

# Objetivo

Definir padrões de desenvolvimento, segurança, arquitetura e interface para todo o projeto.

---

# Arquitetura

Utilizar arquitetura em camadas.

controllers
↓
services
↓
repositories
↓
database

Nenhuma regra de negócio deve ficar dentro das rotas.

---

# Estrutura do Projeto

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
└── utils/

---

# Convenções de Código

## Idioma

Código em inglês.

Exemplos:

User

Sale

Tour

Boat

Commission

---

## Nomes de Arquivos

snake_case

Exemplos:

user_service.py

sale_repository.py

tour_controller.py

---

## Nomes de Classes

PascalCase

Exemplos:

UserService

SaleRepository

TourController

---

## Nomes de Funções

snake_case

Exemplos:

create_sale()

calculate_commission()

find_sale_by_id()

---

# Banco de Dados

## Migrações

Utilizar Alembic.

Nunca alterar tabelas manualmente em produção.

---

## Chaves Primárias

UUID obrigatório.

---

## Exclusão

Utilizar soft delete para tabelas de cadastro.

Nunca remover registros financeiros.

---

# Segurança

## Senhas

Utilizar bcrypt.

Nunca armazenar senha em texto puro.

---

## SQL Injection

Utilizar SQLAlchemy ORM.

Nunca concatenar SQL manualmente.

Errado:

SELECT * FROM vendas WHERE nome = 'valor'

Correto:

Utilizar ORM ou parâmetros.

---

## Uploads

Permitir apenas:

* PDF
* JPG
* JPEG
* PNG

Validar:

* extensão
* mime type
* tamanho máximo

---

## Controle de Acesso

ADMIN

* acesso total

GERENCIA

* relatórios
* vendas

RECEPCAO

* vendas
* consultas

---

## Logs

Registrar:

* login
* logout
* criação de venda
* edição de venda
* alteração de status

---

# Frontend

## Framework CSS

Bootstrap 5

---

## Layout

Menu lateral fixo.

Topo com usuário logado.

Conteúdo central.

---

## Responsividade

Compatível com:

* Desktop
* Notebook
* Tablet

Mobile é opcional.

---

# Interface

Prioridade:

1. Simplicidade
2. Rapidez
3. Legibilidade

Não utilizar animações excessivas.

Não utilizar telas complexas.

---

# Formulários

Sempre validar:

Frontend

Backend

Nunca confiar apenas no navegador.

---

# Tratamento de Erros

Exibir mensagens amigáveis.

Não exibir stacktrace para usuários.

---

# Configurações

Utilizar arquivo .env

Exemplos:

DATABASE_URL

SECRET_KEY

UPLOAD_FOLDER

Nunca armazenar senhas diretamente no código.

---

# Testes

Implementar testes para:

* autenticação
* cálculo de comissão
* criação de vendas
* alteração de status

---

# Qualidade

Utilizar:

black

isort

flake8

pytest

Todos os commits devem manter o projeto sem erros de lint.
