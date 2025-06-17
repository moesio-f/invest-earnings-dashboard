# Motor de Eventos

Esse diretório contém o código para o motor de eventos. O código é organizado em formato de biblioteca, permitindo que diversos componentes sejam inicializados separadamente apesar de compartilhar o mesmo namespace.

## Organização

- [`engine`](./engine): raiz da biblioteca;
    - [`processors`](./engine/processors): definição de diferentes processadores;
    - [`router`](./engine/router): definição de roteadores;
    - [`utils`](./engine/utils): códigos utilitários, demais sub-pacotes só podem compartilhar códigos presentes aqui;

### [`Router`](./engine/router/router.py)

Essa é classe do roteador responsável por analisar as mensagens colocados na fila de notificações e definir para qual canal essa notificação deve ser enviada, bem como realizar conversões na estrutura das mensagens se necessário.

Para utilizar o roteador, é necessário a configuração das seguintes variáveis de ambiente:

| Variável | Descrição |
| --- | --- |
| `NOTIFICATION_QUEUE` | Fila que deve ser utilizada para o recebimento das notifações. |
| `YOC_QUEUE` | Fila que deve ser utilizada para análises de YoC. |
| `BROKER_URL` | URL para conexão com o broker. Deve conter autenticação. |


### [`YoCProcessor`](./engine/processors/yoc.py)

Essa é a classe que realiza análises relacionadas com o Yield on Cost (YoC) de investimentos. Para utilizá-la, deve-se configurar as seguintes variáveis de ambiente:

| Variável | Descrição |
| --- | --- |
| `YOC_QUEUE` | Fila com atividades necessárias da cálculo de YoC. |

Esse processador é _stateless_, sempre que recebe uma solicitação faz a leitura do estado atual do banco e determina se algum trabalho deve ser realizado ou não.


#### Estrutura das Mensagens

Esse processador espera que as mensagens passadas são um JSON com o seguinte schema:

```json
{
  "trigger": "wallet_update|dashboard_query",
  "update_information": {
    "entity": "asset|earning|transaction|economic_data",
    "operation": "CREATE|UPDATE|DELETE",
    "target": "<b3_code>|<economic_index>"
  },
  "query_information": {
    "kind": "ASSET|GROUP",
    "entity": "<b3_code>|<asset_kind_str>|all",
    "table": "earning_yield|monthly_yield",
  }
}
```


- `trigger`: origem da necessidade de execução de análises, pode ser oriundo de atualizações na carteira ou queries do dashboard;
- `update_information`: se a notificação é oriunda de atualizações da carteira, esse campo deve ser um dicionário não-vazio;
    - `entity`: qual entidade sofreu alteração;
    - `operation`: qual tipo da operação;
    - `target`: target da operação (código B3 do ativo subjacente ou índice econômico);
- `query_information`: se a notificação for de uma query no dashboard, esse campo deve ser um dicionário não-vazio;
    - `kind`: indica qual tipo de análise buscada;
    - `entity`: indica qual a entidade associada a análise (i.e., código B3, nome do grupo, etc);
    - `table`: indica qual tabela foi acessada;

