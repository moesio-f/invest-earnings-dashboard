<h1 align="center">
  <div style="display: flex; justify-content: space-between;">
  <a><img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="streamlit logo" height="80"></a>
  <a><img src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png" alt="Python logo" height="80"></a>
  <a><img src="https://pandas.pydata.org/static/img/pandas.svg" alt="pandas logo" height="80"></a>
  </div>
  Dashboard para Análise de Proventos
  <br>
</h1>


![](.github/dashboard_home.png)

Dashboard simples para análise de proventos oriundos de investimentos financeiros com `streamlit`, `SQLAlchemy`, `alembic`, `pandas` e `RabbitMQ`. Esse é um projeto protótipo com o intuito de explorar diferentes tecnologias e arquiteturas para sistemas de análises de dados.

Uma descrição geral da arquitetura se encontra em [`docs`](docs/architecture.md). O repositório é organizado da seguinte forma:

- [`common`](./common): biblioteca utilitária com definições padrões compartilhadas pelos diferentes componentes do sistema;
- [`wallet-api`](./wallet-api): API RESTFul para gerenciamento de uma carteira de investimentos e dados econômicos;
- [`event-engine`](./event-engine): motor de eventos, reage a diferentes notificações emitidas pelo sistema e gera análises;

## Quickstart

Para acessar o dashboard localmente, basta executar o comando `make` ou executar o docker-compose presente na raiz do diretório (i.e., `docker compose up`). O dashboard é disponibilizado localmente na porta `8082`.

Para configurações dos diferentes componentes, checar seus respectivos diretórios.

### Adicionando Ativos, Proventos e Dados Ecônomicos

![](.github/dashboard_settings.png)

O dashboard possui uma seção simplificada de cadastro de ativos e proventos, incluindo adição a partir de arquivos CSV. Todavia, o dashboard e a API ainda não oferecem suporte nativo para remoção/deleção de items, sendo necessário se comunicar diretamente com o banco de dados.


