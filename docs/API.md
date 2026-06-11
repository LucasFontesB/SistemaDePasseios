# API.md

# Padrão de Rotas

Todas as rotas deverão exigir autenticação, exceto login e logout.

---

# Autenticação

## GET /login

Exibe tela de login.

### Resposta

Renderiza:

login.html

---

## POST /login

Realiza autenticação.

### Entrada

email
senha

### Ações

* Validar usuário
* Criar sessão

### Redirecionamento

/dashboard

---

## GET /logout

Encerra sessão do usuário.

### Redirecionamento

/ login

---

# Dashboard

## GET /dashboard

Exibe painel principal.

### Indicadores

* Vendas do dia
* Vendas do mês
* Total vendido
* Total de passageiros
* Total de comissões
* Próximos embarques

### Template

dashboard.html

---

# Vendas

## GET /vendas

Lista vendas.

### Filtros

* contratante
* telefone
* passeio
* status
* data_inicial
* data_final

### Template

vendas/listagem.html

---

## GET /vendas/nova

Exibe formulário de cadastro.

### Template

vendas/form.html

---

## POST /vendas

Cria nova venda.

### Campos

* contratante
* telefone
* adultos
* criancas
* passeio_id
* tipo_passeio_id
* embarcacao_id
* valor_total
* data_saida
* horario_saida
* observacao

### Regras

* Calcular comissão automaticamente
* Gerar número da venda

### Redirecionamento

/vendas/{id}

---

## GET /vendas/{id}

Exibe detalhes da venda.

### Template

vendas/detalhes.html

---

## GET /vendas/{id}/editar

Exibe formulário de edição.

### Template

vendas/form.html

---

## POST /vendas/{id}/editar

Atualiza venda.

### Ações

* Atualizar dados
* Registrar histórico

---

## POST /vendas/{id}/status

Atualiza status.

### Entrada

status

### Status Permitidos

* PENDENTE
* AGUARDANDO_PAGAMENTO
* CONFIRMADO
* EMBARCADO
* FINALIZADO
* CANCELADO
* REEMBOLSADO

### Ações

* Registrar histórico

---

# Comprovantes

## POST /vendas/{id}/comprovantes

Realiza upload de comprovante.

### Arquivos Permitidos

* PDF
* JPG
* JPEG
* PNG

### Ações

* Salvar arquivo
* Registrar metadados

---

## GET /comprovantes/{id}

Download do comprovante.

---

## POST /comprovantes/{id}/remover

Remove comprovante.

### Observação

Remoção lógica recomendada.

---

# Passeios

## GET /passeios

Lista passeios.

### Template

cadastros/passeios/listagem.html

---

## GET /passeios/novo

Exibe formulário.

---

## POST /passeios

Cria passeio.

### Campos

* nome
* descricao
* percentual_comissao

---

## GET /passeios/{id}/editar

Exibe formulário.

---

## POST /passeios/{id}/editar

Atualiza passeio.

---

## POST /passeios/{id}/desativar

Executa soft delete.

---

# Tipos de Passeio

## GET /tipos-passeio

Lista registros.

---

## POST /tipos-passeio

Cria registro.

---

## POST /tipos-passeio/{id}/editar

Atualiza registro.

---

## POST /tipos-passeio/{id}/desativar

Executa soft delete.

---

# Embarcações

## GET /embarcacoes

Lista embarcações.

---

## POST /embarcacoes

Cria embarcação.

---

## POST /embarcacoes/{id}/editar

Atualiza embarcação.

---

## POST /embarcacoes/{id}/desativar

Executa soft delete.

---

# Usuários

## GET /usuarios

Lista usuários.

---

## POST /usuarios

Cria usuário.

### Campos

* nome
* email
* senha
* perfil

---

## POST /usuarios/{id}/editar

Atualiza usuário.

---

## POST /usuarios/{id}/desativar

Executa soft delete.

---

# Relatórios

## GET /relatorios/vendas

Relatório de vendas.

### Filtros

* período
* passeio
* status
* recepcionista

---

## GET /relatorios/comissoes

Relatório de comissões.

### Filtros

* período
* recepcionista

---

# Health Check

## GET /health

Verificação da aplicação.

### Resposta

{
"status": "ok"
}
