# 🚢 Sistema de Gestão de Passeios

Sistema web interno para gerenciamento de vendas de passeios turísticos de hotel. Desenvolvido para substituir o controle manual em planilhas, centralizando vendas, comprovantes, embarcações e comissões em uma única plataforma.

---

## 📋 Sobre o Projeto

O sistema permite que recepcionistas registrem vendas de passeios, anexem comprovantes de pagamento e acompanhem o status de cada reserva. Também gerencia hospedagem de grupos sob regime de tarifa net/sistema (agências e guias, composição por tipo de apartamento, orçamentos versionados, roomlist e pagamentos). A gerência tem acesso a relatórios de vendas, comissões e ao relatório gerencial, enquanto o administrador gerencia usuários, passeios e embarcações.

---

## ✨ Funcionalidades

### Vendas de Passeios

- **Autenticação** com controle de acesso por perfil (Admin, Gerência, Recepção)
- **Dashboard** com indicadores do dia, do mês e próximos embarques
- **Cadastro de Vendas** com cálculo automático de comissão
- **Múltiplos pagamentos por venda** — uma venda pode ter mais de um lançamento de pagamento
- **Agenda de Embarques** — visão diária das saídas
- **Upload de Comprovantes** — PDF, JPG, JPEG e PNG
- **Histórico de Alterações** por venda
- **Relatório de Vendas** por período, passeio, status e recepcionista
- **Relatório de Comissões** individual e pelo critério do hotel
- **Relatório Gerencial** com exportação em PDF
- **Geração de PDF** — voucher e recibo em uma página com linha de corte, sempre pelo valor efetivamente pago
- **Envio via WhatsApp** — mensagem de confirmação pré-formatada
- **Cadastros** de passeios, tipos de passeio e embarcações
- **Gerenciamento de Usuários**
- **Mensagens de sucesso e erros amigáveis**
- **Perfil do usuário** — alteração de nome e senha

### Módulo de Grupos (hospedagem)

Especificação completa de regras de negócio em [`docs/GRUPOS.md`](docs/GRUPOS.md).

- **Cadastro de Grupos** com código sequencial automático, período de estadia, quantidade prevista de apartamentos e prazos de deadline/roomlist
- **Agências e Guias** com percentual de comissão padrão — cadastro próprio, e também criação rápida via modal direto no formulário do grupo, sem perder o que já foi preenchido
- **Composição por Tipo de Apartamento** (Solteiro, Casal, Duplo, Triplo, Quádruplo, Suíte Master I/II) com tarifa dupla — net e sistema — por linha, com totais recalculados automaticamente (ou sobrescritos manualmente quando necessário)
- **Base financeira pelo valor sistema** — saldo e valor pago do grupo são sempre calculados sobre o que o hotel efetivamente recebe; o valor net fica como referência de comissão/agência
- **Alertas não bloqueantes** quando a composição ultrapassa a quantidade prevista de apartamentos, ou quando os prazos de roomlist/pagamento estão vencendo
- **Orçamentos versionados** — cada versão gerada congela um snapshot completo (composição, tarifas, pagamentos, prazos); aprovar uma versão substitui a composição vigente do grupo pela composição congelada
- **Detecção automática de divergência** entre a última versão de orçamento gerada e o estado atual do grupo
- **Roomlist sincronizada com a composição** — alterar a quantidade de um tipo cria ou remove linhas de hóspede automaticamente; uma redução nunca apaga um hóspede já cadastrado, é recusada com mensagem clara nesse caso
- **Exportação da roomlist em PDF e Excel**, agrupada por tipo de apartamento
- **Controle de pagamentos** do grupo, sem exclusão física — correções são sempre um novo lançamento
- **Anexos** (comprovantes, roomlist, orçamentos assinados) com upload/download/remoção
- **Linha do tempo de atividade** unificando comentários e histórico de alterações, com identificação específica por evento e horário exato

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Banco de Dados | PostgreSQL |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| PDF | ReportLab |
| Planilhas (Excel) | openpyxl |
| Servidor | Uvicorn |

---

## 🏗️ Arquitetura

O projeto segue arquitetura em camadas:

```
Controller → Service → Repository → Database
```

```
app/
├── controllers/     # Recebem requisições e retornam respostas
├── services/        # Regras de negócio e validações
├── repositories/    # Acesso ao banco de dados
├── models/          # Models SQLAlchemy
├── core/            # Configurações, segurança, constantes
├── templates/       # Templates Jinja2
├── static/          # CSS e JS
└── database/        # Conexão e seed
```

---

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.12+
- PostgreSQL 14+

### Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/sistema-passeios.git
cd sistema-passeios
```

**2. Crie o ambiente virtual**

```bash
python -m venv .venv
```

**3. Ative o ambiente virtual**

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**4. Instale as dependências**

```bash
pip install -r requirements.txt
```

**5. Configure o `.env`**

Copie o `.env.example` para `.env` e preencha com seus dados:

```env
DATABASE_URL=postgresql://postgres:senha@localhost:5432/passeios
SECRET_KEY=sua-chave-secreta-aqui
SESSION_MAX_AGE=28800
UPLOAD_PATH=uploads
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
```

**6. Crie o banco de dados**

Crie um banco chamado `passeios` no PostgreSQL e execute o script:

```bash
psql -U postgres -d passeios -f create_tables.sql
```

**7. Rode o servidor**

```bash
python main.py
```

Acesse: [http://localhost:8000](http://localhost:8000)

**Login padrão:**
- E-mail: `admin@hotel.com`
- Senha: `admin123`

> ⚠️ Altere a senha padrão após o primeiro acesso.

---

## 🖼️ Logo

Para exibir a logo do hotel no PDF, coloque o arquivo em:

```
app/static/img/logo.png
```

---

## 🔐 Perfis de Acesso

| Perfil | Acesso |
|---|---|
| **ADMIN** | Total — inclui gerenciamento de usuários |
| **GERENCIA** | Dashboard, Vendas, Grupos, Cadastros e Relatórios |
| **RECEPCAO** | Dashboard, Vendas e Grupos (sem Cadastros, Relatórios e Usuários) |

---

## 🗄️ Banco de Dados

O banco utiliza UUID como chave primária em todas as tabelas e soft delete nos cadastros. Vendas, grupos, orçamentos e pagamentos nunca são removidos fisicamente — registros cancelados, reembolsados ou corrigidos são mantidos para auditoria.

Modelagem completa em [`docs/DATABASE.md`](docs/DATABASE.md).

Tabelas principais:
- **Vendas**: `usuarios`, `passeios`, `tipos_passeio`, `embarcacoes`, `vendas`, `comprovantes`, `venda_historico`
- **Grupos**: `grupos`, `grupos_apartamentos`, `grupos_orcamentos` (+ tabelas de snapshot), `grupos_pagamentos`, `grupos_roomlist`, `grupos_anexos`, `grupos_historico`, `grupos_comentarios`, `agencias`, `guias`, `tipos_apartamento`

---

## 📁 Variáveis de Ambiente

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL de conexão com o PostgreSQL |
| `SECRET_KEY` | Chave para assinatura das sessões |
| `SESSION_MAX_AGE` | Tempo de expiração da sessão em segundos |
| `UPLOAD_PATH` | Pasta para armazenamento dos comprovantes |
| `APP_ENV` | `development` ou `production` |
| `APP_HOST` | Host do servidor (padrão: `0.0.0.0`) |
| `APP_PORT` | Porta do servidor (padrão: `8000`) |

---

## 📄 Licença

Este projeto é de uso privado. Todos os direitos reservados.
