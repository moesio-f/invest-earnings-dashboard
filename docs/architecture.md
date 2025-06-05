# Arquitetura da Aplicação

Esse documento contém a arquitetura utilizada pela aplicação.

## Descrição & Requisitos

> A aplicação é um dashboard que permite a análise de proventos recebidos por investimentos em ativos financeiros negociados na B3. Permitindo ao investidor analisar os retornos de cada ativo ou classe de ativo.

- **Usuários**: 1;
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

## _Quantas_ Arquiteturais

Pela descrição do problema, parece existir um único _quanta_.

### Características Arquiteturais

> Essa lista é um mapeamento das características arquiteturais mais importantes do sistema.

- _Performance_: o sistema precisa ser capaz de processar um conjunto de dados que cresce ao longo do tempo;
- _Extensibility_: o sistema precisa ser extensível para novas visualizações e análises serem implementados com facilidade;


## Componentes

Vide os requisitos da aplicação, temos os seguintes fluxos bem definidos:
- _Fluxo de cadastro_, no qual o usuário adiciona algum dado novo ao sistema (e.g., ativo, transação, provento, dado econômico);
- _Fluxo de visualização_, no qual o usuário deseja visualizar alguma das análises que pode ser realizadas pelo sistema;

Perceba que uma pré-condição para a visualização é que as análises sejam executadas. Dessa forma, o fluxo de visualização deve possuir uma etapa de execução das análises. Ademais, por conta das exigências de performance, esse processo não deve ser demorado.

## Estilo Arquitetural

Dado as características do sistema, uma arquitetura Monolítica Modular foi selecionada. Essa escolha se baseia nos seguintes fatores:
- Fluxos simples e diretamente ligados ao banco da aplicação;
- Solução mais performática possível;
    - Computação distribuída introduz latência;
    - Análises podem ser sequenciais ou utilizar dados compartilhados;
    - Usuário único não requer escalabilidade;


## Decisões Arquiteturais

### Arquiteturais

- A interface de usuário deve se comunicar com o restante do sistema através de uma _API Facade_;

### Design

- O processo de análise de dados pode criar tabelas auxiliares no Banco para melhoria de performance;

