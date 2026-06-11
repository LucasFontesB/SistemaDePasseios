# UI_GUIDE.md

# Objetivo

Definir o padrão visual do sistema para garantir consistência entre todas as telas.

---

# Princípios de Design

O sistema deverá priorizar:

* Clareza
* Rapidez
* Simplicidade
* Legibilidade

Evitar:

* Animações excessivas
* Efeitos visuais desnecessários
* Excesso de informações na mesma tela

---

# Identidade Visual

## Conceito

Sistema de gestão de passeios turísticos.

Inspirado em:

* Mar
* Turismo
* Organização
* Confiabilidade

---

# Paleta de Cores

## Cor Primária

Azul Oceano

#0D6EFD

Utilização:

* Botões principais
* Links
* Menu ativo

---

## Cor Secundária

Turquesa

#20C997

Utilização:

* Indicadores positivos
* Destaques

---

## Sucesso

#198754

---

## Atenção

#FFC107

---

## Erro

#DC3545

---

## Fundo

#F8F9FA

---

## Texto Principal

#212529

---

## Texto Secundário

#6C757D

---

# Tipografia

## Fonte Principal

Inter

Fallback:

sans-serif

---

## Tamanhos

Título Principal

32px

---

Título de Página

24px

---

Subtítulo

18px

---

Texto Padrão

14px

---

Texto Pequeno

12px

---

# Layout

## Estrutura

Header
↓
Sidebar
↓
Conteúdo

---

# Header

Altura:

64px

Exibir:

* Nome do sistema
* Usuário logado
* Botão sair

---

# Sidebar

Largura:

260px

Itens:

Dashboard

Vendas
├── Listagem
└── Nova Venda

Cadastros
├── Passeios
├── Tipos
└── Embarcações

Relatórios
├── Vendas
└── Comissões

Administração
└── Usuários

---

# Dashboard

## Cards

Exibir:

* Vendas Hoje
* Receita Hoje
* Receita do Mês
* Comissão do Mês

---

## Próximos Embarques

Tabela simples.

Colunas:

* Horário
* Contratante
* Passeio
* Pessoas

---

# Tabelas

Utilizar:

Bootstrap Table

---

## Cabeçalho

Fixo durante rolagem.

---

## Ordenação

Permitida em todas as colunas principais.

---

## Paginação

20 registros por página.

---

## Pesquisa

Campo de busca sempre visível.

---

# Formulários

## Organização

Campos agrupados por seção.

---

### Contratante

Nome

Telefone

---

### Passageiros

Adultos

Crianças

---

### Passeio

Passeio

Tipo

Embarcação

---

### Financeiro

Valor Total

Comissão

---

### Saída

Data

Horário

---

### Observações

Campo de texto livre.

---

# Botões

## Primário

Salvar

Cor:

Azul Oceano

---

## Secundário

Voltar

Cor:

Cinza

---

## Perigo

Excluir

Cancelar

Cor:

Vermelho

---

# Status

## PENDENTE

Cinza

---

## AGUARDANDO_PAGAMENTO

Amarelo

---

## CONFIRMADO

Azul

---

## EMBARCADO

Turquesa

---

## FINALIZADO

Verde

---

## CANCELADO

Vermelho

---

## REEMBOLSADO

Laranja

---

# Alertas

Sucesso

Operação realizada com sucesso.

---

Erro

Não foi possível concluir a operação.

---

Aviso

Verifique os dados informados.

---

# Modais

Utilizar para:

* Cancelamento de venda
* Desativação de cadastro
* Confirmações críticas

---

# Responsividade

## Desktop

Prioridade máxima.

---

## Notebook

Suporte obrigatório.

---

## Tablet

Suporte recomendado.

---

## Mobile

Fora do escopo da V1.

---

# Acessibilidade

Todos os campos devem possuir:

* Label
* Placeholder
* Mensagem de erro

---

# Componentes Reutilizáveis

Criar componentes para:

* Sidebar
* Header
* Breadcrumb
* Alertas
* Cards
* Tabelas
* Modais
* Paginação

Objetivo:

Evitar duplicação de código HTML.
