# REQUIREMENTS.md

## Requisitos Funcionais

### RF001 - Autenticação

O sistema deve permitir login de usuários.

### RF002 - Cadastro de Venda

O sistema deve permitir registrar uma venda de passeio.

Campos:

* Número da venda
* Nome do contratante
* Quantidade de adultos
* Quantidade de crianças
* Passeio
* Tipo do passeio
* Embarcação
* Valor total
* Data de saída
* Horário
* Observações

### RF003 - Comissão

O sistema deve calcular automaticamente a comissão baseada em percentual configurável.

### RF004 - Upload de Comprovantes

O sistema deve permitir anexar comprovantes de pagamento.

Formatos aceitos:

* PDF
* JPG
* JPEG
* PNG

### RF005 - Consulta de Vendas

O sistema deve permitir pesquisar vendas por:

* Contratante
* Data
* Passeio
* Status

### RF006 - Dashboard

O sistema deve exibir:

* Vendas do dia
* Vendas do mês
* Total de passageiros
* Total de comissões

### RF007 - Relatórios

O sistema deve gerar relatórios por:

* Período
* Passeio
* Recepcionista
* Comissão

## Requisitos Não Funcionais

### RNF001

O sistema deve ser acessível via navegador.

### RNF002

O sistema deve funcionar na rede interna do hotel.

### RNF003

O sistema deve utilizar PostgreSQL como banco de dados.

### RNF004

O sistema deve armazenar comprovantes no servidor.

### RNF005

O sistema deve permitir backups do banco e dos arquivos anexados.
