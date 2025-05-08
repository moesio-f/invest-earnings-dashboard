all: down build up 


down:
	@docker compose down

build:
	@docker compose build

up:
	@docker compose up -d

logs:
	@docker compose logs -f

