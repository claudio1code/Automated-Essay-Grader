#!/bin/bash
#
# Este script inicia a aplicação Streamlit e abre o navegador automaticamente.

URL="http://localhost:8501"

echo "🚀 Iniciando o Corretor de Redação AI..."
echo "O servidor estará disponível em: $URL"

# Ativa o ambiente virtual e executa o Streamlit em segundo plano
source venv/bin/activate && PYTHONPATH=./src streamlit run src/app/main.py &

# Aguarda 3 segundos para dar tempo ao servidor de iniciar
echo "Aguardando o servidor iniciar..."
sleep 3

# Abre a URL no navegador padrão (funciona na maioria dos ambientes Linux com GUI)
echo "Abrindo o navegador..."
xdg-open $URL

# Opcional: Traz o processo do servidor de volta para o primeiro plano
# para que você possa pará-lo com Ctrl+C no terminal.
wait