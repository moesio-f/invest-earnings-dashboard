# API de Gerenciamento de Carteiras

Esse diretório contém a API de gerenciamento de carteiras. A API implementada utilizando `fastapi` e `sqlalchemy`. Para execução local, pode-se utilizar o comando `DB_URL=<connection string> fastapi dev app/api.py` ou executar o serviço diretamente do `docker-compose` definido na raiz do projeto.

## Organização

O código fonte é disponibilizado em [`app`](./app), seguindo uma organização simples com versionamento da API.

## Variáveis de Ambiente

| Variável | Descrição |
| --- | --- |
| `DB_URL` | String de conexão com o banco de dados. O banco deve ter sido inicializado previamente utilizando as [`migrations`](../common/migrations). |
