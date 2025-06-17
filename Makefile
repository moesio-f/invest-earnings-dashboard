# Variáveis
COMPOSE ?= ./docker-compose.dev.yaml

# Recipe padrão
all: down build up 


down:
	@docker compose -f ${COMPOSE} down --remove-orphans

build:
	@docker compose -f ${COMPOSE} build

up:
	@docker compose -f ${COMPOSE} up -d --remove-orphans

logs:
	@docker compose -f ${COMPOSE} logs -f

bash:
	@docker compose -f ${COMPOSE} exec app bash

