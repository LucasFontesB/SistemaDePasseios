# 🚢 Sistema de Gestão de Passeios

Sistema web interno para gerenciamento de vendas de passeios turísticos de hotel. Desenvolvido para substituir o controle manual em planilhas, centralizando vendas, comprovantes, embarcações e comissões em uma única plataforma.

---

## 📋 Sobre o Projeto

O sistema permite que recepcionistas registrem vendas de passeios, anexem comprovantes de pagamento e acompanhem o status de cada reserva. A gerência tem acesso a relatórios de vendas e comissões, enquanto o administrador gerencia usuários, passeios e embarcações.

---

## ✨ Funcionalidades

- **Autenticação** com controle de acesso por perfil (Admin, Gerência, Recepção)
- **Dashboard** com indicadores do dia, do mês e próximos embarques
- **Cadastro de Vendas** com cálculo automático de comissão
- **Agenda de Embarques** — visão diária das saídas
- **Upload de Comprovantes** — PDF, JPG, JPEG e PNG
- **Histórico de Alterações** por venda
- **Relatório de Vendas** por período, passeio, status e recepcionista
- **Relatório de Comissões** individual e pelo critério do hotel
- **Geração de PDF** — voucher e recibo em uma página com linha de corte
- **Envio via WhatsApp** — mensagem de confirmação pré-formatada
- **Cadastros** de passeios, tipos de passeio e embarcações
- **Gerenciamento de Usuários**
- **Mensagens de sucesso e erros amigáveis**
- **Perfil do usuário** — alteração de nome e senha

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Banco de Dados | PostgreSQL |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| PDF | ReportLab |
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
| **GERENCIA** | Dashboard, Vendas, Cadastros e Relatórios |
| **RECEPCAO** | Dashboard e Vendas |

---

## 🗄️ Banco de Dados

O banco utiliza UUID como chave primária em todas as tabelas e soft delete nos cadastros. As vendas nunca são removidas fisicamente — registros cancelados ou reembolsados são mantidos para auditoria.

Tabelas principais: `usuarios`, `passeios`, `tipos_passeio`, `embarcacoes`, `vendas`, `comprovantes`, `venda_historico`.

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
