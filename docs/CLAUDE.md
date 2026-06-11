# CLAUDE.md

# Sistema de Gestão de Passeios

## Objetivo

Este projeto é um sistema web interno para gerenciamento de vendas de passeios turísticos realizadas por um hotel.

O sistema substituirá uma planilha utilizada atualmente pela recepção para controlar vendas, passageiros, embarcações, comprovantes e comissões.

---

# Stack Tecnológica

Backend:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

Frontend:

* HTML
* CSS
* JavaScript
* Bootstrap 5

Infraestrutura:

* Docker
* Caddy

---

# Estrutura da Documentação

Antes de implementar qualquer funcionalidade, consulte os documentos abaixo.

---

## README.md

Visão geral do projeto.

Contém:

* Objetivos
* Stack utilizada
* Estrutura inicial
* Funcionalidades principais

Consultar quando precisar entender rapidamente o projeto.

---

## VISION.md

Visão de negócio do sistema.

Contém:

* Problema que será resolvido
* Público-alvo
* Objetivos
* Indicadores de sucesso

Consultar antes de propor novas funcionalidades.

---

## REQUIREMENTS.md

Requisitos funcionais e não funcionais.

Contém:

* Funcionalidades obrigatórias
* Restrições técnicas
* Regras gerais

Toda implementação deve atender aos requisitos descritos neste documento.

---

## DATABASE.md

Fonte oficial da modelagem de dados.

Contém:

* Tabelas
* Campos
* Relacionamentos
* Regras de negócio
* Índices

Nunca criar tabelas ou colunas sem atualizar este documento.

Em caso de conflito entre código e documentação, o DATABASE.md é a referência principal.

---

## SCREENS.md

Descrição das telas do sistema.

Contém:

* Objetivos de cada tela
* Campos
* Ações disponíveis
* Funcionalidades visíveis ao usuário

Consultar antes de criar templates HTML.

---

## SCREEN_FLOW.md

Fluxo de navegação do sistema.

Contém:

* Caminhos entre telas
* Navegação principal
* Permissões por perfil

Consultar antes de alterar menus ou navegação.

---

## API.md

Fonte oficial das rotas.

Contém:

* Endpoints
* Entradas
* Saídas
* Regras

Consultar antes de criar ou modificar controllers.

---

## UI_GUIDE.md

Padrão visual do sistema.

Contém:

* Paleta de cores
* Layout
* Componentes
* Tipografia
* Responsividade

Todas as telas devem seguir este guia.

---

## PROJECT_STRUCTURE.md

Estrutura física do projeto.

Contém:

* Organização de pastas
* Responsabilidade de cada camada
* Convenções

Toda nova funcionalidade deve seguir esta arquitetura.

---

## SECURITY.md

Regras de segurança.

Contém:

* Autenticação
* Sessões
* Uploads
* Permissões
* Backup
* Logs

Nenhuma implementação pode violar este documento.

---

## ROADMAP.md

Planejamento de versões.

Contém:

* Funcionalidades da V1
* Funcionalidades futuras
* Escopo do projeto

Não implementar funcionalidades fora da versão atual sem justificativa explícita.

---

# Regras de Desenvolvimento

## Arquitetura

Utilizar arquitetura em camadas:

Controller
↓
Service
↓
Repository
↓
Database

---

## Controllers

Responsáveis apenas por:

* Receber requisições
* Chamar services
* Retornar respostas

Não implementar regras de negócio em controllers.

---

## Services

Responsáveis por:

* Regras de negócio
* Validações
* Processamentos
* Cálculos

---

## Repositories

Responsáveis por:

* Persistência
* Consultas
* Acesso ao banco

---

# Convenções

## Linguagem

Todo o código deve ser escrito em inglês.

Exemplos:

Sale

Tour

Boat

User

Receipt

---

## Arquivos

Utilizar snake_case.

Exemplo:

sale_service.py

---

## Classes

Utilizar PascalCase.

Exemplo:

SaleService

---

## Métodos

Utilizar snake_case.

Exemplo:

calculate_commission()

---

# Banco de Dados

Utilizar:

* PostgreSQL
* SQLAlchemy
* Alembic

Não utilizar SQL concatenado manualmente.

Não utilizar DELETE físico para tabelas com soft delete.

---

# Segurança

Obrigatório:

* bcrypt para senhas
* HTTPS
* CSRF Protection
* Sessões seguras
* Upload validado
* Controle de permissões

---

# Design

Objetivos:

* Simplicidade
* Rapidez
* Legibilidade

Prioridade para desktop.

Evitar componentes excessivamente complexos.

---

# Escopo Atual

A prioridade é concluir a V1.

Objetivo da V1:

Substituir integralmente a planilha atualmente utilizada pelo hotel.

Novas funcionalidades devem ser avaliadas com base no ROADMAP.md.

---

# Instruções para IA

Ao implementar uma funcionalidade:

1. Consultar REQUIREMENTS.md.
2. Consultar DATABASE.md.
3. Consultar SCREENS.md.
4. Consultar API.md.
5. Consultar SECURITY.md.
6. Seguir PROJECT_STRUCTURE.md.
7. Atualizar documentação quando necessário.

Nunca assumir regras de negócio não documentadas.

Em caso de dúvida, solicitar esclarecimentos antes de implementar.

A documentação é a fonte oficial de verdade do projeto.
