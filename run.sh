#!/bin/bash
#
# Este script inicia a aplicação Streamlit, configurando o PYTHONPATH
# para que o Python encontre os módulos dentro da pasta 'src'.

echo "🚀 Iniciando o Corretor de Redação AI..."

# Ativa o ambiente virtual e executa o Streamlit
source venv/bin/activate && PYTHONPATH=./src streamlit run src/app/main.py
