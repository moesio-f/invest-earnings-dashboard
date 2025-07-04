<h1 align="center">
  <div style="display: flex; justify-content: space-between;">
  <a><img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="streamlit logo" style="height: 80px;"></a>
  <a><img src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/community/logos/python-logo-only.png" alt="Python logo" style="height: 80px;"></a>
  <a><img src="https://pandas.pydata.org/static/img/pandas.svg" alt="pandas logo" style="height: 80px;"></a>
  </div>
  Dashboard para Análise de Proventos
  <br>
</h1>


![](.github/dashboard_home.png)

Dashboard simples para análise de proventos oriundos de investimentos financeiros com `streamlit`, `SQLAlchemy`, `alembic`, `pandas` e `RabbitMQ`. Esse é um projeto protótipo com o intuito de explorar diferentes tecnologias e arquiteturas para sistemas de análises de dados.

Uma descrição geral da arquitetura se encontra em [`docs`](docs/architecture.md). O repositório é organizado da seguinte forma:

- [`common`](./common): biblioteca utilitária com definições padrões compartilhadas pelos diferentes componentes do sistema;
- [`wallet-api`](./wallet-api): API RESTFul para gerenciamento de uma carteira de investimentos e dados econômicos;
- [`market-scrapers`](./market-scrapers): scrapers de dados do mercado;
- [`event-engine`](./event-engine): motor de eventos, reage a diferentes notificações emitidas pelo sistema e gera análises;
- [`dashboard`](./dashboard): interface gráfica para o dashboard e gerenciamento de carteira;

## Quickstart

Para acessar o dashboard localmente, basta executar o comando `make` ou executar o docker-compose presente na raiz do diretório (i.e., `docker compose up`). O dashboard é disponibilizado localmente na porta `8082`.

Para configurações dos diferentes componentes, checar seus respectivos diretórios.

### Adicionando Ativos, Proventos e Dados Econômicos

![](.github/dashboard_settings.png)

O dashboard possui uma seção simplificada de cadastro de ativos e proventos, incluindo adição a partir de arquivos CSV. Todavia, o dashboard e a API ainda não oferecem suporte nativo para remoção/deleção de items, sendo necessário se comunicar diretamente com o banco de dados.

## Arquitetura

O diagrama abaixo contém uma visão geral da arquitetura do sistema, que consiste em uma arquitetura híbrida baseada em eventos. Para mais informações, checar a [documentação](./docs/architecture.md).

```mermaid
---
title: Visão Geral da Arquitetura
---
flowchart TD
    subgraph "Banco(s) de Dados"
        wallet_db[("<p>Schema</p>wallet")]
        analytic_db[("<p>Schema</p>analytic")]
        logging_db@{shape: lin-cyl, label: "Logging"}
    end
    wallet_api[Gerenciador de Carteira]
    market_scraper[Scrapper de dados do Mercado]

    subgraph Interface Gráfica
        dashboard[Dashboard]
        settings_ui[Configurações da Carteira]
    end

    subgraph Motor de Eventos
        router_channel@{shape: das, label: "Canal de Roteamento"}
        processor_channel@{shape: das, label: "Canal de Processamento"}
        router[Router]
        processor@{shape: procs, label: "Analytic Processor"}

        router_channel -->|Mensagem| router
        router -->|Seleção de Fila| processor_channel
        processor_channel --> processor
    end

    settings_ui -->|Consome| wallet_api
    wallet_api ---|Leitura & Escrita| wallet_db
    market_scraper ---|Leitura & Escrita| wallet_db
    wallet_api -->|Notificação| router_channel
    market_scraper -->|Notificação| router_channel
    dashboard -->|Notificação| router_channel
    dashboard ---|Leitura| analytic_db
    processor ---|Leitura de Contexto| wallet_db
    processor ---|Logs| logging_db
    processor ---|Leitura de Estado| analytic_db
    processor ---|Escrita de Estado| analytic_db
```
