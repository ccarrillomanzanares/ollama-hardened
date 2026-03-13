# Makefile for Ollama Hardened

# Docker Compose binary detection
DOCKER_COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "/home/ccmai/.docker-compose/docker-compose"; fi)

.PHONY: start stop restart logs reload clean status health

start:
	@echo "🚀 Starting Ollama Hardened..."
	@./install.py

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
	@./install.py

status:
	@$(DOCKER_COMPOSE) ps

health:
	@echo "🏥 Services health status:"
	@$(DOCKER_COMPOSE) ps --format "table {{.Name}}\t{{.Status}}"

clean:
	@echo "⚠️ WARNING: This will delete the .env, certificates, and dynamic configuration files."
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(DOCKER_COMPOSE) down -v
	@rm -f .env docker-compose.override.yml
	@echo "✅ Cleanup completed."
