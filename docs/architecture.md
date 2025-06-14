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

Essa escolha se baseia no fato que o sistema como um todo responde a algum tipo de evento. Por exemplo, ao se cadastrar um novo _provento_ para um dado _ativo_, é necessário a execução de múltiplas análises para essa entrada (e.g., YoC, equivalências, etc). A presença de um ou mais mediadores é importante para garantir a _consistência_ dos resultados e identificar erros/falhas.

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

### Mediators

Para garantir a funcionalidade do sistema, são necessários alguns mediadores distintos.

- `GetMediator`: mediador para atividades simples como recuperação de informações;
    - Esse mediador escuta o canal de eventos iniciadores;
    - Esse mediador é responsável pela leitura a algum banco de dados da aplicação;
    - Deve responder no canal apropriado de resposta e no de broadcast;
    - Caso o mediador não seja capaz de responder, deve enviar o mesmo evento para o canal do próximo mediador;
- `CreateUpdateMediator`: mediador para atividades de criação ou atualização de dados;
    - Esse mediador escuta o canal de eventos de criação e atualização;
    - Esse mediador é responsável pelo gerenciamento de um workflow relacionado com a criação ou atualização de entidades;
    - Deve responder no canal apropriado de resposta e no de broadcast;
    - Caso esse mediador não seja capaz de responder, deve indicar na resposta o motivo;

### Processors

Os "processadores" representam atividades que podem ser realizadas em resposta a um determinado evento. 

Todos processadores escutam ao canal de broadcast e possuem canais próprios para comunicação point-to-point. A resposta do processador deve ser enviada ao canal de: (i) resposta, se point-to-point; ou (ii) broadcast, se a mensagem original veio do broadcast.

- `DataWriter`: responsável pela escrita de algum dado no banco;
    - Responsável por escrita, atualização e deleção;
    - Mensagens devem possuir informação sobre o banco, tabela e afins;
    - 
- `AlayticProcessor`: classe de processadores de análise de dados

Devem existir 2 serviços principais e uma interface gráfica. Em particular, tais componentes devem ser responsáveis pelo seguinte:

- Serviço de Gerenciamento de Carteira: permite o cadastro e atualizações nos dados da carteira (e.g., proventos, transações, ativos);
    - Deve apenas realizar transações ACID;
    - Responsável pelo schema/banco `wallet`;
- Serviço de Processamento de Dados: realiza análises suportadas pelo sistema;
    - Deve ser organizado utilizando uma arquitetura Event-Driven;
    - Coordenação deve ser evitada, todavia deve-se utilizar uma topologia `Mediator`;
    - Escrita no Banco deve ser realizada por processadores específico (e.g., `DataWriter`);
        - Tais processadores são responsáveis por escolher como e quando as análises realizadas pelo sistema serão persistidas no banco da aplicação;
        - Deve ser _stateful_ (i.e., deve conhecer o estado atual do banco, bem como dados que precisam ser escritas);
    - Processadores de análise devem ser _stateless_ e operar sobre os dados recebidos como entrada;
        - Devem produzir novos eventos indicando a finalização da análise (bem como o resultado);
    - Responsável pelo schema/banco `analytics`;
- Interface Gráfica: composto pelo dashboard e UI para gerenciamento da carteira;
    - Emite eventos para o serviço de processamento;
    - Consome funcionalidades do serviço de gerenciamento de carteira;
    - Criar dashboards das análises presentes em `analytics` (read-only);
    - Deve ser organizado como um monolito modular;
        - Limitar reuso entre páginas da interface;
        - O máximo a ser compartilhado são utilidades agnósticas ao domínio;



