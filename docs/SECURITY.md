# SECURITY.md

# Objetivo

Definir padrões mínimos de segurança para desenvolvimento, implantação e operação do Sistema de Gestão de Passeios.

---

# Princípios Gerais

* Segurança por padrão
* Menor privilégio possível
* Defesa em camadas
* Auditoria de ações críticas
* Proteção dos dados dos clientes

---

# Autenticação

## Login

Autenticação baseada em sessão.

Não utilizar autenticação básica HTTP.

---

## Senhas

Requisitos mínimos:

* 8 caracteres
* Pelo menos 1 letra
* Pelo menos 1 número

Recomendado:

* 12 caracteres ou mais

---

## Armazenamento

Nunca armazenar senhas em texto puro.

Utilizar:

bcrypt

---

## Alteração de Senha

Somente o próprio usuário ou administrador.

---

# Sessões

## Cookie

Configurações obrigatórias:

HttpOnly = True

Secure = True

SameSite = Lax

---

## Expiração

Tempo máximo:

8 horas

Expirar automaticamente após inatividade.

---

## Logout

Invalidar sessão imediatamente.

---

# Controle de Acesso

## Perfis

ADMIN

GERENCIA

RECEPCAO

---

## ADMIN

Permissões:

* Total

---

## GERENCIA

Permissões:

* Dashboard
* Vendas
* Relatórios
* Cadastros

Sem acesso a usuários.

---

## RECEPCAO

Permissões:

* Dashboard
* Vendas

Sem acesso administrativo.

---

# Proteção CSRF

Todos os formulários POST devem possuir token CSRF.

Inclui:

* Login
* Cadastro
* Edição
* Upload
* Exclusão lógica

---

# Upload de Arquivos

## Tipos Permitidos

PDF

JPG

JPEG

PNG

---

## Tamanho Máximo

10 MB

---

## Validação

Obrigatório validar:

* Extensão
* MIME Type
* Tamanho

---

## Nome do Arquivo

Nunca utilizar o nome enviado pelo usuário.

Gerar nome interno:

UUID

Exemplo:

f9e4a76c-1234.pdf

---

## Armazenamento

Arquivos fora da pasta pública.

Exemplo:

/uploads

Não permitir acesso direto por URL.

---

# Banco de Dados

## ORM

Utilizar SQLAlchemy.

---

## SQL Injection

Proibido SQL montado por concatenação.

---

## Credenciais

Armazenar somente em:

.env

---

## Produção

Usuário do banco sem privilégios de superusuário.

---

# Logs

## Registrar

Login

Logout

Criação de venda

Edição de venda

Mudança de status

Upload de comprovante

Criação de usuário

---

## Não Registrar

Senhas

Tokens

Cookies

Dados sensíveis

---

# Auditoria

Registrar:

Quem

Quando

O que foi alterado

Valor anterior

Valor novo

---

# Erros

## Ambiente de Produção

Nunca exibir:

* Stacktrace
* SQL
* Caminhos internos

Usuário deve visualizar apenas mensagem amigável.

---

# Cabeçalhos HTTP

Adicionar:

X-Frame-Options

DENY

---

X-Content-Type-Options

nosniff

---

Referrer-Policy

strict-origin-when-cross-origin

---

Content-Security-Policy

Definir política mínima compatível com Bootstrap.

---

# HTTPS

Obrigatório.

Utilizar Caddy com certificado TLS automático.

---

# Rate Limiting

Aplicar em:

/login

Exemplo:

5 tentativas por minuto

por IP

---

# Backup

## Banco

Backup diário.

Retenção mínima:

30 dias

---

## Uploads

Backup diário.

Retenção mínima:

30 dias

---

## Teste de Restauração

Executar trimestralmente.

---

# Exclusões

## Cadastros

Soft Delete obrigatório.

---

## Vendas

Nunca excluir.

Utilizar status:

CANCELADO

REEMBOLSADO

---

# Ambiente

## Variáveis

Utilizar:

DATABASE_URL

SECRET_KEY

UPLOAD_PATH

SESSION_SECRET

---

## Arquivos

Nunca versionar:

.env

uploads/

backups/

---

# Dependências

Atualizar dependências periodicamente.

Monitorar vulnerabilidades conhecidas.

---

# Checklist de Produção

[ ] HTTPS ativo

[ ] Backup configurado

[ ] Restore testado

[ ] Rate limit ativo

[ ] CSRF ativo

[ ] Sessões seguras

[ ] Senhas criptografadas

[ ] Logs funcionando

[ ] Upload validado

[ ] Variáveis de ambiente configuradas

[ ] Usuário administrador criado
