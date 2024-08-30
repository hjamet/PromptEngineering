# Variables
PYTHON = poetry run python
APP = app.py
CLOUDFLARED = cloudflared
TUNNEL_NAME = prompt-engineering
CONFIG_TEMPLATE = ./config_template.yml
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
	@echo "Configuration du tunnel Cloudflare..."
	@if [ -f $(CONFIG_FILE) ]; then \
		TUNNEL_ID=$$(grep -oP '(?<=tunnel: ).*' $(CONFIG_FILE)); \
	else \
		TUNNEL_ID=$$($(CLOUDFLARED) tunnel create $(TUNNEL_NAME) | grep -oP '(?<=Created tunnel ).*(?= with id)'); \
	fi
	@if [ ! -f /home/$(USER)/.cloudflared/$$TUNNEL_ID.json ]; then \
		echo "Création du fichier de credentials pour le tunnel..."; \
		$(CLOUDFLARED) tunnel token $$TUNNEL_ID > /home/$(USER)/.cloudflared/$$TUNNEL_ID.json; \
	else \
		echo "Le fichier de credentials existe déjà."; \
	fi
	@sed 's|<USER>|$(USER)|g; s|345d8b1b-1174-4384-b569-16b39c812671|'$$TUNNEL_ID'|g' $(CONFIG_TEMPLATE) > $(CONFIG_FILE)
	@echo "Configuration DNS..."
	@$(CLOUDFLARED) tunnel route dns $$TUNNEL_ID $(TUNNEL_NAME).henri-jamet.com
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

# Démarrer le tunnel Cloudflare avec le fichier de configuration
.PHONY: run-tunnel
run-tunnel:
	@echo "Démarrage du tunnel Cloudflare..."
	$(CLOUDFLARED) tunnel --config $(CONFIG_FILE) run $(TUNNEL_NAME)

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