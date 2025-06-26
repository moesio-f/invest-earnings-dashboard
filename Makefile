all: down build up 

down:
	@docker compose down --remove-orphans

build:
	@docker compose build

up:
	@docker compose up -d --remove-orphans

logs:
	@docker compose logs -f ${SERVICE}

sh:
	@docker compose exec ${SERVICE} sh

ps:
	@docker compose ps

stats:
	@docker compose stats

ips:
	@docker network inspect -f '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' invest-earnings-network

create-backup:
	@docker compose run --rm migrations sh common/scripts/dump_backup.sh

load-backup:
	@docker compose run --rm migrations sh common/scripts/load_backup.sh

run-scrapper:
	@docker compose run --env PREVIOUS_DAYS=1825 --rm scrappers python -m scrappers.market_price
