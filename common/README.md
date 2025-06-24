# Utilidades

Esse diretório contém a base mínima que deve ser compartilhada entre os diferentes serviços do sistema.

## Organização

- [`invest_earning`](invest_earning): _namespace_ package da aplicação;
    - [`database`](invest_earning/database): modelos e entidades dos bancos de dados;
    - [`logging`](invest_earning/logging): facilidades para criação de logs;
- [`migrations`](migrations): scripts de migrações dos diferentes bancos de dados;
    - Utiliza `alembic` para controle de schemas dos diferentes bancos da aplicação;
- [`scripts`](scripts): scripts com facilidades para diferentes serviços (i.e., configuração de cron jobs, etc);
- [`tools`](tools): scripts para facilidades;

