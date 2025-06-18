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

bash:
	@docker compose -f ${COMPOSE} exec app ${SERVICE}

ps:
	@docker compose ps

stats:
	@docker compose stats

ips:
	@docker network inspect -f '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' invest-earnings_default
