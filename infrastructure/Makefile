# Infrastructure Makefile

SHELL := /bin/bash

# Compose configuration
PROJECT_NAME_DEV := financial-data-extractor-dev

COMPOSE_FILE_DEV := docker/docker-compose.dev.yml

DC_DEV := docker compose -p $(PROJECT_NAME_DEV) -f $(COMPOSE_FILE_DEV)

.PHONY: help up down restart ps logs logs-postgres logs-redis stop destroy reset psql redis-cli pgadmin url health \
        up-dev down-dev restart-dev ps-dev logs-dev logs-postgres-dev logs-redis-dev stop-dev destroy-dev reset-dev

help:
	@echo "Infrastructure commands (DEV uses $(COMPOSE_FILE_DEV); PROD uses $(COMPOSE_FILE_PROD)):"
	@echo "  DEV:"
	@echo "    make up-dev         - Start dev services in background"
	@echo "    make down-dev       - Stop and remove dev services (keep volumes)"
	@echo "    make destroy-dev    - Stop and remove dev services + volumes"
	@echo "    make reset-dev      - Destroy then start fresh (dev)"
	@echo "    make ps-dev         - Show dev service status"
	@echo "    make logs-dev       - Tail all dev logs"
	@echo "    make logs-postgres-dev / logs-redis-dev"
	@echo "    make restart-dev    - Restart dev services"
	@echo "    make psql           - Open psql shell to dev Postgres"
	@echo "    make redis-cli      - Open redis-cli to dev Redis"
	@echo "    make pgadmin        - Open pgAdmin (dev only)"
	@echo "    make url            - Print dev service URLs"
	@echo "    make health         - Check dev container health"
	@echo ""
	@echo "Shortcuts (DEV defaults): up, down, destroy, reset, restart, ps, logs, logs-postgres, logs-redis, url, health"

# Shortcuts defaulting to DEV stack
up: up-dev
down: down-dev
stop: stop-dev
destroy: destroy-dev
reset: reset-dev
restart: restart-dev
ps: ps-dev
logs: logs-dev
logs-postgres: logs-postgres-dev
logs-redis: logs-redis-dev
url: url-dev
health: health-dev

# DEV targets
up-dev:
	$(DC_DEV) up -d
	@$(MAKE) --no-print-directory url-dev

down-dev:
	$(DC_DEV) down

stop-dev:
	$(DC_DEV) stop

destroy-dev:
	$(DC_DEV) down -v --remove-orphans

reset-dev: destroy-dev up-dev

restart-dev:
	$(DC_DEV) restart

ps-dev:
	$(DC_DEV) ps

logs-dev:
	$(DC_DEV) logs -f --tail=200

logs-postgres-dev:
	$(DC_DEV) logs -f --tail=200 postgres

logs-redis-dev:
	$(DC_DEV) logs -f --tail=200 redis

# Tools (DEV stack)
psql:
	@$(DC_DEV) exec -e PGPASSWORD=postgres postgres psql -h localhost -U postgres -d financial_data_extractor || \
	  (echo "Postgres not ready or container missing. Try: make up-dev" && exit 1)

redis-cli:
	@$(DC_DEV) exec redis redis-cli -u redis://localhost:6379 || \
	  (echo "Redis not ready or container missing. Try: make up-dev" && exit 1)

pgadmin:
	@open http://localhost:5050 || xdg-open http://localhost:5050 || true

url-dev:
	@echo "[DEV] Postgres:        postgres://postgres:postgres@localhost:5432/financial_data_extractor"
	@echo "[DEV] pgAdmin:         http://localhost:5050 (admin@local.dev / adminadmin)"
	@echo "[DEV] Redis:           redis://localhost:6379"
	@echo "[DEV] Redis Commander: http://localhost:8081"

health-dev:
	@echo "Checking DEV container health..."
	@$(DC_DEV) ps
