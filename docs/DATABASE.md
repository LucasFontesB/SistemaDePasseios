# DATABASE.md

# Visão Geral

O sistema será responsável por gerenciar:

* Usuários
* Passeios
* Tipos de Passeio
* Embarcações
* Vendas
* Comprovantes
* Comissões

---

# Convenções

## Chaves Primárias

Todas as tabelas utilizarão UUID como chave primária.

Exemplo:

id UUID PRIMARY KEY

---

## Auditoria

Todas as tabelas de cadastro possuirão:

criado_em TIMESTAMP NOT NULL

atualizado_em TIMESTAMP NOT NULL

deletado_em TIMESTAMP NULL

### Soft Delete

Registro ativo:

deletado_em = NULL

Registro removido:

deletado_em = 2026-06-10 14:30:00

Nenhum cadastro será removido fisicamente do banco.

---

# Tabela: usuarios

Controle de acesso ao sistema.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(150) |
| email         | VARCHAR(150) |
| senha_hash    | VARCHAR(255) |
| perfil        | VARCHAR(30)  |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

## Perfis

* ADMIN
* GERENCIA
* RECEPCAO

---

# Tabela: passeios

Cadastro dos passeios disponíveis.

| Campo               | Tipo         |
| ------------------- | ------------ |
| id                  | UUID         |
| nome                | VARCHAR(150) |
| descricao           | TEXT         |
| percentual_comissao | NUMERIC(5,2) |
| criado_em           | TIMESTAMP    |
| atualizado_em       | TIMESTAMP    |
| deletado_em         | TIMESTAMP    |

## Exemplos

* Maragogi
* Praia do Gunga
* Francês
* São Miguel dos Milagres

---

# Tabela: tipos_passeio

Classificação dos passeios.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(100) |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

## Exemplos

* Compartilhado
* Privativo
* Catamarã
* Lancha

---

# Tabela: embarcacoes

Cadastro das embarcações.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| nome          | VARCHAR(150) |
| capacidade    | INTEGER      |
| observacao    | TEXT         |
| criado_em     | TIMESTAMP    |
| atualizado_em | TIMESTAMP    |
| deletado_em   | TIMESTAMP    |

---

# Tabela: vendas

Tabela principal do sistema.

| Campo               | Tipo          |
| ------------------- | ------------- |
| id                  | UUID          |
| numero_venda        | VARCHAR(30)   |
| contratante         | VARCHAR(200)  |
| telefone            | VARCHAR(30)   |
| adultos             | INTEGER       |
| criancas            | INTEGER       |
| passeio_id          | UUID          |
| tipo_passeio_id     | UUID          |
| embarcacao_id       | UUID          |
| valor_total         | NUMERIC(10,2) |
| percentual_comissao | NUMERIC(5,2)  |
| valor_comissao      | NUMERIC(10,2) |
| data_saida          | DATE          |
| horario_saida       | TIME          |
| status              | VARCHAR(30)   |
| observacao          | TEXT          |
| usuario_id          | UUID          |
| criado_em           | TIMESTAMP     |
| atualizado_em       | TIMESTAMP     |

## Observações

* Não utilizar soft delete.
* Venda cancelada continua existindo.
* Histórico financeiro nunca deve ser removido.

---

## Status Permitidos

* PENDENTE
* AGUARDANDO_PAGAMENTO
* CONFIRMADO
* EMBARCADO
* FINALIZADO
* CANCELADO
* REEMBOLSADO

---

# Tabela: comprovantes

Arquivos anexados a uma venda.

| Campo         | Tipo         |
| ------------- | ------------ |
| id            | UUID         |
| venda_id      | UUID         |
| nome_original | VARCHAR(255) |
| nome_arquivo  | VARCHAR(255) |
| caminho       | VARCHAR(500) |
| tipo_arquivo  | VARCHAR(50)  |
| tamanho_bytes | BIGINT       |
| enviado_em    | TIMESTAMP    |

## Observações

* Arquivos serão armazenados no servidor.
* O banco armazenará apenas metadados.

---
 
# Tabela: pagamentos
 
Histórico de pagamentos recebidos referentes a uma venda.
 
| Campo           | Tipo          |
| --------------- | ------------- |
| id               | UUID          |
| venda_id         | UUID          |
| valor            | NUMERIC(10,2) |
| forma_pagamento  | VARCHAR(30)   |
| observacao       | TEXT          |
| usuario_id       | UUID          |
| criado_em        | TIMESTAMP     |
 
## Observações
 
* Uma venda pode possuir múltiplos pagamentos (ex: sinal pago por agência +
  saldo pago na recepção).
* O valor pago total da venda é a soma de todos os pagamentos não cancelados.
* Não há soft delete nem exclusão física: correções de lançamentos errados
  são feitas através de um novo registro com valor negativo (lançamento de
  ajuste), preservando o histórico financeiro completo (RN007).
* O campo forma_pagamento da tabela vendas é considerado legado a partir da
  introdução desta tabela e não deve mais ser exigido no cadastro/edição de
  venda. Cada pagamento individual carrega sua própria forma de pagamento.

## Status de Pagamento (calculado, não persistido)
 
Calculado dinamicamente a partir da soma dos pagamentos:
 
* NAO_PAGO — soma dos pagamentos <= 0
* PARCIAL — soma dos pagamentos > 0 e < valor_total da venda
* PAGO — soma dos pagamentos >= valor_total da venda
Este status é independente do campo status da venda (PENDENTE, CONFIRMADO,
EMBARCADO etc.) — uma venda pode estar CONFIRMADO e PARCIAL no pagamento
simultaneamente.

---

# Relacionamentos

usuarios (1)
└── vendas (N)

passeios (1)
└── vendas (N)

tipos_passeio (1)
└── vendas (N)

embarcacoes (1)
└── vendas (N)

vendas (1)
└── comprovantes (N)

vendas (1)
└── pagamentos (N)

---

# Índices Recomendados

## vendas

idx_vendas_numero

idx_vendas_contratante

idx_vendas_telefone

idx_vendas_status

idx_vendas_data_saida

idx_vendas_passeio

idx_vendas_usuario

idx_vendas_criado_em

## comprovantes

idx_comprovantes_venda

## pagamentos
 
idx_pagamentos_venda

---

# Estrutura de Upload

/uploads
/2026
/06
comprovante_001.pdf
comprovante_002.jpg

---

# Regras de Negócio

RN001

O valor da comissão será calculado automaticamente utilizando o percentual configurado para o passeio.

RN002

O percentual utilizado na venda será armazenado na própria venda para preservar o histórico.

RN003

Uma venda poderá possuir múltiplos comprovantes.

RN004

Cadastros removidos via soft delete não deverão aparecer nas telas de seleção.

RN005

Relatórios históricos deverão considerar registros removidos via soft delete.

RN006

A exclusão física de registros será proibida para usuários do sistema.

RN007

Todas as ações financeiras deverão permanecer rastreáveis para auditoria futura.

RN008
 
Uma venda poderá possuir múltiplos pagamentos. O valor pago total é a soma
de todos os pagamentos registrados.
 
RN009
 
A comissão é sempre calculada sobre o valor_total da venda, independente do
valor efetivamente pago até o momento.
 
RN010
 
Pagamentos nunca são excluídos. Correções são feitas através de um novo
lançamento de ajuste (valor negativo).

---

# Módulo de Grupos (Fase 1 — Agências e Guias)

Ver docs/GRUPOS.md para a especificação completa do módulo. As tabelas abaixo
foram criadas por migration SQL manual (fora do repositório) e já existem no
banco `passeios`.

# Tabela: agencias

Cadastro de agências intermediárias na venda de grupos de hospedagem.

| Campo                       | Tipo          |
| ---------------------------- | ------------- |
| id                            | UUID          |
| nome                          | VARCHAR(200)  |
| nome_fantasia                 | VARCHAR(200)  |
| cnpj                          | VARCHAR(20)   |
| contato                       | VARCHAR(150)  |
| telefone                      | VARCHAR(30)   |
| email                         | VARCHAR(150)  |
| percentual_comissao_padrao    | NUMERIC(5,2)  |
| observacao                    | TEXT          |
| criado_em                     | TIMESTAMP     |
| atualizado_em                 | TIMESTAMP     |
| deletado_em                   | TIMESTAMP     |

## Observações

* Apenas `nome` é obrigatório (RN-G011). Todos os demais campos são opcionais.
* `percentual_comissao_padrao` assume 0 quando não informado — zero significa
  apenas que não há sugestão automática de diária a lançar no sistema
  (RN-G011); o campo continua editável no grupo.
* Soft delete obrigatório (`deletado_em`).
* Os valores cadastrados aqui apenas pré-preenchem o formulário do grupo
  (RN-G005) — o que vale para o grupo é sempre o valor gravado no próprio
  grupo.

---

# Tabela: guias

Cadastro de guias turísticos intermediários na venda de grupos de hospedagem.

| Campo                       | Tipo          |
| ---------------------------- | ------------- |
| id                            | UUID          |
| nome                          | VARCHAR(200)  |
| cpf                           | VARCHAR(20)   |
| cadastur                      | VARCHAR(50)   |
| telefone                      | VARCHAR(30)   |
| email                         | VARCHAR(150)  |
| percentual_comissao_padrao    | NUMERIC(5,2)  |
| observacao                    | TEXT          |
| criado_em                     | TIMESTAMP     |
| atualizado_em                 | TIMESTAMP     |
| deletado_em                   | TIMESTAMP     |

## Observações

* Mesmas regras de `agencias`: apenas `nome` obrigatório (RN-G011), soft
  delete obrigatório, comissão padrão apenas pré-preenche o formulário do
  grupo (RN-G005).

---

---

# Tabela: tipos_apartamento (Fase 7.1)

Catálogo fixo do hotel — Solteiro, Casal, Duplo, Triplo, Quádruplo, Suíte
Master I, Suíte Master II (RN-G019). Cadastro operacional (Cadastros,
ADMIN/GERENCIA), diferente de agências/guias (seção Grupos).

**Fase 8.2 — RN-G031:** "Casal/Duplo" foi separado em dois tipos
distintos (Casal e Duplo) por migration de dados — grupos/composições
existentes que usavam o tipo combinado foram remapeados para o tipo
correspondente. Puramente cadastral, não alterou nenhum cálculo.

| Campo                        | Tipo          |
| ------------------------------ | ------------- |
| id                              | UUID          |
| nome                            | VARCHAR(50)   |
| ordem                           | INTEGER       |
| valor_diaria_net_padrao         | NUMERIC(10,2) |
| valor_diaria_sistema_padrao     | NUMERIC(10,2) |
| observacao                      | TEXT          |
| criado_em                       | TIMESTAMP     |
| atualizado_em                   | TIMESTAMP     |
| deletado_em                     | TIMESTAMP     |

## Observações

* `nome` único; `ordem` define a sequência fixa de exibição em qualquer
  lista/seletor.
* `valor_diaria_net_padrao`/`valor_diaria_sistema_padrao` são apenas
  referência — pré-preenchem a diária ao adicionar o tipo num grupo, igual
  ao padrão já usado em `percentual_comissao_padrao` de agências/guias
  (RN-G005). O valor gravado por grupo é sempre o editado na própria linha
  de `grupos_apartamentos`.
* Soft delete. Um tipo desativado continua resolvível por nome na
  reconstituição de composição ao aprovar um orçamento (RN-G007) — ver
  `grupos_orcamentos_apartamentos` abaixo.

---

# Tabela: grupos (Fase 2, revisado nas Fases 7.2 e 8.1)

Grupo de hospedagem sob regime de tarifa net/sistema (ver RN-G001 a
RN-G034 em docs/GRUPOS.md).

| Campo                         | Tipo          |
| ------------------------------ | ------------- |
| id                              | UUID          |
| codigo                          | VARCHAR(30)   |
| nome                            | VARCHAR(200)  |
| responsavel                     | VARCHAR(200)  |
| telefone                        | VARCHAR(30)   |
| email                           | VARCHAR(150)  |
| agencia_id                      | UUID          |
| guia_id                         | UUID          |
| data_entrada                    | DATE          |
| data_saida                      | DATE          |
| qtd_hospedes                    | INTEGER       |
| qtd_apartamentos                | INTEGER       |
| qtd_apartamentos_cortesia       | INTEGER       |
| qtd_apartamentos_prevista       | INTEGER       |
| valor_total_net                 | NUMERIC(10,2) |
| valor_total_net_manual          | BOOLEAN       |
| valor_total_sistema             | NUMERIC(10,2) |
| valor_total_sistema_manual      | BOOLEAN       |
| status                          | VARCHAR(30)   |
| observacao                      | TEXT          |
| prazo_deadline                  | DATE          |
| prazo_roomlist                  | DATE          |
| usuario_id                      | UUID          |
| criado_em                       | TIMESTAMP     |
| atualizado_em                   | TIMESTAMP     |

## Observações

* `codigo` é único, gerado automaticamente no formato `GRP-YYYYMMDD-XXXX`
  (não é digitado pelo usuário).
* `agencia_id` e `guia_id` são opcionais e independentes — RN-G004: no
  máximo uma agência e no máximo um guia por grupo, mas um grupo pode não
  ter nenhum (direto) ou ter os dois simultaneamente. Podem ser criados
  sem sair da tela de grupo, via modal (RN-G030 — Fase 8.3).
* **Fase 7.2 — RN-G020 (substituiu RN-G002, revogada):** não existe mais
  diária única do grupo. `qtd_apartamentos`, `valor_total_net` e
  `valor_total_sistema` são **agregados calculados** a partir da
  composição por tipo em `grupos_apartamentos` — ver tabela abaixo. As
  flags `_manual` continuam existindo, mas agora atuam sobre o agregado
  (RN-G003: alterar linhas ou datas nunca sobrescreve um total manual).
  `noites` é derivado de `data_saida - data_entrada` e não é uma coluna.
* `qtd_apartamentos_cortesia` entra na ocupação (`apartamentos_ocupados`,
  calculado) mas nunca nos cálculos de valor (RN-G015) — continua campo
  único do grupo, não quebrado por tipo.
* `qtd_apartamentos_prevista` (Fase 8.1, RN-G028): opcional, preenchido só
  na criação, puramente informativo — quando a composição real ultrapassa
  esse número, a aba Dados Gerais mostra um alerta não-bloqueante. Nunca é
  usado em cálculo; `qtd_apartamentos` (real, agregado) é sempre a fonte
  de verdade.
* Comissão retida e percentual efetivo são sempre calculados
  (`valor_total_sistema - valor_total_net`), nunca digitados (RN-G001,
  parte que não mudou com a revogação).
* **Fase 8.1 — RN-G027 (revoga RN-G001):** `valor_pago` (property) soma
  `grupos_pagamentos`; `saldo` = `valor_total_sistema - valor_pago` — a
  base financeira do módulo passou a ser o valor **sistema**, não mais o
  net. Net virou referência de composição/comissão com a agência, exibido
  em segundo plano nas telas (cabeçalho, listagem, Pagamentos, Dados
  Gerais) — nunca removido, só deixou de ser a base de "quanto o hotel
  recebe".
* `prazo_deadline`/`prazo_roomlist` (Fase 7.2, RN-G021): datas opcionais,
  sem valor padrão, puramente informativas — não entram na verificação de
  divergência do orçamento (RN-G012). Fase 8.2 (RN-G029): quando a 7 dias
  ou menos do vencimento (ou já vencidos), disparam alertas não-
  bloqueantes em Dados Gerais — roomlist só se ainda houver linha vazia;
  deadline só se o saldo (RN-G027) for maior que zero.
* Nunca excluído fisicamente.

## Status Permitidos

`PROSPECCAO`, `ORCAMENTO_ENVIADO`, `EM_NEGOCIACAO`, `CONFIRMADO`,
`HOSPEDADO`, `FINALIZADO`, `CANCELADO`, `PERDIDO`.

Transição para `CANCELADO` restrita a ADMIN e GERENCIA (RN-G010).

---

# Tabela: grupos_apartamentos (Fase 7.2)

RN-G020: fonte de verdade da composição de tarifa do grupo — uma linha por
tipo de apartamento usado.

| Campo                  | Tipo          |
| ------------------------ | ------------- |
| id                        | UUID          |
| grupo_id                  | UUID          |
| tipo_apartamento_id       | UUID          |
| quantidade                | INTEGER       |
| valor_diaria_net          | NUMERIC(10,2) |
| valor_diaria_sistema      | NUMERIC(10,2) |
| criado_em                 | TIMESTAMP     |
| atualizado_em             | TIMESTAMP     |

## Observações

* `(grupo_id, tipo_apartamento_id)` é único — um tipo só pode aparecer uma
  vez por grupo; adicionar o mesmo tipo de novo é rejeitado, o usuário
  edita a linha existente.
* **Não guarda valor_total por linha.** Assim como `Grupo.noites`, o
  subtotal (`quantidade × diária × noites`) é calculado em tempo real
  (`GrupoApartamento.subtotal_net(noites)`/`subtotal_sistema(noites)`),
  nunca persistido, para nunca dessincronizar do grupo.
* Toda alteração (criar/editar/remover linha) resincroniza os agregados do
  grupo (`qtd_apartamentos`, `valor_total_net`, `valor_total_sistema`),
  respeitando as flags `_manual` (RN-G003) — implementado em
  `GrupoService._recalcular_agregados`.
* Editada em linha na própria aba Dados Gerais (sem tela separada).

---

# Tabela: grupos_historico (Fase 3)

Log de alterações do módulo de Grupos (RN-G009). Uma linha por campo
alterado, gravada sempre na camada de service da entidade afetada — nunca
por event listener do SQLAlchemy, que não tem acesso ao usuário da sessão.

| Campo            | Tipo         |
| ----------------- | ------------ |
| id                 | UUID         |
| grupo_id           | UUID         |
| usuario_id         | UUID         |
| entidade           | VARCHAR(30)  |
| entidade_id        | UUID         |
| acao               | VARCHAR(30)  |
| campo              | VARCHAR(100) |
| valor_anterior     | TEXT         |
| valor_novo         | TEXT         |
| criado_em          | TIMESTAMP    |

## Observações

* `grupo_id` sempre aponta para o grupo dono do evento (agrupador da aba
  Atividade); `entidade_id` identifica o registro específico dentro dessa
  entidade (para `entidade = GRUPO` os dois coincidem; para futuras
  entidades como ORCAMENTO/PAGAMENTO, `entidade_id` será o id do
  orçamento/pagamento).
* `entidade`: apenas as entidades listadas em GRUPOS.md — `GRUPO`,
  `ORCAMENTO`, `PAGAMENTO`, `ROOMLIST`, `ANEXO`, `COMENTARIO`. Os
  cadastros de apoio Agências, Guias e Tipos de Apartamento **não** são
  rastreados aqui — soft delete já é suficiente para eles. Alterações na
  composição por tipo (`grupos_apartamentos`, Fase 7.2) também não geram
  linhas próprias — o efeito delas nos agregados (`qtd_apartamentos`,
  `valor_total_net`, `valor_total_sistema`) é registrado como `EDICAO` da
  entidade `GRUPO`.
* `acao`: `CRIACAO`, `EDICAO`, `EXCLUSAO`, `STATUS`.
* Em `EDICAO`, os valores são gravados já formatados para exibição (datas
  `dd/mm/aaaa`, dinheiro `R$ x,xx`, booleanos `Sim`/`Não`, agência/guia
  pelo nome) — não os valores brutos da coluna — para que a futura aba
  Atividade (Fase 6) não precise reformatar nada.
* Gerado pelo helper genérico `GrupoHistoricoService.registrar_diff`, que
  recebe dois dicts (antes/depois) já formatados e grava uma linha por
  chave cujo valor mudou.
* Nunca editado nem excluído.

---

---

# Tabela: grupos_orcamentos (Fase 4, revisado na Fase 7.3)

Versionamento imutável de orçamentos de um grupo (RN-G006). Cada linha é
uma versão numerada e congelada — nenhuma alteração no grupo depois de
gerada modifica uma versão já salva.

| Campo                       | Tipo          |
| ----------------------------- | ------------- |
| id                             | UUID          |
| grupo_id                       | UUID          |
| versao                         | INTEGER       |
| qtd_hospedes                   | INTEGER       |
| qtd_apartamentos                | INTEGER       |
| qtd_apartamentos_cortesia       | INTEGER       |
| noites                          | INTEGER       |
| valor_total_net                 | NUMERIC(10,2) |
| valor_total_sistema              | NUMERIC(10,2) |
| valor_pago_snapshot              | NUMERIC(10,2) |
| saldo_snapshot                   | NUMERIC(10,2) |
| motivo                          | VARCHAR(200)  |
| validade                        | DATE          |
| condicoes                       | TEXT          |
| status                          | VARCHAR(30)   |
| desatualizado                   | BOOLEAN       |
| data_entrada_snapshot            | DATE          |
| data_saida_snapshot              | DATE          |
| status_snapshot                  | VARCHAR(30)   |
| prazo_deadline_snapshot          | DATE          |
| prazo_roomlist_snapshot          | DATE          |
| usuario_id                      | UUID          |
| criado_em                       | TIMESTAMP     |
| atualizado_em                   | TIMESTAMP     |

## Observações

* `(grupo_id, versao)` é único; `versao` é sequencial por grupo, calculada
  como `última versão + 1` (1 se ainda não houver nenhuma).
* **Fase 7.3 — RN-G013 (reescrita):** o snapshot congela tudo que pode
  mudar depois — não só os totais agregados, mas também datas, status e
  prazos do grupo (colunas `*_snapshot` acima), a composição completa por
  tipo (`grupos_orcamentos_apartamentos`) e os pagamentos itemizados
  (`grupos_orcamentos_pagamentos`). As colunas legadas `valor_diaria_net`/
  `valor_diaria_sistema` (de quando o grupo tinha diária única) foram
  removidas nesta migration — não fazem mais sentido com a composição por
  tipo (RN-G020).
* Nada do snapshot é recalculado ao reimprimir — o PDF de uma versão
  antiga lê exclusivamente das tabelas de snapshot dessa versão.
* Apenas `status` e `desatualizado` são mutáveis após a criação — são
  metadados de fluxo, não fazem parte do snapshot negociado.
* `status`: `RASCUNHO`, `ENVIADO`, `APROVADO`, `RECUSADO`. Uma vez
  `APROVADO` ou `RECUSADO`, a versão é considerada finalizada e não aceita
  nova transição de status.
* `desatualizado`: marcado automaticamente pelo sistema quando o grupo
  diverge da última versão gerada (RN-G012) — comparação sobre
  quantidades, totais e valor pago (não sobre prazos, RN-G021, nem sobre
  status). Nunca é o sistema que gera uma nova versão sozinho.
* Aprovar uma versão (RN-G007, reescrito na Fase 7.3) copia `qtd_hospedes`,
  `qtd_apartamentos_cortesia` e os totais para o grupo, marcando
  `valor_total_net_manual`/`valor_total_sistema_manual` como `true` — e
  **substitui inteiramente** `grupos_apartamentos` do grupo pelas linhas
  congeladas em `grupos_orcamentos_apartamentos` desta versão (não só
  copia os totais). Cada `tipo_apartamento_nome` do snapshot é resolvido
  de volta a um `tipos_apartamento.id` por nome (mesmo se o tipo estiver
  desativado); se algum nome não existir mais no cadastro, a aprovação
  inteira é recusada antes de qualquer alteração — tudo ou nada.
* Nunca excluída fisicamente.

---

# Tabela: grupos_orcamentos_apartamentos (Fase 7.3)

RN-G013: uma linha congelada por tipo de apartamento usado na versão.

| Campo                   | Tipo          |
| -------------------------- | ------------- |
| id                          | UUID          |
| orcamento_id                | UUID          |
| tipo_apartamento_nome       | VARCHAR(50)   |
| quantidade                  | INTEGER       |
| valor_diaria_net            | NUMERIC(10,2) |
| valor_diaria_sistema        | NUMERIC(10,2) |
| valor_total_net             | NUMERIC(10,2) |
| valor_total_sistema         | NUMERIC(10,2) |

## Observações

* `tipo_apartamento_nome` é **texto, não FK** — deliberado: se o cadastro
  for renomeado ou desativado depois, este documento continua mostrando o
  nome de quando foi gerado.
* Diferente de `grupos_apartamentos` (subtotal calculado em tempo real),
  aqui `valor_total_net`/`valor_total_sistema` **são persistidos** — é
  documento congelado, não dado vivo.
* Populada inteira em `OrcamentoService.gerar_nova_versao`, uma linha por
  linha de `grupos_apartamentos` do grupo naquele momento.

---

# Tabela: grupos_orcamentos_pagamentos (Fase 7.3)

RN-G013: um pagamento congelado por linha, existente até o momento da
geração da versão.

| Campo            | Tipo          |
| ------------------- | ------------- |
| id                   | UUID          |
| orcamento_id         | UUID          |
| valor                | NUMERIC(10,2) |
| data_pagamento       | DATE          |
| forma_pagamento      | VARCHAR(50)   |

## Observações

* Independe de `grupos_pagamentos` continuar mudando depois — pagamentos
  futuros ao grupo não retroagem a versões já geradas.
* Populada em `OrcamentoService.gerar_nova_versao`, uma linha por
  pagamento existente do grupo naquele momento.

---

---

# Tabela: grupos_pagamentos (Fase 5)

Histórico de recebimentos de um grupo, sempre sobre o valor net (RN-G001).

| Campo            | Tipo          |
| ----------------- | ------------- |
| id                 | UUID          |
| grupo_id           | UUID          |
| valor              | NUMERIC(10,2) |
| data_pagamento     | DATE          |
| forma_pagamento    | VARCHAR(50)   |
| observacao         | TEXT          |
| usuario_id         | UUID          |
| criado_em          | TIMESTAMP     |

## Observações

* `valor` pode ser negativo apenas para lançamentos de ajuste/correção
  (RN-G008) — não deve ser zero.
* `forma_pagamento` é opcional; quando informado usa os mesmos valores de
  `vendas.pagamentos` (`DINHEIRO`, `PIX`, `CARTAO_DEBITO`,
  `CARTAO_CREDITO`).
* `Grupo.valor_pago` (property) = soma de todos os pagamentos do grupo,
  com cast explícito para `float` antes de somar (Decimal do Postgres +
  float do Python não se misturam). **Fase 8.1 — RN-G027 (revoga
  RN-G001):** `Grupo.saldo` = `valor_total_sistema - valor_pago` (era
  `valor_total_net`).
* Nunca excluído fisicamente — correção é sempre um novo lançamento com
  valor negativo, nunca um DELETE nem edição do registro original.
* RN-G017: todo pagamento registrado dispara a verificação de divergência
  do orçamento (RN-G012), mesmo sem qualquer mudança estrutural no grupo —
  `valor_pago_snapshot`/`saldo_snapshot` da última versão deixam de
  refletir a realidade a partir do primeiro pagamento seguinte à geração.

---

---

# Tabela: grupos_roomlist (Fase 6, revisado nas Fases 7.4 e 8.4)

Lista de apartamentos e hóspedes do grupo.

| Campo              | Tipo         |
| -------------------- | ------------ |
| id                    | UUID         |
| grupo_id              | UUID         |
| apartamento           | VARCHAR(30)  |
| hospede_nome          | VARCHAR(200) |
| documento             | VARCHAR(50)  |
| tipo_apartamento_id   | UUID         |
| cortesia              | BOOLEAN      |
| check_in              | DATE         |
| check_out             | DATE         |
| observacao            | TEXT         |
| criado_em             | TIMESTAMP    |
| atualizado_em         | TIMESTAMP    |

## Observações

* **Fase 8.4 — RN-G032:** `hospede_nome` passou a ser opcional (nullable).
  Linhas com `hospede_nome` nulo são "linhas vazias" — placeholders
  gerados automaticamente pela composição do grupo (`grupos_apartamentos`),
  não hóspedes reais ainda cadastrados. A roomlist deixa de ser criada só
  manualmente: alterar a quantidade de um tipo na composição sincroniza o
  número de linhas aqui —
  aumentar cria linhas vazias extras; diminuir remove apenas linhas ainda
  vazias, e é **rejeitado** (sem nenhuma alteração) se a redução exigir
  apagar uma linha que já tem `hospede_nome` preenchido — nunca apaga
  hóspede real automaticamente. A mesma proteção vale para remover um tipo
  inteiro da composição.
* **Fase 7.4 — RN-G023:** `tipo_apartamento_id` substitui a antiga coluna
  de texto livre `tipo_apartamento` — passa a referenciar o cadastro
  `tipos_apartamento` (RN-G019), o mesmo dropdown usado na composição de
  tarifa do grupo, para manter os nomes consistentes entre roomlist e
  cobrança. Opcional.
* `cortesia` (RN-G015): entra na contagem de ocupação do grupo, mas nunca
  em cálculo de valor — é só um marcador informativo por linha, não
  interfere em `qtd_apartamentos`/`qtd_apartamentos_cortesia` do grupo
  (que vêm da composição em `grupos_apartamentos`).
* Não é um registro financeiro — pode ser removido fisicamente (a
  restrição de exclusão física do GRUPOS.md se aplica a grupos,
  orçamentos e pagamentos, não à roomlist) — exceto pela proteção
  descrita acima quando a remoção vem do lado da composição (RN-G032).
* Edição em linha na própria listagem (sem tela de edição separada).
* **Fase 8.5 — RN-G033:** exportável em PDF e Excel (.xlsx), agrupada por
  tipo de apartamento na ordem de `tipos_apartamento.ordem`. Linha vazia
  (`hospede_nome` nulo) aparece como "A definir".

---

# Tabela: grupos_anexos (Fase 6)

Segue o mesmo padrão de `comprovantes` (vendas), com soft delete próprio.

| Campo            | Tipo          |
| ----------------- | ------------- |
| id                 | UUID          |
| grupo_id           | UUID          |
| orcamento_id       | UUID          |
| pagamento_id       | UUID          |
| tipo               | VARCHAR(30)   |
| nome_original      | VARCHAR(255)  |
| nome_arquivo       | VARCHAR(255)  |
| caminho            | VARCHAR(500)  |
| tipo_arquivo       | VARCHAR(50)   |
| tamanho_bytes      | BIGINT        |
| usuario_id         | UUID          |
| enviado_em         | TIMESTAMP     |
| removido_em        | TIMESTAMP     |

## Observações

* `tipo`: `COMPROVANTE_PAGAMENTO`, `ORCAMENTO_ASSINADO`, `ROOMLIST` (Fase
  7.4, RN-G024 — mesmo registro exibido nas abas Roomlist e Anexos, sem
  duplicar linha), `OUTRO` (default).
* `orcamento_id`/`pagamento_id` existem no schema para vincular um anexo a
  uma versão de orçamento ou pagamento específico, mas a tela atual não
  expõe essa vinculação — ficam `NULL` até uma fase futura que precise
  disso.
* Validação de upload idêntica a `comprovantes`: extensão (PDF/JPG/JPEG/
  PNG), MIME type e tamanho máximo (10 MB), nome interno gerado por UUID
  (SECURITY.md).
* Diferente de `comprovantes` (hard delete): usa **soft delete**
  (`removido_em`), já previsto no schema. O arquivo físico é mantido em
  disco mesmo após a remoção lógica — os anexos do grupo (comprovantes de
  pagamento, orçamentos assinados) seguem o mesmo espírito de retenção de
  trilha financeira/auditoria dos demais registros do módulo.
* Armazenados em `uploads/grupos/{ano}/{mês}/`, fora da pasta pública,
  sem acesso direto por URL (download só pela rota autenticada).

---

# Tabela: grupos_comentarios (Fase 6)

Comentários de usuários sobre o grupo, exibidos na aba Atividade.

| Campo       | Tipo      |
| ------------- | --------- |
| id            | UUID      |
| grupo_id      | UUID      |
| usuario_id    | UUID      |
| texto         | TEXT      |
| criado_em     | TIMESTAMP |

## Observações

* Apenas criação — sem edição nem exclusão de comentários na UI.
* A criação de um comentário também grava uma linha em `grupos_historico`
  (`entidade=COMENTARIO`, `acao=CRIACAO`) para satisfazer RN-G009, mas a
  aba Atividade não duplica essa linha genérica — ela é suprimida da
  timeline porque o próprio comentário (com o texto completo) já
  representa esse evento.
