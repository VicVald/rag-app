#!/bin/bash

# Script para fazer push das imagens Docker para o Docker Hub
# Substitua estas variáveis pelos seus valores
DOCKER_USERNAME="vhusertest"
APP_NAME="rag-app"
VERSION="latest"

echo "=== Deploy RAG App to Docker Hub ==="
echo "Docker Username: $DOCKER_USERNAME"
echo "App Name: $APP_NAME"
echo ""

# 1. Verificar se está logado
echo "1. Verificando login no Docker Hub..."
sudo docker info | grep Username || echo "⚠️  Você precisa fazer login: sudo docker login"

# 2. Build da imagem (se necessário)
echo "2. Fazendo build da imagem..."
sudo docker build -t ${APP_NAME}-api .

# 3. Tag das imagens para Docker Hub
echo "3. Fazendo tag das imagens..."
sudo docker tag ${APP_NAME}-api:latest ${DOCKER_USERNAME}/${APP_NAME}-api:${VERSION}
sudo docker tag ${APP_NAME}-api:latest ${DOCKER_USERNAME}/${APP_NAME}-api:latest

# Para PostgreSQL, vamos usar a imagem oficial
sudo docker pull postgres:15
sudo docker tag postgres:15 ${DOCKER_USERNAME}/${APP_NAME}-postgres:15
sudo docker tag postgres:15 ${DOCKER_USERNAME}/${APP_NAME}-postgres:latest

# 4. Push das imagens para Docker Hub
echo "4. Fazendo push das imagens para Docker Hub..."
sudo docker push ${DOCKER_USERNAME}/${APP_NAME}-api:${VERSION}
sudo docker push ${DOCKER_USERNAME}/${APP_NAME}-api:latest
sudo docker push ${DOCKER_USERNAME}/${APP_NAME}-postgres:15
sudo docker push ${DOCKER_USERNAME}/${APP_NAME}-postgres:latest

echo ""
echo "=== Push completo! ==="
echo "Imagem da API: ${DOCKER_USERNAME}/${APP_NAME}-api:latest"
echo "Imagem PostgreSQL: ${DOCKER_USERNAME}/${APP_NAME}-postgres:latest"
echo ""
echo "Para usar as imagens:"
echo "docker pull ${DOCKER_USERNAME}/${APP_NAME}-api:latest"
echo "docker pull ${DOCKER_USERNAME}/${APP_NAME}-postgres:latest"
echo ""
echo "URLs públicas:"
echo "https://hub.docker.com/r/${DOCKER_USERNAME}/${APP_NAME}-api"
echo "https://hub.docker.com/r/${DOCKER_USERNAME}/${APP_NAME}-postgres"