# Variáveis
COMPOSE := ./docker-compose.dev.yaml

# Recipe padrão
all: down build up 


down:
	@docker compose -f ${COMPOSE} down

build:
	@docker compose -f ${COMPOSE} build

up:
	@docker compose -f ${COMPOSE} up -d

logs:
	@docker compose -f ${COMPOSE} logs -f

