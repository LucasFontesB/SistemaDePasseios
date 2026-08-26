# GRUPOS.md

# Objetivo

Módulo de organização de grupos de hospedagem.

Controla a negociação, o orçamento, o recebimento e a operação de grupos vendidos por agências de turismo e guias turísticos, sob regime de **tarifa net**.

---

# Conceito Central: Tarifa Net

Agências e guias operam da mesma forma financeira: retêm a própria comissão e repassam o líquido ao hotel.

Por isso o sistema controla dois valores distintos por diária:

| Valor | Significado |
| ----- | ----------- |
| Diária Net | O que o hotel efetivamente recebe do intermediário |
| Diária Sistema | O que a recepção lança no PMS do hotel |

A comissão retida nunca é digitada. É derivada:

```
valor_comissao = valor_total_sistema - valor_total_net
percentual_efetivo = valor_comissao / valor_total_sistema * 100
```

## RN-G001 — REVOGADA E SUBSTITUÍDA POR RN-G027

~~Pagamentos, saldo e receita em relatórios são sempre calculados sobre o valor net.~~ Decisão revertida a pedido do usuário: na prática, o que o hotel efetivamente recebe e controla é o valor sistema. O net passa a ser referência de composição/comissão com a agência, não a base financeira do hotel.

## RN-G027

A base de cálculo financeiro do módulo passa a ser o **valor sistema**, não mais o net:

* `Grupo.valor_pago` continua somando `grupos_pagamentos` normalmente, mas agora é comparado contra `valor_total_sistema`.
* `Grupo.saldo = valor_total_sistema - valor_pago`.
* O snapshot do orçamento (`valor_pago_snapshot`, `saldo_snapshot`) passa a ser calculado sobre sistema.
* Cabeçalho fixo, listagem de grupos e resumo do grupo mostram o valor sistema como o "valor total" principal — net vira informação secundária, rotulada como referência de agência/comissão.
* A aba Pagamentos mostra o resumo financeiro (total, pago, saldo) em cima do sistema.

O que **não muda**: a fórmula de comissão retida continua sendo a diferença entre os dois tarifários (`valor_total_sistema - valor_total_net`), e o PDF do orçamento (RN-G022) continua mostrando as duas tarifas lado a lado por tipo — net não desaparece da tela, só deixa de ser a base de "quanto o hotel vai receber".

Aplica-se retroativamente a toda a documentação e telas já implementadas nas Fases 1 a 7 — ver RN-G034 para o levantamento de todos os pontos afetados.

## RN-G002

**[SUPERSEDIDA pela composição por tipo de apartamento — ver seção "Tarifa por Tipo de Apartamento" e RN-G019/RN-G020]**

A diária deixa de ser um valor único por grupo. Cada tipo de apartamento usado no grupo tem sua própria diária net e diária sistema, sugeridas a partir do cadastro `tipos_apartamento` e editáveis livremente por linha.

---

# Tarifa por Tipo de Apartamento

O hotel possui tipos de apartamento com valores diferentes entre si: Solteiro, Casal, Duplo, Triplo, Quádruplo, Suíte Master I e Suíte Master II.

A partir desta revisão, o grupo não tem mais uma única diária — ele é composto por **uma linha por tipo de apartamento usado**, cada uma com sua própria quantidade e diária (net e sistema).

## RN-G031

`Casal` e `Duplo` são tipos distintos, não um só — a diferença é a configuração de cama, que importa para reserva e limpeza:

* **Casal**: 1 cama de casal
* **Duplo**: 2 camas de solteiro, ou 1 cama de casal + 1 cama de solteiro

O cadastro `tipos_apartamento` original tinha "Duplo/Casal" como um único tipo; ele é dividido em dois, preservando o `id` do tipo original para não quebrar grupos já criados com esse tipo (vira "Casal" ou "Duplo", a critério do usuário na correção manual, já que não dá para inferir automaticamente qual configuração era usada). Um segundo tipo novo é criado para o que sobrar.

## RN-G019

Novo cadastro **tipos_apartamento**: `nome`, `ordem` (para exibição sempre na mesma sequência), `valor_diaria_net_padrao`, `valor_diaria_sistema_padrao`, `observacao`, soft delete.

Menu: **Cadastros** (não Grupos) — restrito a ADMIN e GERENCIA, junto com Passeios/Tipos de Passeio/Embarcações. É catálogo fixo do hotel, diferente de agências e guias, que são cadastros operacionais que a recepção cria durante a negociação.

Os valores padrão são apenas **referência**: pré-preenchem a diária ao adicionar o tipo num grupo, mas o valor gravado na linha do grupo é sempre o que foi editado ali, igual ao padrão já usado em `percentual_comissao_padrao` de agências/guias (RN-G005).

## RN-G020

Nova tabela **grupos_apartamentos**: uma linha por tipo de apartamento usado no grupo — `tipo_apartamento_id`, `quantidade`, `valor_diaria_net`, `valor_diaria_sistema`.

Esta tabela é a **fonte de verdade** para valor e ocupação faturada do grupo. O que antes eram os campos únicos `valor_diaria_net`/`valor_diaria_sistema`/`qtd_apartamentos` do grupo agora são **agregados calculados**, sincronizados a cada alteração de linha:

```
qtd_apartamentos       = SOMA(quantidade) de todas as linhas
valor_total_net         = SOMA(quantidade × valor_diaria_net × noites) de todas as linhas
valor_total_sistema     = SOMA(quantidade × valor_diaria_sistema × noites) de todas as linhas
```

As flags `valor_total_net_manual` e `valor_total_sistema_manual` continuam existindo, mas agora atuam **sobre o agregado**, não sobre uma fórmula única — útil para um desconto fechado negociado por cima da soma das linhas (RN-G003 continua valendo: alteração nas linhas nunca sobrescreve um total marcado como manual).

`qtd_apartamentos_cortesia` (RN-G015) continua como campo único do grupo, não quebrado por tipo — cortesia é contagem simples de ocupação, sem entrar em nenhum cálculo de valor.

## RN-G028

Volta um campo `qtd_apartamentos_prevista` no grupo, preenchido na criação — quantidade total de apartamentos que o usuário espera usar, antes de montar a composição por tipo. É puramente informativo, opcional, não trava nada.

Sempre que a soma das linhas de `grupos_apartamentos` (`qtd_apartamentos`) ultrapassar `qtd_apartamentos_prevista`, a aba Dados Gerais exibe um alerta: "Composição atual (X apartamentos) já passou da quantidade prevista na criação (Y)." Não bloqueia — apenas avisa, porque a composição real é sempre a fonte de verdade (RN-G020); a previsão é só uma referência de planejamento.

## RN-G015

Apartamentos de cortesia são controlados em campo próprio — `qtd_apartamentos_cortesia`.

Eles contam para ocupação e aparecem na roomlist, mas **não entram em nenhum cálculo de valor**.

```
apartamentos_ocupados = qtd_apartamentos + qtd_apartamentos_cortesia
```

`qtd_apartamentos` representa apenas os apartamentos faturados. É esse o número usado nas fórmulas acima.

Comportamento:

* Flag `false`: o valor é recalculado a cada alteração de diária, apartamentos ou datas.
* Flag `true`: o valor digitado é preservado. A tela exibe o valor calculado ao lado como referência, com ação "recalcular" para voltar ao automático.

`noites` é derivado de `data_saida - data_entrada`. Não é coluna.

## RN-G003

Alterar datas ou quantidade de apartamentos nunca pode sobrescrever um valor marcado como manual.

---

# Cadastros Novos

## agencias

Menu: seção **Grupos** na sidebar (não em Cadastros) — liberada para ADMIN, GERENCIA e RECEPCAO, junto com o item principal do módulo.

Soft delete obrigatório.

## guias

Menu: seção **Grupos** na sidebar (não em Cadastros) — liberada para ADMIN, GERENCIA e RECEPCAO, junto com o item principal do módulo.

Soft delete obrigatório.

## RN-G004

Um grupo possui no máximo uma agência e no máximo um guia. Ambos são opcionais — grupo direto, sem intermediário, é válido.

## RN-G005

Os valores padrão do cadastro apenas pré-preenchem o formulário. O que vale para o grupo é sempre o valor gravado no próprio grupo.

## RN-G030

O formulário de criação/edição de grupo permite cadastrar uma agência ou guia novo sem sair da tela — um link "+ Nova Agência" / "+ Novo Guia" ao lado do select, abrindo um formulário rápido (mesmos campos do cadastro completo, só `nome` obrigatório — RN-G011) que grava via requisição assíncrona e seleciona automaticamente o registro criado, sem descartar o que já foi preenchido no restante do formulário do grupo.

## RN-G011

Nos cadastros de agências e guias, apenas `nome` é obrigatório. Todos os demais campos são opcionais, inclusive `percentual_comissao_padrao`, que assume zero quando não informado.

Percentual zero significa apenas que não há sugestão automática para o valor a lançar no sistema. O campo continua editável.

---

# Tela de Grupos

O item principal na sidebar é **Grupos**. Agências e Guias ficam na mesma seção de menu, como cadastros de apoio — não dentro do menu Cadastros restrito (que continua só ADMIN/GERENCIA).

A tela de detalhe do grupo em si é dividida em abas, navegadas por query param:

```
/grupos/{id}?tab=orcamentos
```

Cada aba carrega apenas os dados que precisa. Todo POST redireciona de volta para a aba de origem.

## Cabeçalho Fixo

Visível em todas as abas:

* Nome do grupo
* Status
* Período
* Valor total (sistema) — RN-G027/RN-G034: passou a ser o valor sistema, não mais net
* Valor pago
* Saldo (sobre o valor sistema)

## RN-G029

A tela do grupo (Dados Gerais) exibe alertas de prazo, não bloqueantes:

* **Prazo Roomlist** (`prazo_roomlist`): se estiver a 7 dias ou menos de vencer, ou já vencido, e a roomlist ainda tiver linhas sem hóspede preenchido, mostra aviso — "Prazo de envio da roomlist vence em X dias" / "Prazo de roomlist vencido há X dias."
* **Prazo Deadline** (`prazo_deadline`): se estiver a 7 dias ou menos de vencer, ou já vencido, e o saldo (RN-G027) ainda for maior que zero, mostra aviso — "Prazo de pagamento vence em X dias" / "Prazo de pagamento vencido há X dias."

Sem prazo preenchido, sem alerta — RN-G021 continua valendo (campos opcionais, sem padrão).

## Aba 1 — Dados Gerais

Seções:

### Identificação
* Código
* Nome do grupo
* Responsável
* Telefone
* E-mail

### Intermediário
* Agência
* Guia

### Período e Ocupação
* Data de entrada
* Data de saída
* Noites (calculado)
* Quantidade de hóspedes
* Quantidade de apartamentos faturados
* Quantidade de apartamentos de cortesia
* Total de apartamentos ocupados (calculado)

### Tarifa por Tipo de Apartamento
Tabela editável, uma linha por tipo usado:
* Tipo de apartamento (select do cadastro `tipos_apartamento`)
* Quantidade
* Diária net (sugerida pelo padrão do tipo, editável)
* Diária sistema (sugerida pelo padrão do tipo, editável)
* Subtotal net e subtotal sistema (calculados, somente exibição)

Abaixo da tabela:
* Valor total net (soma das linhas; editável se marcado como manual — RN-G020)
* Valor total sistema (idem)
* Comissão retida (calculada)
* Percentual efetivo (calculado)

### Prazos
* Prazo Deadline (opcional)
* Prazo Roomlist (opcional)

### Outros
* Status
* Observação

## RN-G021

`prazo_deadline` e `prazo_roomlist` são datas opcionais, sem valor padrão. Não entram na verificação de divergência do orçamento (RN-G012) — são informativos, não afetam valor ou quantidade.

## Aba 2 — Orçamentos

Lista de versões em ordem decrescente.

Cada versão é um registro imutável com snapshot completo dos valores da época.

Ações:

* Gerar novo orçamento — cria a próxima versão com os valores atuais do grupo
* Gerar PDF de qualquer versão
* Marcar como enviado
* Aprovar
* Recusar

Nenhuma ação altera versão já salva.

## RN-G006

Todo orçamento salvo é um registro permanente e imutável, independente do status.

Nenhuma alteração no grupo modifica um orçamento já salvo. Cada versão preserva exatamente o que foi enviado ao cliente naquela data.

## RN-G012

A geração de nova versão é **ação manual do usuário**. O sistema nunca cria versão automaticamente.

Quando o grupo diverge do último orçamento gerado — desistência de quartos, mudança de tarifa, acréscimo de apartamentos, entrada de pagamento — o sistema apenas sinaliza:

* O orçamento vigente recebe `desatualizado = TRUE`
* A aba exibe aviso de que o documento enviado não reflete mais o grupo
* O botão "Gerar novo orçamento" fica em destaque

O usuário decide se e quando gerar. O novo orçamento nasce com os valores atuais do grupo, na próxima versão da sequência.

## RN-G017

Todo pagamento registrado — mesmo um recebimento de rotina, sem qualquer mudança estrutural — dispara a verificação de divergência (RN-G012) e marca o orçamento vigente como desatualizado, já que `valor_pago_snapshot` e `saldo_snapshot` deixam de refletir a realidade a partir do primeiro pagamento seguinte à geração da versão.

Essa é uma decisão consciente: o aviso pode se tornar frequente em grupos com pagamentos parcelados, mas o alternativa — silenciar o aviso para pagamentos — deixaria o saldo do PDF desatualizado sem qualquer sinalização visível.

## RN-G013

O snapshot do orçamento congela **tudo que pode mudar depois** — reimprimir uma versão antiga deve reproduzir o documento exatamente como foi enviado, mesmo que o grupo tenha mudado inteiro desde então. Isso agora inclui:

* Data de entrada e saída (`data_entrada_snapshot`, `data_saida_snapshot`)
* Status do grupo no momento da geração (`status_snapshot`)
* Prazos (`prazo_deadline_snapshot`, `prazo_roomlist_snapshot`)
* **Composição completa por tipo de apartamento** — nova tabela `grupos_orcamentos_apartamentos`: uma linha congelada por tipo, com nome do tipo (texto, não FK — se o cadastro for renomeado depois, o documento antigo continua mostrando o nome de quando foi gerado), quantidade, diária net, diária sistema, subtotal net e subtotal sistema
* **Pagamentos itemizados**, não só o total — nova tabela `grupos_orcamentos_pagamentos`: uma linha congelada por pagamento existente até o momento da geração (valor, data, forma de pagamento)
* Valor pago total e saldo (`valor_pago_snapshot`, `saldo_snapshot`)

Nada disso é recalculado na hora de reimprimir. O PDF de uma versão antiga sempre lê exclusivamente das tabelas de snapshot dessa versão.

## RN-G014

Cada versão pode registrar um `motivo` livre — "desistência de 3 quartos", "entrada de 50%", "inclusão de cortesia". Campo opcional, mas é o que dá leitura à evolução da negociação.

## RN-G016 — REVOGADA E SUBSTITUÍDA POR RN-G022

~~O PDF do orçamento exibe apenas o valor net.~~ Decisão revertida a pedido do usuário: o PDF passa a mostrar as duas tarifas.

## RN-G022

O PDF do orçamento exibe, por tipo de apartamento: quantidade, diária net, diária sistema e o valor total de cada tipo (nos dois tarifários). Ao final: quantidade total de apartamentos, valor total geral (net e sistema), registro de cada pagamento recebido, saldo restante, status do grupo, prazo deadline e prazo roomlist — tudo lido do snapshot da versão (RN-G013), nunca recalculado.

## RN-G025

O cabeçalho do PDF exibe a logo do hotel (`app/static/img/logo.png`).

## RN-G007

Aprovar um orçamento copia seus valores para o grupo e sugere alterar o status para CONFIRMADO.

## Aba 3 — Pagamentos

Histórico completo de recebimentos.

Exibe valor total, valor pago acumulado e saldo — sobre o **valor sistema** (RN-G027).

## RN-G008

Pagamentos nunca são excluídos. Correções são feitas por lançamento de valor negativo.

## Aba 4 — Roomlist

Lista de apartamentos e hóspedes.

Campos: apartamento, hóspede, documento, tipo de apartamento, check-in, check-out, observação.

## RN-G023

`tipo_apartamento` na roomlist deixa de ser texto livre e passa a referenciar o cadastro `tipos_apartamento` (RN-G019) — mesmo dropdown usado na composição de tarifa do grupo, para manter os nomes consistentes entre roomlist e cobrança.

## RN-G032

A composição por tipo (`grupos_apartamentos`) gera automaticamente as linhas da roomlist correspondentes:

* Ao adicionar uma linha de composição com quantidade N de um tipo, o sistema cria N linhas vazias na roomlist para aquele tipo (`hospede_nome = NULL`, aguardando preenchimento).
* Ao **aumentar** a quantidade de uma linha existente, cria as linhas extras necessárias.
* Ao **diminuir** a quantidade, remove primeiro as linhas ainda vazias daquele tipo. Se não houver linhas vazias suficientes (ou seja, o usuário já preencheu hóspedes além do que a redução permite), a redução é **rejeitada** com uma mensagem clara — nunca apaga um hóspede já cadastrado.
* Ao **remover** a linha de composição inteira, mesma regra: só remove se todas as linhas de roomlist daquele tipo ainda estiverem vazias; senão, rejeita e pede para o usuário remover os hóspedes manualmente primeiro.

Isso exige tornar `grupos_roomlist.hospede_nome` **opcional** (deixa de ser `NOT NULL`) — uma linha "aguardando preenchimento" é um estado válido, não um erro de dado incompleto.

## RN-G033

A aba Roomlist ganha exportação em **PDF** e **Excel (.xlsx)** da lista completa (apartamento, hóspede, documento, tipo, check-in/out, observação), agrupada por tipo de apartamento na mesma ordem do cadastro (`ordem`). Linhas ainda vazias aparecem como "A definir".

## RN-G024

A aba Roomlist permite anexar arquivo — geralmente é a agência quem envia a roomlist pronta. Reaproveita a mesma infraestrutura de `grupos_anexos` (RN-G018), com um tipo próprio (`ROOMLIST`) na lista de tipos de anexo.

O anexo enviado por ali aparece **nas duas abas**: um upload rápido dentro da própria aba Roomlist (já com o tipo pré-selecionado) e também na listagem geral da aba Anexos — é o mesmo registro, só duas portas de entrada/visualização.

## Aba 5 — Anexos

Comprovantes de pagamento e orçamentos assinados.

Formatos: PDF, JPG, JPEG, PNG. Máximo 10 MB.

Nome interno gerado por UUID, conforme SECURITY.md.

## RN-G018

Diferente de `comprovantes` (vendas), que usa exclusão física, anexos de grupo usam **soft delete** (`removido_em`). O arquivo permanece em disco após a remoção lógica — decisão deliberada, alinhada com o restante do módulo, que preserva trilha de auditoria em tudo que é financeiro ou documental (pagamentos nunca somem, orçamentos nunca são reescritos).

## Aba 6 — Atividade

Linha do tempo única, em ordem cronológica, unindo:

* Comentários dos usuários
* Registro automático de todas as alterações

Filtro para exibir apenas comentários.

## RN-G026

Cada evento na timeline precisa se identificar de forma inequívoca — não basta dizer "Orçamento foi editado" quando o grupo tem várias versões, nem "Pagamento registrado" quando há vários pagamentos no histórico.

Cada linha exibe:

* **Horário exato** (não só a data), para que a ordem entre eventos próximos fique visível sem ambiguidade
* Um identificador específico do registro afetado, buscado por join a partir do `entidade_id`:
  * `ORCAMENTO` → "Orçamento v{versao}"
  * `PAGAMENTO` → "Pagamento de {data_pagamento} — R$ {valor}"
  * `ROOMLIST` → "Roomlist — {hospede_nome}"
  * `ANEXO` → "Anexo — {nome_original}"
  * `GRUPO` → "Dados do grupo" (não precisa de identificador adicional, só existe um)

Sem isso, dois orçamentos editados em sequência aparecem como eventos indistinguíveis, o que já foi reportado como confuso na prática.

---

# Log de Alterações

## RN-G009

Toda alteração em qualquer entidade do grupo gera registro em `grupos_historico`, com uma linha por campo alterado.

Registrado na camada de **service**, não em event listener do SQLAlchemy — o listener não tem acesso ao usuário da sessão e produziria log anônimo.

Cada registro grava:

* Quem
* Quando
* Qual entidade e qual registro
* Qual campo
* Valor anterior
* Valor novo

## Entidades Rastreadas

* GRUPO
* ORCAMENTO
* PAGAMENTO
* ROOMLIST
* ANEXO
* COMENTARIO

## Ações

* CRIACAO
* EDICAO
* EXCLUSAO
* STATUS

---

# Status do Grupo

Fluxo principal:

```
PROSPECCAO
↓
ORCAMENTO_ENVIADO
↓
EM_NEGOCIACAO
↓
CONFIRMADO
↓
HOSPEDADO
↓
FINALIZADO
```

Saídas:

* CANCELADO — grupo confirmado que caiu
* PERDIDO — negociação que não fechou

A distinção importa para o relatório de conversão.

## Status do Orçamento

* RASCUNHO
* ENVIADO
* APROVADO
* RECUSADO

---

# Permissões

O módulo de grupos é liberado para todos os perfis:

* ADMIN
* GERENCIA
* RECEPCAO

## RN-G010

O cancelamento de grupo é restrito a ADMIN e GERENCIA.

## Impacto na Documentação

Esta liberação altera o previsto em SECURITY.md e SCREEN_FLOW.md, que hoje limitam RECEPCAO a Dashboard e Vendas. Ambos precisam ser atualizados.

---

# Exclusão

Grupos nunca são excluídos fisicamente.

Cadastros de agências e guias utilizam soft delete.

Registros financeiros — orçamentos e pagamentos — nunca são removidos.

---

# RN-G034 — Varredura: Sistema como valor primário

Consequência de RN-G027: em toda a interface, o valor sistema passa a ser o "valor principal" exibido, e o net vira informação secundária (rótulo "referência agência/comissão"), nos seguintes pontos:

* Cabeçalho fixo do grupo (já coberto na seção "Tela de Grupos")
* Listagem de Grupos — coluna de valor total mostra sistema
* Aba Pagamentos — resumo financeiro sobre sistema (RN-G027)
* Resumo/visão geral do grupo em Dados Gerais
* PDF do orçamento (RN-G022) — continua mostrando as duas tarifas por tipo lado a lado (isso não muda), mas o total geral e o saldo em destaque usam sistema; net aparece como coluna auxiliar

O que continua sendo net, propositalmente, porque é sobre a relação com o intermediário, não sobre o caixa do hotel:

* Diária/valor negociado na composição por tipo (`grupos_apartamentos`) continua tendo as duas colunas — net é o que se acerta com a agência
* Cálculo de comissão retida (`sistema - net`)
* Percentual efetivo

---

# Escopo de Implementação

**Status: Etapa 1, Etapa 2 e Etapa 3 (Fase 7) concluídas. Etapa 4 (Fase 8, ajustes de uso real) em andamento.**

## Etapa 1 — Concluída

* Cadastro de agências
* Cadastro de guias
* Tabela grupos
* Aba Dados Gerais
* Aba Orçamentos com geração de PDF
* Aba Pagamentos
* Log de alterações

## Etapa 2 — Concluída

* Aba Roomlist
* Aba Anexos
* Aba Atividade completa

## Etapa 3 — Fase 7: Revisão Estrutural (em andamento)

* Cadastro `tipos_apartamento` (RN-G019)
* Composição de tarifa por tipo (`grupos_apartamentos`), substituindo a diária única (RN-G020)
* Prazos deadline e roomlist no grupo (RN-G021)
* Snapshot completo do orçamento — breakdown por tipo, pagamentos itemizados, datas, status, prazos (RN-G013)
* PDF com logo, as duas tarifas por tipo e todos os dados do snapshot (RN-G022)
* Anexo na aba Roomlist, reaproveitando `grupos_anexos` (RN-G023/RN-G024)
* Timeline com identificação inequívoca de cada evento (RN-G026)

Como o ambiente ainda não tem dados reais, esta fase substitui o modelo antigo de diária única sem necessidade de migração de dados — as colunas `valor_diaria_net`/`valor_diaria_sistema` saem do grupo e a coluna `tipo_apartamento` (texto livre) sai da roomlist.

## Etapa 4 — Fase 8: Ajustes de Uso Real (em andamento)

* Base financeira invertida: sistema passa a ser o valor primário, net vira referência de agência (RN-G027/RN-G034)
* Quantidade de apartamentos prevista na criação, com alerta de excesso na composição (RN-G028)
* Alertas de prazo (roomlist e deadline) na tela do grupo (RN-G029)
* Criação rápida de agência/guia a partir do formulário de grupo (RN-G030)
* Split dos tipos Casal e Duplo (RN-G031)
* Geração automática de linhas de roomlist a partir da composição, bidirecional e protegida contra apagar hóspede preenchido (RN-G032)
* Exportação da roomlist em PDF e Excel (RN-G033)

## Pendência futura (fora do escopo atual)

* Relatório de grupos (indicadores de conversão por status, receita net por período). Não implementado — sem indicadores/filtros definidos ainda. Retomar quando houver demanda concreta de uso.

---

# Arquivos Previstos

```
app/models/grupo.py
app/models/agencia.py
app/models/guia.py
app/repositories/grupo_repository.py
app/repositories/agencia_repository.py
app/repositories/guia_repository.py
app/services/grupo_service.py
app/services/grupo_historico_service.py
app/services/orcamento_service.py
app/controllers/grupo_controller.py
app/controllers/agencia_controller.py
app/controllers/guia_controller.py
app/templates/grupos/listagem.html
app/templates/grupos/form.html
app/templates/grupos/detalhes.html
app/templates/grupos/tabs/*.html
app/utils/pdf_orcamento.py
```
