# Scrapper de Dados de Mercado

Esse diretório contém scripts para extração de dados de mercado. É responsabilidade do usuário programar a execução dos diferentes scripts (e.g., `cronjobs`).

## Organização

O código fonte é disponibilizado em [`scrapper`](./scrappers).

## Variáveis de Ambiente

A tabela abaixa representa as configurações gerais necessárias por todos os scrappers.

| Variável | Descrição |
| --- | --- |
| `DB_URL` | String de conexão com o banco de dados da carteira. |
| `BROKER_URL` | String de conexão com o broker. |
| `NOTIFICATION_QUEUE` | Fila que deve ser utilizada para o envio de notificações. |

### Configurações Específicas

| Variável | Scrapper | Descrição |
| --- | --- | --- |
| `PREVIOUS_DAYS` | [`market_price`](./scrappers/market_price.py) | Quantidade de dias anteriores ao atual para tentar extrair (default=30). |
