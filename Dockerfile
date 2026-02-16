# Multi-stage build para melhor performance
FROM python:3.12-slim as builder

# Define argumentos de build
ARG DEBIAN_FRONTEND=noninteractive

# Instala dependências de build e sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copia e instala dependências Python com otimizações
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Stage final - imagem limpa e pequena
FROM python:3.12-slim

# Instala apenas runtime essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && find /usr -name "*.pyc" -delete \
    && find /usr -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

WORKDIR /app

# Copia apenas o necessário do builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY . .

# Configurações de ambiente otimizadas
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

# Comando otimizado
CMD ["streamlit", "run", "src/app/main.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--browser.gatherUsageStats=false"]
