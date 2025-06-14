# Arquitetura da Aplicação

Esse documento contém a arquitetura utilizada pela aplicação.

## Descrição & Requisitos

> A aplicação é um dashboard que permite a análise de proventos recebidos por investimentos em ativos financeiros negociados na B3. Permitindo ao investidor analisar os retornos de cada ativo ou classe de ativo.

- **Usuários**: 1 por deploy;
- **Requisitos**:
    - _Cadastro_
        - Permitir o cadastro de diferentes ativos;
        - Permitir o cadastro de transações envolvendo os ativos;
        - Permitir o cadastro de proventos distribuídos por ativos;
        - Permitir o cadastro de índices econômicos a nível mensal;
    - _Visualização_
        - Cálculo de métricas relacionadas com YoC (Yield on Cost);
        - Cálculo de rendimentos _versus_ índices econômicos (e.g., CDI, IPCA);
        - Quantidade total de proventos recebidos e a receber;
        - Análise por classe de ativo (e.g., Ação, ETF, FII, BDR);
- **Contexto Adicional**:
    - É possível que a aplicação possua dados relativos à um grande período de tempo;
    - A visualização deve ser atualizada sempre que os dados atualizarem;
    - Deve ser possível expandir as visualizações existentes na aplicação;
    - Deve ser possível expandir o escopo da aplicação no futuro (e.g., preço atual dos ativos na bolsa, scrapping de dados);

## Características Arquiteturais

> Essa lista é um mapeamento das características arquiteturais mais importantes do sistema.

- _Availability_: a UI deve estar disponível 24/7 mostrando as análises mais recentes realizadas pelo sistema e permitindo atualizações na carteira;
- _Extensibility_: o sistema precisa ser extensível para novas visualizações e análises;
- _Performance_: o sistema precisa ser capaz de processar um grande conjunto de dados;

## Componentes

Das características, é possível visualizar uma estrutura com os seguintes componentes:

- Componentes de configurações da carteira;
  - Cadastro, remoção, atualização;
- Componentes de análise;
  - Responsável por realizar uma análise; 
- Interface gráfica para acesso às funcionalidades;

## Estilo Arquitetural

Dado as características do sistemas, uma arquitetura híbrida Event-Driven com topologia Mediator foi selecionadaa. Em particular, existe um componente síncrono para o gerenciamento de carteiras e um outro componente assíncrono para geração e recuperação de análises.

Essa escolha se baseia no fato que o sistema como um todo responde a algum tipo de evento. Por exemplo, ao se cadastrar um novo _provento_ para um dado _ativo_, é necessário a execução de múltiplas análises para essa entrada (e.g., YoC, equivalências, etc). A presença de um ou mais mediadores é importante para garantir a _consistência_ dos resultados e identificar erros/falhas. Um detalhe importante, no futuro pode ser vantajoso utilizar uma arquitetura Space-based para reduzir a dependência de um banco síncrono.

## Decisões Arquiteturais

O diagrama abaixo contém uma visão geral das decisões tomadas. Em especial, cabe destacar:

- Tanto o dashboard quanto o módulo de gerenciamento de carteira lêem diretamente dos bancos;
    - No caso do dashboard, primeiro realizasse a leitura e depois uma requisição ao mediador que deve retornar se análise já está disponível ou indicar o ETA;
        - Em qualquer caso, o dashboard deve exibir os dados mais recentes disponíveis no banco até ter a análise definitiva;
        - Essa decisão permite grande responsividade;
    - Um grande _tradeoff_ dessa escolha é um maior acomplamento (i.e., modificações nos schemas se propagam por todo sistema) e _bottleneck_ nas chamadas síncronas de contexto e estado;
        - Ambos pontos podem ser mitigados com o uso de uma arquitetura Space-based ao custo de um aumento de complexidade;
- A organização dos canais entre mediadores e processadores é livre para escolha durante implementação (e.g., broadcast, multicast, p2p, etc);
    - O único requisito é que o mediador possa identificar quando um dado processador finalizou seu trabalho (i.e., messagem de finalização);
    - Devem existir múltiplos canais que agrupem processadores por domínios;
    - Um processador só pode realizar broadcast no seu canal de domínio;

```mermaid
---
title: Visão Geral da Arquitetura
---
flowchart TD
    subgraph Banco de Dados
        wallet_db[("<p>Schema</p>wallet")]
        analytic_db[("<p>Schema</p>analytic")]
    end
    wallet_api[Gerenciador de Carteira]

    subgraph Interface Gráfica
        dashboard[Dashboard]
        settings_ui[Configurações da Carteira]
    end

    subgraph Motor de Análises
        mediator_channel@{shape: das, label: "Fila do Mediador"}
        analytic_channel@{shape: das, label: "Fila de Análise"}
        mediator@{shape: procs, label: "Mediador"}
        processor@{shape: procs, label: "Analytic Processor"}

        mediator_channel -->|Mensagem| mediator
        mediator <-->|Etapa de Análise| analytic_channel
        analytic_channel --> processor
    end

    settings_ui -->|Consome| wallet_api
    wallet_api -->|Leitura & Escrita| wallet_db
    wallet_api -->|Notificação de atualização| mediator_channel
    dashboard <-->|Requisição & ETA| mediator_channel
    dashboard -->|Leitura| analytic_db
    processor -->|Leitura de Contexto| wallet_db
    processor -->|Leitura de Estado| analytic_db
    processor -->|Escrita de Estado| analytic_db
```
