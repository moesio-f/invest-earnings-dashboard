# Dashboard & UI

Esse diretório contém o código para a interface gráfica. O código é organizado como um dashboard modular, com compartilhamento mínimo entre páginas para permitir reorganizações no futuro caso seja necessário.

## Organização

- [`app`](./app): raiz da UI;
    - [`dashboard`](./app/dashboard): dashboard para visualização de análises;
    - [`wallet`](./app/wallet): interfaces para gerenciamento e visualização da carteira;

## Variáveis de Ambiente

| Variável | Descrição |
| --- | --- |
| `BROKER_URL` | URL para conexão com o broker. |
| `NOTIFICATION_QUEUE` | Fila para notificação de eventos. |
| `WALLET_API_URL` | URL da API de gerenciamento da carteira. |
| `ANALYTIC_DB_URL` | URL para conexão com o banco de dados das análises. |
