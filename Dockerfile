FROM python:3.11-slim

# Instala dependências do sistema necessárias para compilação
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    pkg-config \
    libhdf5-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Atualiza pip e instala wheel para evitar problemas de compilação
RUN pip install --upgrade pip setuptools wheel

# Instala dependências com configurações otimizadas para evitar segfault
ENV PIP_NO_CACHE_DIR=1
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX"
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Baixa e cacheia modelo para não precisar no runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('Qwen/Qwen3-Embedding-0.6B').save('/app/model')"

# Copia o código da aplicação
COPY . .

EXPOSE 8080

# Substitua main.py pela sua API (se for FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
