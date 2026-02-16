# Makefile para o Corretor de Redação AI

.PHONY: help build run run-with-key stop clean logs rebuild dev

# Variáveis
IMAGE_NAME = corretor-redacao
CONTAINER_NAME = corretor-redacao-container
PORT = 8501

help: ## Exibe ajuda
	@echo "Comandos disponíveis:"
	@echo "  make build         - Constrói a imagem Docker"
	@echo "  make run           - Inicia o container (sem API Key)"
	@echo "  make run-with-key  - Inicia o container pedindo API Key"
	@echo "  make stop          - Para o container"
	@echo "  make logs          - Mostra logs do container"
	@echo "  make clean         - Remove imagem e container"
	@echo "  make rebuild       - Reconstrói a imagem (build + clean)"
	@echo "  make dev           - Constrói e roda com API Key (para desenvolvimento)"

build: ## Constrói a imagem Docker
	docker build -t $(IMAGE_NAME) .

run: ## Inicia o container (sem API Key)
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):8501 $(IMAGE_NAME)

run-with-key: ## Inicia o container pedindo API Key
	@read -p "Digite sua GEMINI_API_KEY: " api_key; \
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):8501 -e GEMINI_API_KEY=$$api_key $(IMAGE_NAME); \
	echo "✅ Container iniciado! Acesse: http://localhost:$(PORT)"

run-interactive: ## Inicia o container em modo interativo
	docker run -it --name $(CONTAINER_NAME) -p $(PORT):8501 $(IMAGE_NAME)

stop: ## Para o container
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

logs: ## Mostra logs do container
	docker logs -f $(CONTAINER_NAME)

clean: ## Remove imagem e container
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true

rebuild: clean build ## Reconstrói a imagem

dev: build run-with-key ## Constrói e roda com API Key (para desenvolvimento)
