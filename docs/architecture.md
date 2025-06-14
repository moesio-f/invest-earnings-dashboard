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

## _Quantas_ Arquiteturais

Quanta único. As necessidades de diferentes partes do sistema são similares.

### Características Arquiteturais

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

Dado as características do sistemas, a Arquitetura Event-Driven com topologia Mediator foi selecionada. Para funcionalidades que requerem uma resposta, será utilizado a estratégia _request-reply_.

Essa escolha se baseia no fato que o sistema como um todo responde a algum tipo de evento. Por exemplo, ao se cadastrar um novo _provento_ para um dado _ativo_, é necessário a execução de múltiplas análises para essa entrada (e.g., YoC, equivalências, etc). A presença de um ou mais mediadores é importante para garantir a _consistência_ dos resultados e identificar erros/falhas. Um detalhe importante, no futuro pode ser vantajoso utilizar uma arquitetura Space-Based para reduzir a dependência de um banco síncrono.

## Decisões Arquiteturais

```mermaid
---
title: Visão Geral da Arquitetura
---
flowchart TD
wallet[(Wallet)]
analytics[(Analytics)]

subgraph Interface Gráfica
    dashboard[Dashboard]
    config[Gerenciamento de Carteira]
end
subgraph Processamento de Dados
    writer_channel@{shape: das, label: "Writer Channel"}
    processor_channel@{shape: das, label: "Processor Channel"}
    dispatcher[Event Dispatcher] -->|Evento de Processamento| processor_channel
    processor_channel -->|Evento de Processamento| processor@{shape: procs, label: "Data Processors"}
    processor -->|Broadcast de Resultado| processor_channel
    processor -->|Broadcast de Resultado| writer_channel
    writer_channel -->|Evento para Persistência| writer@{shape: procs, label: "Data Writers"}
end
config ---|Requisação| api[Serviço de Gerenciamento de Carteira]
dashboard ---|Leitura| analytics
dispatcher ---|Leitura| wallet
dispatcher ---|Leitura| analytics
writer ---|Escrita| analytics
api ---|Escrita & Leitura| wallet
```

### Canais

> Canais representam meios de comunicação entre mediadores e processadores.

- `Mediators`: canais para eventos que devem ser iniciados por mediadores;
    - `simple_mediator`: canal padrão que deve ser utilizado p
- `Processors`: canal de broadcast para todos processadores;
- `P2P`: canais P2P disponibilizados por cada processador;
- `Multicast`: canais de Pub/Sub gerenciados por mediadores, processadores podem escolher escutar tais canais;      

### Mediators

> Os "mediadores" servem para coordenar processadores de forma a garantir consistência dos dados e/ou operações.

- `SimpleMediator`: mediador para atividades simples que necessitam _request-reply_;
    - Esse mediador escuta o `Mediator` e `Broadcast`;
    - 
- ``:

### Processors

> Os "processadores" representam atividades que podem ser realizadas em resposta a um determinado evento.

Todos processadores escutam o canal de broadcast e possuem canais próprios para comunicação point-to-point/multicast. A resposta do processador deve ser enviada ao canal de resposta (se point-to-point/multicast) ou de broadcast.

- `DataWriter`: processador que realiza escritas, atualizações e deleções em algum banco do sistema;
- `ContextCreator`: processador que cria o _contexto_ de alguma operação realizada em algum banco;
    - Responsável por obter todos os dados associados com uma dada operação no banco;
- `AnalyticProcessor`: definição genérica de processadores de dados analíticos;
    -  Responsável por realização de análises sobre eventos que geram contextos de análise;
    -  



