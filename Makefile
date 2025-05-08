# Variáveis
COMPOSE := ./docker-compose.dev.yaml

# Recipe padrão
all: down build up 


down:
	@docker compose down

build:
	@docker compose build

up:
	@docker compose up -d

logs:
	@docker compose logs -f

