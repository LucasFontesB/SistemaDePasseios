# SCREENS.md

# Tela 01 - Login

## Objetivo

Permitir autenticação dos usuários.

## Campos

* E-mail
* Senha

## Ações

* Entrar

## Regras

* Apenas usuários ativos podem acessar o sistema.

---

# Tela 02 - Dashboard

## Objetivo

Apresentar visão geral das vendas.

## Indicadores

### Hoje

* Quantidade de vendas
* Valor vendido
* Total de passageiros

### Mês Atual

* Quantidade de vendas
* Valor vendido
* Valor de comissão

### Próximos Embarques

* Data
* Horário
* Passeio
* Contratante

### Pendências

* Pagamentos pendentes
* Passeios sem comprovante

---

# Tela 03 - Listagem de Vendas

## Objetivo

Consultar vendas cadastradas.

## Filtros

* Contratante
* Telefone
* Passeio
* Status
* Data Inicial
* Data Final

## Colunas

* Número
* Contratante
* Passeio
* Data Saída
* Valor
* Comissão
* Status

## Ações

* Visualizar
* Editar
* Cancelar

---

# Tela 04 - Nova Venda

## Objetivo

Cadastrar venda de passeio.

## Campos

### Contratante

* Nome
* Telefone

### Passageiros

* Adultos
* Crianças

### Passeio

* Passeio
* Tipo de Passeio
* Embarcação

### Financeiro

* Valor Total

### Saída

* Data
* Horário

### Outros

* Observação

## Campos Calculados

* Percentual Comissão
* Valor Comissão

## Ações

* Salvar
* Salvar e Anexar Comprovante

---

# Tela 05 - Detalhes da Venda

## Objetivo

Visualizar informações completas.

## Exibir
 
* Todos os dados da venda
* Comprovantes anexados
* Histórico de alterações
* Histórico de pagamentos (data, valor, forma de pagamento, observação,
  quem registrou)
* Resumo financeiro: valor total, valor pago, saldo restante
* Status de pagamento: NÃO PAGO / PARCIAL / PAGO

## Ações
 
* Editar
* Alterar Status
* Anexar Comprovante
* Registrar Pagamento
## Regras
 
* O campo forma_pagamento do cadastro da venda é legado e não é mais
  exigido — cada pagamento individual define sua própria forma de
  pagamento.
* A comissão exibida continua sendo calculada sobre o valor total da
  venda, independente do quanto já foi pago.

---

# Tela 06 - Cadastro de Passeios

## Objetivo

Gerenciar passeios.

## Campos

* Nome
* Descrição
* Percentual Comissão

## Ações

* Novo
* Editar
* Desativar

---

# Tela 07 - Cadastro de Tipos de Passeio

## Objetivo

Gerenciar tipos de passeio.

## Campos

* Nome

## Ações

* Novo
* Editar
* Desativar

---

# Tela 08 - Cadastro de Embarcações

## Objetivo

Gerenciar embarcações.

## Campos

* Nome
* Capacidade
* Observação

## Ações

* Novo
* Editar
* Desativar

---

# Tela 09 - Relatório de Vendas

## Filtros

* Período
* Passeio
* Status
* Recepcionista

## Indicadores

* Total Vendido
* Total de Comissões
* Quantidade de Passageiros

---

# Tela 10 - Relatório de Comissões

## Filtros

* Período
* Recepcionista

## Exibir

* Total Vendido
* Total de Comissão
* Quantidade de Vendas

---

# Tela 11 - Usuários

## Objetivo

Gerenciar acesso ao sistema.

## Campos

* Nome
* E-mail
* Perfil

## Ações

* Novo
* Editar
* Desativar

---

# Tela 12 - Listagem de Grupos (Módulo de Grupos)

## Objetivo

Consultar grupos de hospedagem cadastrados. Ver docs/GRUPOS.md.

## Filtros

* Nome
* Status
* Entrada a partir de / Entrada até

## Colunas

* Código
* Nome (+ responsável)
* Intermediário (agência, guia ou "Direto")
* Período
* Apartamentos (faturados + cortesia)
* Valor Total (Sistema) — RN-G027, base financeira do grupo (Fase 8.1)
* Status

## Ações

* Visualizar
* Editar

## Acesso

ADMIN, GERENCIA, RECEPCAO.

---

# Tela 13 - Novo/Editar Grupo (Módulo de Grupos)

## Objetivo

Cadastrar ou editar os dados gerais de um grupo de hospedagem. A partir da
Fase 7.2, **não inclui mais tarifa** — a composição por tipo de
apartamento é montada na tela de detalhes, depois de salvar (RN-G020).

## Campos

### Identificação
* Nome do Grupo (obrigatório)
* Responsável, Telefone, E-mail

### Intermediário
* Agência (opcional) — link "+ Nova Agência" abre um modal de criação
  rápida (Fase 8.3, RN-G030), sem sair da tela nem perder os dados já
  preenchidos no resto do formulário; salva via AJAX e seleciona a
  agência recém-criada automaticamente
* Guia (opcional) — mesmo mecanismo de criação rápida via modal ("+ Novo
  Guia")

### Período e Ocupação
* Data de Entrada / Data de Saída (obrigatórios; saída > entrada)
* Quantidade de Hóspedes
* Apartamentos de Cortesia
* Apartamentos Faturados — na edição, exibido somente-leitura (calculado
  a partir da composição; não existe no formulário de criação, já que um
  grupo novo ainda não tem composição)
* Quantidade Prevista de Apartamentos (opcional, só no formulário de
  criação — Fase 8.2, RN-G028): referência informativa; se a composição
  real depois ultrapassar esse número, um alerta não-bloqueante aparece
  na aba Dados Gerais

### Prazos (Fase 7.2)
* Prazo Deadline (opcional)
* Prazo Roomlist (opcional)
* Informativos — não afetam valor, quantidade nem a verificação de
  divergência do orçamento (RN-G021)

### Outros
* Observação

## Ações

* Salvar
* Cancelar

## Acesso

ADMIN, GERENCIA, RECEPCAO.

---

# Tela 14 - Detalhes do Grupo (Módulo de Grupos)

## Objetivo

Visualizar e operar um grupo através de abas navegadas por query param
(`/grupos/{id}?tab=...`). Todas as seis abas ativas desde a Fase 6.

## Cabeçalho Fixo (visível em todas as abas)

* Nome do grupo, Status, Período, Valor Total (Sistema), Valor Pago /
  Saldo — base financeira é o valor sistema (RN-G027, Fase 8.1)

## Aba Dados Gerais

* **Alertas não-bloqueantes (Fase 8.2, RN-G028/RN-G029):** exibidos no
  topo da aba quando aplicável — composição já ultrapassou a quantidade
  prevista de apartamentos; prazo de roomlist vencido ou a 7 dias/menos
  do vencimento (só enquanto ainda houver linha vazia na roomlist); prazo
  de pagamento (deadline) vencido ou a 7 dias/menos do vencimento (só
  enquanto o saldo for maior que zero). Puramente informativos, não
  impedem nenhuma ação.
* Identificação, Intermediário, Período e Ocupação (em modo leitura)
* **Tarifa por Tipo de Apartamento (Fase 7.2, RN-G020):** tabela editável
  em linha, uma linha por tipo usado — Tipo (somente leitura após criada),
  Quantidade, Diária Net, Diária Sistema, Subtotal Net e Subtotal Sistema
  (calculados, somente exibição). Formulário para adicionar um novo tipo,
  com diárias pré-preenchidas via JS a partir do padrão do
  `tipos_apartamento` selecionado (RN-G005), livremente sobrescrevíveis.
  Rejeita tipo já adicionado ao grupo — o usuário edita a linha existente.
* Abaixo da tabela: Valor Total (Sistema) — destaque, base financeira do
  grupo (RN-G027) — e Valor Total Net como referência secundária de
  agência/comissão (soma das linhas); quando não-manual, mostra um
  pequeno formulário "Sobrescrever
  manualmente"; quando manual, mostra aviso + ação "Recalcular" para
  voltar ao automático (RN-G003/RN-G020). Comissão Retida e Percentual
  Efetivo — apenas exibição.
* Prazos (Fase 7.2): Prazo Deadline, Prazo Roomlist
* Painel lateral: Alterar Status (com aviso de que cancelamento é
  restrito a ADMIN/GERENCIA — RN-G010) e Informações (usuário/datas)

## Acesso

ADMIN, GERENCIA, RECEPCAO. Cancelamento de grupo restrito a ADMIN e
GERENCIA (RN-G010).

## Aba Roomlist (Fase 6, revisado nas Fases 7.4 e 8.4/8.5)

* **Sincronizada automaticamente com a composição do grupo (Fase 8.4,
  RN-G032):** alterar a quantidade de um tipo na aba Dados Gerais cria ou
  remove linhas vazias aqui (linha vazia = "A definir", sem hóspede
  preenchido). Reduzir quantidade ou remover um tipo inteiro é **recusado
  com mensagem clara** se isso exigisse apagar uma linha que já tem
  hóspede cadastrado — o usuário precisa remover o hóspede manualmente
  primeiro.
* **Exportação (Fase 8.5, RN-G033):** botões "Exportar PDF" e "Exportar
  Excel" no topo da aba — roomlist completa, agrupada por tipo de
  apartamento na ordem do cadastro (`ordem`), linha vazia mostrada como
  "A definir"
* Lista de apartamentos e hóspedes com edição em linha (cada registro é
  seu próprio formulário, sem tela de edição separada)
* Campos: apartamento, hóspede, documento, **tipo de apartamento (select
  do cadastro `tipos_apartamento` — RN-G023, substituiu o texto livre)**,
  cortesia, check-in, check-out, observação
* Formulário para adicionar novo registro no final da lista
* Remoção física (não é registro financeiro) — exceto pela proteção
  acima quando a remoção vem do lado da composição
* **Upload de anexo (RN-G024):** formulário próprio na aba, reaproveitando
  a mesma rota de `/grupos/{id}/anexos` com `tipo=ROOMLIST` pré-selecionado
  — geralmente é a agência quem envia a roomlist pronta. O mesmo registro
  também aparece na aba Anexos (não duplica linha).

## Aba Anexos (Fase 6)

* Lista de anexos (comprovantes de pagamento, orçamentos assinados,
  roomlist, outros) com tipo, tamanho, data de envio e quem enviou
* Upload com seleção de tipo + arquivo (PDF, JPG, JPEG, PNG, máx. 10 MB) —
  mesma validação de extensão/MIME/tamanho dos comprovantes de venda
* Download e remoção (soft delete — o arquivo é mantido em disco)

## Aba Atividade (Fase 6, revisado na Fase 7.5)

* Linha do tempo única, ordem cronológica decrescente, unindo comentários
  dos usuários e o histórico automático de alterações (RN-G009) desde a
  Fase 3
* **Identificação inequívoca de cada evento (RN-G026):** cada linha do
  histórico mostra um identificador específico em negrito, buscado por
  join a partir do `entidade_id` — "Orçamento v{versão}", "Pagamento de
  {data} — R$ {valor}", "Roomlist — {hóspede}", "Anexo — {nome do
  arquivo}", "Dados do Grupo"
* **Horário exato** (`dd/mm/aaaa hh:mm:ss`, com segundos) em vez de só a
  data, para que a ordem entre eventos próximos fique visível
* Formulário para novo comentário
* Filtro "Mostrar apenas comentários" / "Mostrar tudo"

## Aba Pagamentos (Fase 5)

* Resumo financeiro: valor total (sistema), valor pago, saldo — sempre
  sobre o valor sistema (RN-G027, revoga RN-G001), refletido também no
  cabeçalho fixo. Valor total net exibido como referência secundária de
  agência/comissão.
* Histórico completo de recebimentos (data, valor, forma, observação,
  quem registrou); lançamentos negativos aparecem destacados
* Formulário para registrar novo pagamento (valor, data, forma opcional,
  observação opcional)
* Nenhuma ação de exclusão — correção de lançamento errado é feita
  registrando um novo pagamento com valor negativo (RN-G008)

## Aba Orçamentos (Fase 4, revisado na Fase 7.3)

* Aviso no topo quando a versão vigente está `desatualizado` (RN-G012),
  destacando o botão "Gerar Novo Orçamento"
* Formulário para gerar nova versão: motivo (opcional), validade
  (opcional), condições adicionais (opcional) — sempre ação explícita do
  usuário, nunca automática
* Lista de versões em ordem decrescente, cada uma com: quantidades,
  valor total, valor pago/saldo congelados na época, motivo, badges de
  status e de desatualizado
* Ações por versão: Gerar PDF (qualquer status), Marcar como Enviado
  (somente se `RASCUNHO`), Aprovar/Recusar (somente se ainda não
  finalizada)
* Nenhuma ação altera uma versão já salva além do próprio `status`/
  `desatualizado` — os valores congelados nunca mudam (RN-G006)
* **PDF (RN-G022, substitui a revogada RN-G016):** logo do hotel, tabela
  por tipo de apartamento com as duas tarifas (net e sistema) lado a
  lado, subtotal por tipo, quantidade total, valor total geral nos dois
  tarifários, pagamentos itemizados, saldo, status do grupo e os dois
  prazos — tudo lido do snapshot da versão, nunca recalculado. **Fase
  8.1, RN-G027/RN-G034:** o destaque visual (bloco verde/negrito) passou
  a ser o valor total sistema; o valor total net permanece exibido, mas
  como referência secundária de agência/comissão.

---

# Tela 17 - Cadastro de Tipos de Apartamento (Módulo de Grupos)

## Objetivo

Gerenciar o catálogo fixo de tipos de apartamento do hotel — Solteiro,
Casal, Duplo, Triplo, Quádruplo, Suíte Master I, Suíte Master II — usado
na composição de tarifa dos grupos e no campo "tipo de apartamento" da
roomlist (RN-G019). **Fase 8.2, RN-G031:** "Duplo/Casal" foi separado em
dois tipos distintos por migration de dados (cadastral, sem impacto em
cálculo).

## Campos

* Nome (obrigatório, único)
* Ordem de Exibição
* Diária Net Padrão / Diária Sistema Padrão — apenas referência, pré-
  preenchem a linha ao adicionar o tipo num grupo (RN-G005)
* Observação

## Ações

* Novo
* Editar
* Desativar

## Acesso

ADMIN, GERENCIA — em **Cadastros**, não em Grupos (é catálogo fixo do
hotel, diferente de agências/guias, que a recepção cria durante a
negociação).

---

# Tela 15 - Cadastro de Agências (Módulo de Grupos)

## Objetivo

Gerenciar agências intermediárias de grupos de hospedagem. Ver docs/GRUPOS.md.

## Campos

* Nome (obrigatório)
* Nome Fantasia
* CNPJ
* Pessoa de Contato
* Telefone
* E-mail
* Percentual de Comissão Padrão (pré-preenche a sugestão de diária a lançar
  no sistema ao criar um grupo — RN-G002/RN-G005; zero quando não informado)
* Observação

## Ações

* Novo
* Editar
* Desativar

## Acesso

ADMIN, GERENCIA, RECEPCAO.

---

# Tela 16 - Cadastro de Guias (Módulo de Grupos)

## Objetivo

Gerenciar guias turísticos intermediários de grupos de hospedagem. Ver
docs/GRUPOS.md.

## Campos

* Nome (obrigatório)
* CPF
* Cadastur
* Telefone
* E-mail
* Percentual de Comissão Padrão (mesmas regras de Agências)
* Observação

## Ações

* Novo
* Editar
* Desativar

## Acesso

ADMIN, GERENCIA, RECEPCAO.

---

# Navegação Principal

Dashboard

Vendas
├── Listagem
├── Nova Venda

Grupos
├── Grupos (listagem/detalhe)
├── Agências
├── Guias

Cadastros
├── Passeios
├── Tipos de Passeio
├── Embarcações
├── Tipos de Apartamento

Relatórios
├── Vendas
├── Comissões

Administração
├── Usuários
