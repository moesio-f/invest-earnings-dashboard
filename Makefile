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
	@docker compose -f ${COMPOSE} logs -f ${SERVICE}

sh:
	@docker compose -f ${COMPOSE} exec ${SERVICE} sh

ps:
	@docker compose -f ${COMPOSE} ps

stats:
	@docker compose -f ${COMPOSE} stats

ips:
	@docker network inspect -f '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' invest-earnings-network
