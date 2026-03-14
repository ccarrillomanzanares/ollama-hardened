# Makefile for Ollama Hardened

# Docker Compose binary detection
DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

.PHONY: start stop restart logs reload clean status health backup update duckdns

start:
	@echo "🚀 Starting Ollama Hardened..."
	@python3 install.py

stop:
	@echo "🛑 Stopping services..."
	@$(DOCKER_COMPOSE) stop

restart:
	@echo "🔄 Restarting services..."
	@$(DOCKER_COMPOSE) restart

logs:
	@$(DOCKER_COMPOSE) logs -f

reload:
	@echo "♻️ Reloading configuration..."
	@python3 install.py

status:
	@$(DOCKER_COMPOSE) ps

health:
	@echo "🏥 Services health status:"
	@$(DOCKER_COMPOSE) ps --format "table {{.Name}}\t{{.Status}}"

backup:
	@python3 backup.py

update:
	@python3 update.py

duckdns:
	@bash install-duckdns.sh

clean:
	@echo "⚠️ WARNING: This will delete the .env, certificates, and dynamic configuration files."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(DOCKER_COMPOSE) down -v
	@rm -f .env docker-compose.override.yml Caddyfile.ext
	@echo "✅ Cleanup completed."
