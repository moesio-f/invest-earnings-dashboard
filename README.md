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

Dashboard simples para análise de proventos oriundos de investimentos financeiros com `streamlit`, `SQLAlchemy`, `alembic` e `pandas`. Esse é um projeto protótipo cujo objetivo foi desenvolver um dashboard para análise de dados, juntamente com o uso de tecnologias para gerenciamento de banco de dados relacionais.

## Quickstart

Para acessar o dashboard localmente, basta executar o comando `make` ou executar o docker-compose presente na raiz do diretório (i.e., `docker compose -f docker-compose.yaml up`). O dashboard é disponibilizado localmente na porta `8082`.

### Variáveis de Ambiente

É possível configurar algumas funcionalidades do sistema através das seguintes variáveis de ambiente:

| Variável | Descrição | Valor Padrão |
| --- | --- | --- |
| `DB_BACKEND` | Define o sistema banco de dados a ser utilizado. Atualmente, apenas o `sqlite` é suportado. | `sqlite`
| `DB_BACKUP_PATH` | Caminho onde backups periódicos devem ser armazenados. | |
| `DB_BOOTSTRAP_DATA_PATH` | Caminho onde dados de bootstrap devem ser lidos (atualmente, apenas dados econômicos são inicializados automaticamente). | |
| `CONNECTION_STRING` | String de conexão para o banco de dados. | `sqlite:////local.db` |

### Adicionando Ativos, Proventos e Dados Ecônomicos

![](.github/dashboard_settings.png)

O dashboard possui uma seção simplificada de cadastro de ativos e proventos, incluindo adição a partir de arquivos CSV. Todavia, o dashboard e a API ainda não oferecem suporte nativo para remoção/deleção de items, sendo necessário se comunicar diretamente com o banco de dados.


# Roadmap

- Refatoração do código e adição de testes unitários;
- Adição de novas funcionalidades na API pare removação/deleção de objetos;
- Criação de API com flask que disponibiliza os resultados de forma agnóstica ao sistema (i.e., Python);
- Novas visualizações e seções no dashboard;
