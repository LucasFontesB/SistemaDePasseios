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

# Pagamentos
 
## POST /vendas/{id}/pagamentos
 
Registra um novo pagamento para a venda.
 
### Entrada
 
valor
forma_pagamento
observacao (opcional)
 
### Regras
 
* valor não pode ser zero.
* Para corrigir um lançamento errado, registrar um novo pagamento com valor
  negativo equivalente (lançamento de ajuste). Pagamentos nunca são excluídos.
* forma_pagamento deve ser um dos valores: DINHEIRO, PIX, CARTAO_DEBITO,
  CARTAO_CREDITO.
* O valor pago total e o status de pagamento (NAO_PAGO/PARCIAL/PAGO) são
  recalculados automaticamente a partir da soma dos pagamentos da venda.
* A comissão da venda não é afetada por este endpoint — permanece calculada
  sobre o valor_total.
### Redirecionamento
 
/vendas/{id}
 
---
 
## GET /vendas/{id}
 
(Endpoint já existente, sem alteração de rota)
 
### Observação
 
A tela de detalhes da venda agora também exibe o histórico de pagamentos,
o valor pago, o saldo restante e o status de pagamento.

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

# Tipos de Apartamento (Fase 7.1)

Cadastro fixo do hotel, usado na composição de tarifa dos Grupos
(RN-G019). Restrito a ADMIN/GERENCIA, mesmo padrão de Passeios (listagem
e formulário na mesma página).

## GET /tipos-apartamento

Lista tipos de apartamento.

### Template

cadastros/tipos_apartamento.html

---

## POST /tipos-apartamento

Cria tipo de apartamento.

### Campos

* nome (obrigatório, único)
* ordem (define a sequência de exibição)
* valor_diaria_net_padrao, valor_diaria_sistema_padrao (RN-G005 — apenas
  referência, pré-preenchem a linha ao adicionar o tipo num grupo)
* observacao

---

## GET /tipos-apartamento/{id}/editar

Exibe formulário de edição.

---

## POST /tipos-apartamento/{id}/editar

Atualiza tipo de apartamento.

---

## POST /tipos-apartamento/{id}/desativar

Executa soft delete. Um tipo desativado continua resolvível por nome na
reconstituição de composição ao aprovar um orçamento (RN-G007).

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

# Módulo de Grupos

Ver docs/GRUPOS.md para a especificação completa do módulo. Acesso liberado
para ADMIN, GERENCIA e RECEPCAO (RN-G010 e seção Permissões do GRUPOS.md).

# Log de Alterações (Fase 3)

Não é um endpoint próprio: a partir da Fase 3, todas as rotas de escrita
de Grupos abaixo (POST /grupos, POST /grupos/{id}/editar, POST
/grupos/{id}/status, POST /grupos/{id}/recalcular-net, POST
/grupos/{id}/recalcular-sistema) também gravam em `grupos_historico`
(RN-G009), uma linha por campo alterado. Aplicado retroativamente à Fase
2 — nenhuma rota nova foi criada. Os cadastros de Agências e Guias (Fase
1) não geram log; soft delete já é suficiente para eles.

---

# Grupos (Fase 2 — Dados Gerais)

## GET /grupos

Lista grupos.

### Filtros

* nome
* status
* data_inicial (filtra `data_entrada >=`)
* data_final (filtra `data_entrada <=`)

### Template

grupos/listagem.html

---

## GET /grupos/novo

Exibe formulário de cadastro.

### Template

grupos/form.html

---

## POST /grupos

Cria grupo. A partir da Fase 7.2, a tarifa não é mais preenchida aqui —
`qtd_apartamentos`, `valor_total_net` e `valor_total_sistema` nascem
zerados; a composição por tipo é montada na tela de detalhes depois de
salvar (ver "Grupos — Composição por Tipo de Apartamento" abaixo).

### Campos

* nome (obrigatório)
* responsavel, telefone, email
* agencia_id, guia_id (opcionais, RN-G004)
* data_entrada, data_saida (obrigatórios; saída deve ser posterior à entrada)
* qtd_hospedes, qtd_apartamentos_cortesia
* qtd_apartamentos_prevista (opcional, só na criação, RN-G028 — referência
  para o alerta não-bloqueante se a composição real ultrapassar esse
  número)
* prazo_deadline, prazo_roomlist (opcionais, RN-G021; RN-G029 dispara
  alerta não-bloqueante em Dados Gerais quando a 7 dias ou menos do
  vencimento, ou já vencidos)
* observacao

### Regras

* Gerar código sequencial (`GRP-YYYYMMDD-XXXX`).
* Status inicial sempre `PROSPECCAO`.

### Redirecionamento

/grupos/{id}?tab=dados

---

## GET /grupos/{id}?tab={aba}

Exibe detalhes do grupo. Abas navegadas por query param — todas as seis
ativas desde a Fase 6 (`dados`, `orcamentos`, `pagamentos`, `roomlist`,
`anexos`, `atividade`).

### Template

grupos/detalhes.html (inclui grupos/tabs/*.html)

---

## GET /grupos/{id}/editar

Exibe formulário de edição. Mesmos campos do cadastro — sem tarifa (ver
composição abaixo); mostra `qtd_apartamentos` como campo calculado
somente-leitura.

### Template

grupos/form.html

---

## POST /grupos/{id}/editar

Atualiza grupo (identificação, intermediário, período, hóspedes,
cortesia, prazos, observação). RN-G003: alterar datas nunca sobrescreve um
total marcado como manual — mas resincroniza os totais automáticos a
partir da composição atual, já que `noites` pode ter mudado.

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{id}/status

Atualiza status do grupo.

### Entrada

status

### Regras

* RN-G010: transição para `CANCELADO` exige perfil ADMIN ou GERENCIA.

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{id}/recalcular-net

Zera a flag `valor_total_net_manual` e recalcula `valor_total_net` somando
`quantidade × diária net × noites` de todas as linhas de
`grupos_apartamentos` (RN-G020).

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{id}/recalcular-sistema

Mesma ação do endpoint acima, para `valor_total_sistema`.

### Redirecionamento

/grupos/{id}?tab=dados

---

# Grupos — Composição por Tipo de Apartamento (Fase 7.2)

## POST /grupos/{grupo_id}/apartamentos

Adiciona uma linha de composição.

### Campos

* tipo_apartamento_id (obrigatório)
* quantidade (obrigatório, mínimo 1)
* valor_diaria_net, valor_diaria_sistema

### Regras

* RN-G020: rejeitado se o tipo já foi adicionado a este grupo (constraint
  `UNIQUE(grupo_id, tipo_apartamento_id)`) — o usuário edita a linha
  existente em vez de duplicar.
* Após salvar, resincroniza `qtd_apartamentos`, `valor_total_net` e
  `valor_total_sistema` do grupo (RN-G003: só os totais não-manuais são
  recalculados) e dispara a verificação de divergência do orçamento
  (RN-G012).
* **Fase 8.4 — RN-G032:** cria `quantidade` linhas vazias correspondentes
  em `grupos_roomlist` (`hospede_nome` nulo) para este tipo.

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{grupo_id}/apartamentos/{item_id}/editar

Atualiza quantidade/diárias de uma linha (edição em linha na própria
listagem). Mesma resincronização de agregados do endpoint acima.

### Regras (Fase 8.4 — RN-G032)

* Se `quantidade` aumentar, cria linhas vazias extras na roomlist para
  este tipo (delta).
* Se `quantidade` diminuir, remove apenas linhas ainda vazias
  (`hospede_nome` nulo) para cobrir o delta. Se não houver linhas vazias
  suficientes — ou seja, a redução exigiria apagar um hóspede já
  cadastrado — a operação é **rejeitada por inteiro**: nem a quantidade
  nem a roomlist são alteradas, e uma mensagem de erro explica quantos
  hóspedes precisam ser removidos manualmente antes.

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{grupo_id}/apartamentos/{item_id}/remover

Remove uma linha da composição e resincroniza os agregados do grupo.

### Regras (Fase 8.4 — RN-G032)

* Remove também todas as linhas vazias da roomlist para este tipo. Se
  houver qualquer linha com `hospede_nome` preenchido (hóspede já
  cadastrado), a remoção é **rejeitada por inteiro** — nada é apagado, e
  o usuário precisa remover os hóspedes manualmente na aba Roomlist
  primeiro.

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{grupo_id}/valor-total-net/manual

Define `valor_total_net` com o valor enviado e marca
`valor_total_net_manual = true` (RN-G020 — a flag passou a atuar sobre o
agregado da composição, não sobre uma fórmula única).

### Entrada

valor

### Redirecionamento

/grupos/{id}?tab=dados

---

## POST /grupos/{grupo_id}/valor-total-sistema/manual

Mesma ação do endpoint acima, para `valor_total_sistema`.

### Redirecionamento

/grupos/{id}?tab=dados

---

# Grupos — Orçamentos (Fase 4, revisado na Fase 7.3)

## POST /grupos/{grupo_id}/orcamentos

Gera uma nova versão de orçamento com os valores atuais do grupo
(RN-G012 — sempre ação manual do usuário, nunca automática).

### Campos

* motivo (opcional)
* validade (opcional, data)
* condicoes (opcional)

### Regras

* `versao` = última versão do grupo + 1 (ou 1 se for a primeira).
* Snapshot congelado (RN-G013, reescrita na Fase 7.3): quantidades, totais,
  `valor_pago`/`saldo`, datas de entrada/saída, status do grupo e os dois
  prazos — mais duas tabelas cheias, gravadas na mesma transação: uma
  linha por tipo de apartamento em `grupos_orcamentos_apartamentos`
  (nome do tipo como texto, quantidade, diárias e subtotais) e uma linha
  por pagamento existente até o momento em `grupos_orcamentos_pagamentos`.
  Nada disso é recalculado depois — nem para reimpressão do PDF.
* Status inicial sempre `RASCUNHO`; `desatualizado` sempre `false`.

### Redirecionamento

/grupos/{id}?tab=orcamentos

---

## POST /grupos/{grupo_id}/orcamentos/{orcamento_id}/enviar

Marca a versão como `ENVIADO`. Exige que o status atual seja `RASCUNHO`.

### Redirecionamento

/grupos/{id}?tab=orcamentos

---

## POST /grupos/{grupo_id}/orcamentos/{orcamento_id}/aprovar

Marca a versão como `APROVADO`. Rejeitado se a versão já estiver
`APROVADO` ou `RECUSADO`.

### Regras

* RN-G007 (reescrita na Fase 7.3): copia `qtd_hospedes` e
  `qtd_apartamentos_cortesia` para o grupo, marca os totais como manuais e
  **substitui inteiramente** a composição atual (`grupos_apartamentos`)
  pelas linhas congeladas em `grupos_orcamentos_apartamentos` desta
  versão — não só os totais agregados, senão o grupo ficaria com o valor
  certo mas a composição por tipo desatualizada. Cada `tipo_apartamento_nome`
  do snapshot é resolvido de volta a um tipo do cadastro (mesmo
  desativado); se algum não existir mais, a aprovação inteira é recusada
  sem alterar nada (tudo ou nada).
* Não altera o status do grupo automaticamente — apenas sugere ao usuário
  (via mensagem) que o atualize para `CONFIRMADO`.

### Redirecionamento

/grupos/{id}?tab=orcamentos

---

## POST /grupos/{grupo_id}/orcamentos/{orcamento_id}/recusar

Marca a versão como `RECUSADO`. Rejeitado se a versão já estiver
`APROVADO` ou `RECUSADO`.

### Redirecionamento

/grupos/{id}?tab=orcamentos

---

## GET /grupos/{grupo_id}/orcamentos/{orcamento_id}/pdf

Gera o PDF da versão informada (qualquer status). Lê exclusivamente das
tabelas de snapshot dessa versão — nada é recalculado a partir do grupo
atual.

### Conteúdo (RN-G022, substitui a RN-G016 revogada)

Logo do hotel no cabeçalho; tabela por tipo de apartamento com quantidade,
diária net, diária sistema e subtotal nos dois tarifários; quantidade
total e valor total geral (net e sistema); pagamentos recebidos até a
geração; saldo; status do grupo; prazo deadline e prazo roomlist —
diferente da regra original (RN-G016), que mostrava só o valor net; a
decisão foi revertida a pedido do usuário.

### Resposta

application/pdf

---

## Detecção de divergência (RN-G012)

Não é um endpoint próprio: sempre que uma rota de escrita de Grupos altera
quantidades, totais ou o valor pago (POST /grupos/{id}/editar,
recalcular-net, recalcular-sistema, valor-total-{net,sistema}/manual,
qualquer alteração de composição em /grupos/{id}/apartamentos/*, ou
registro de pagamento), o sistema compara o grupo com a última versão de
orçamento gerada. Se divergir e a versão ainda não estiver marcada, ela
recebe `desatualizado = true` e um aviso aparece na aba Orçamentos.
Prazos (RN-G021) não entram nessa comparação — são informativos. O
sistema nunca gera uma nova versão sozinho.

---

# Grupos — Pagamentos (Fase 5)

## POST /grupos/{grupo_id}/pagamentos

Registra um novo pagamento para o grupo.

### Entrada

* valor (não pode ser zero; negativo é lançamento de correção)
* data_pagamento (opcional; assume a data de hoje se vazio)
* forma_pagamento (opcional; DINHEIRO, PIX, CARTAO_DEBITO, CARTAO_CREDITO)
* observacao (opcional)

### Regras

* RN-G008: pagamentos nunca são excluídos — não há rota de remoção.
  Correções são feitas por um novo lançamento com valor negativo.
* `valor_pago` e `saldo` do grupo são sempre recalculados sobre o valor
  sistema (RN-G027, revoga RN-G001), somando todos os pagamentos do
  grupo.
* RN-G017: dispara a verificação de divergência do orçamento — a última
  versão gerada é marcada `desatualizado` mesmo que nenhum outro campo do
  grupo tenha mudado.

### Redirecionamento

/grupos/{id}?tab=pagamentos

---

# Grupos — Roomlist (Fase 6, revisado nas Fases 7.4 e 8.4/8.5)

## POST /grupos/{grupo_id}/roomlist

Adiciona um registro manual à roomlist (fora do fluxo automático de
sincronização com a composição — RN-G032).

### Campos

* apartamento, hospede_nome (obrigatório neste formulário — as linhas
  vazias criadas automaticamente pela composição são a única forma de
  `hospede_nome` nulo no banco), documento
* tipo_apartamento_id (RN-G023 — select do cadastro `tipos_apartamento`,
  substitui o antigo campo de texto livre)
* cortesia (checkbox "on")
* check_in, check_out, observacao

### Redirecionamento

/grupos/{id}?tab=roomlist

---

## GET /grupos/{grupo_id}/roomlist/pdf

Exporta a roomlist completa do grupo em PDF (Fase 8.5, RN-G033).

### Regras

* Agrupada por tipo de apartamento, na ordem de `tipos_apartamento.ordem`.
* Linha vazia (`hospede_nome` nulo) aparece como "A definir".
* `Content-Disposition: inline` — abre no navegador (`target="_blank"`),
  mesmo padrão de `GET /grupos/{grupo_id}/orcamentos/{orcamento_id}/pdf`.

---

## GET /grupos/{grupo_id}/roomlist/excel

Exporta a roomlist completa do grupo em Excel (.xlsx) (Fase 8.5,
RN-G033).

### Regras

* Mesmo agrupamento e convenção "A definir" do PDF acima.
* `Content-Disposition: attachment` — baixa o arquivo diretamente.

---

## POST /grupos/{grupo_id}/roomlist/{item_id}/editar

Atualiza um registro (edição em linha na própria listagem).

### Redirecionamento

/grupos/{id}?tab=roomlist

---

## POST /grupos/{grupo_id}/roomlist/{item_id}/remover

Remove fisicamente o registro (não é dado financeiro).

### Redirecionamento

/grupos/{id}?tab=roomlist

---

## POST /grupos/{grupo_id}/anexos (a partir da aba Roomlist)

Não é uma rota nova — RN-G024: a aba Roomlist tem seu próprio formulário
de upload que reaproveita exatamente `POST /grupos/{grupo_id}/anexos`
(mesma rota da aba Anexos), enviando `tipo=ROOMLIST` num campo oculto. É o
mesmo registro em `grupos_anexos` — aparece nas duas abas, sem duplicar
linha.

---

# Grupos — Anexos (Fase 6, tipo ROOMLIST adicionado na Fase 7.4)

## POST /grupos/{grupo_id}/anexos

Upload de anexo. Mesma validação de `POST /vendas/{id}/comprovantes`.

### Entrada

* tipo (COMPROVANTE_PAGAMENTO, ORCAMENTO_ASSINADO, ROOMLIST, OUTRO)
* arquivo (multipart; PDF, JPG, JPEG, PNG; máx. 10 MB)

### Redirecionamento

/grupos/{id}?tab=anexos (ou `?tab=roomlist` quando enviado por lá)

---

## GET /grupos/{grupo_id}/anexos/{anexo_id}

Download do anexo.

---

## POST /grupos/{grupo_id}/anexos/{anexo_id}/remover

Soft delete (`removido_em`) — diferente de `comprovantes`, que usa
remoção física. O arquivo permanece em disco.

### Redirecionamento

/grupos/{id}?tab=anexos

---

# Grupos — Atividade e Comentários (Fase 6)

## POST /grupos/{grupo_id}/comentarios

Registra um comentário do usuário sobre o grupo.

### Entrada

texto (obrigatório)

### Redirecionamento

/grupos/{id}?tab=atividade

---

## GET /grupos/{grupo_id}?tab=atividade

Não é endpoint novo — a aba Atividade (já coberta por
`GET /grupos/{id}`) une comentários e `grupos_historico` numa única
linha do tempo, ordenada por data decrescente.

### Filtros

* `?filtro=comentarios` — exibe apenas os comentários, ocultando o
  histórico de alterações.

---

# Agências

## GET /agencias

Lista agências ativas.

### Template

agencias/listagem.html

---

## GET /agencias/nova

Exibe formulário de cadastro.

### Template

agencias/form.html

---

## POST /agencias

Cria agência.

### Campos

* nome (obrigatório)
* nome_fantasia
* cnpj
* contato
* telefone
* email
* percentual_comissao_padrao (assume 0 se vazio)
* observacao

### Regras (Fase 8.3 — RN-G030)

* Se a requisição trouxer o header `X-Requested-With: XMLHttpRequest`
  (criação rápida via modal no formulário de grupo, sem navegar de
  página), a rota responde em JSON em vez de redirecionar:
  * sucesso: `{"id": "...", "nome": "..."}`
  * erro de validação: `{"erros": [...]}` com status 400
  * sem sessão: 401; sem permissão: 403
* Sem o header, comportamento inalterado (form HTML tradicional,
  redireciona para `/agencias`).

---

## GET /agencias/{id}/editar

Exibe formulário de edição.

---

## POST /agencias/{id}/editar

Atualiza agência.

---

## POST /agencias/{id}/desativar

Executa soft delete.

---

# Guias

## GET /guias

Lista guias ativos.

### Template

guias/listagem.html

---

## GET /guias/novo

Exibe formulário de cadastro.

### Template

guias/form.html

---

## POST /guias

Cria guia.

### Campos

* nome (obrigatório)
* cpf
* cadastur
* telefone
* email
* percentual_comissao_padrao (assume 0 se vazio)
* observacao

### Regras (Fase 8.3 — RN-G030)

* Mesmo comportamento de detecção via `X-Requested-With: XMLHttpRequest`
  descrito em `POST /agencias` — resposta JSON `{"id", "nome"}`/`{"erros"}`
  quando a criação rápida vem do modal do formulário de grupo.

---

## GET /guias/{id}/editar

Exibe formulário de edição.

---

## POST /guias/{id}/editar

Atualiza guia.

---

## POST /guias/{id}/desativar

Executa soft delete.

---

# Health Check

## GET /health

Verificação da aplicação.

### Resposta

{
"status": "ok"
}
