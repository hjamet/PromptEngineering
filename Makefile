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
	@echo "  make        : Démarre l'application et le tunnel Cloudflare"
	@echo "  make debug  : Démarre l'application en mode debug"
	@echo "  make stop   : Arrête tous les processus"
	@echo "  make clean  : Nettoie les fichiers temporaires et les caches"