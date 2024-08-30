# Variables
PYTHON = poetry run python
APP = app.py
CLOUDFLARED = cloudflared
TUNNEL_NAME = prompt-engineering
CONFIG_FILE = ./config.yml

# Obtenir le nom d'utilisateur actuel
USER := $(shell whoami)

# Commande par défaut
.PHONY: all
all: run

# Installation complète du projet
.PHONY: install
install:
	@echo "Installation du projet..."
	@if ! command -v poetry &> /dev/null; then \
		echo "Installation de Poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	poetry install
	@if ! command -v $(CLOUDFLARED) &> /dev/null; then \
		echo "Installation de Cloudflared..."; \
		wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb; \
		sudo dpkg -i cloudflared-linux-amd64.deb; \
		rm cloudflared-linux-amd64.deb; \
	fi
	@if [ ! -f ~/.cloudflared/cert.pem ]; then \
		echo "Authentification Cloudflare..."; \
		$(CLOUDFLARED) tunnel login; \
	fi
	@if [ ! -f $(CONFIG_FILE) ]; then \
		echo "Création du tunnel Cloudflare..."; \
		TUNNEL_ID=$$($(CLOUDFLARED) tunnel create $(TUNNEL_NAME) | grep -oP '(?<=Created tunnel ).*(?= with id)'); \
		echo "url: http://localhost:8050" > $(CONFIG_FILE); \
		echo "tunnel: $$TUNNEL_ID" >> $(CONFIG_FILE); \
		echo "credentials-file: /home/$(USER)/.cloudflared/$$TUNNEL_ID.json" >> $(CONFIG_FILE); \
		echo "ingress:" >> $(CONFIG_FILE); \
		echo "  - hostname: $(TUNNEL_NAME).henri-jamet.com" >> $(CONFIG_FILE); \
		echo "    service: http://localhost:8050" >> $(CONFIG_FILE); \
		echo "  - service: http_status:404" >> $(CONFIG_FILE); \
		echo "Configuration DNS..."; \
		$(CLOUDFLARED) tunnel route dns $(TUNNEL_NAME) $(TUNNEL_NAME).henri-jamet.com; \
	fi
	@echo "Installation terminée. Utilisez 'make run' pour démarrer l'application."

# Démarrer l'application et le tunnel Cloudflare
.PHONY: run
run:
	@echo "Démarrage de l'application Dash et du tunnel Cloudflare..."
	@$(MAKE) -j2 run-app run-tunnel

# Démarrer l'application Dash (mode production)
.PHONY: run-app
run-app:
	@echo "Démarrage de l'application Dash..."
	$(PYTHON) $(APP)

# Démarrer le tunnel Cloudflare avec le fichier de configuration temporaire
.PHONY: run-tunnel
run-tunnel:
	@echo "Démarrage du tunnel Cloudflare..."
	sed 's|<USER>|$(USER)|g' $(CONFIG_FILE) > config_temp.yml
	$(CLOUDFLARED) tunnel --config config_temp.yml run $(TUNNEL_NAME)
	rm config_temp.yml

# Démarrer l'application en mode debug
.PHONY: debug
debug:
	@echo "Démarrage de l'application Dash en mode debug..."
	$(PYTHON) $(APP) --debug

# Arrêter tous les processus (utile pour le développement)
.PHONY: stop
stop:
	@echo "Arrêt de tous les processus..."
	@pkill -f "python $(APP)" || true
	@pkill -f "$(CLOUDFLARED) tunnel run" || true

# Nettoyer les fichiers temporaires et les caches
.PHONY: clean
clean:
	@echo "Nettoyage des fichiers temporaires et des caches..."
	rm -rf __pycache__ .cache cache-directory
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# Aide
.PHONY: help
help:
	@echo "Commandes disponibles:"
	@echo "  make install : Installe le projet et configure Cloudflare"
	@echo "  make         : Démarre l'application et le tunnel Cloudflare"
	@echo "  make debug   : Démarre l'application en mode debug"
	@echo "  make stop    : Arrête tous les processus"
	@echo "  make clean   : Nettoie les fichiers temporaires et les caches"