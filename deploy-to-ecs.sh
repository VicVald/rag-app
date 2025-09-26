#!/bin/bash

# Script para fazer deploy da aplicação RAG no AWS ECS
# Substitua estas variáveis pelos seus valores
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="YOUR_ACCOUNT_ID"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
APP_NAME="rag-app"

echo "=== Deploy RAG App to ECS ==="
echo "AWS Region: $AWS_REGION"
echo "Account ID: $AWS_ACCOUNT_ID"
echo ""

# 1. Login no ECR
echo "1. Fazendo login no ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# 2. Criar repositórios ECR se não existirem
echo "2. Criando repositórios ECR..."
aws ecr create-repository --repository-name ${APP_NAME}-api --region $AWS_REGION 2>/dev/null || echo "Repositório ${APP_NAME}-api já existe"

# 3. Build e tag das imagens
echo "3. Fazendo build e tag das imagens..."
docker build -t ${APP_NAME}-api .
docker tag ${APP_NAME}-api:latest ${ECR_REGISTRY}/${APP_NAME}-api:latest

# 4. Push das imagens para ECR
echo "4. Fazendo push das imagens para ECR..."
docker push ${ECR_REGISTRY}/${APP_NAME}-api:latest

echo ""
echo "=== Push completo! ==="
echo "Imagem da API: ${ECR_REGISTRY}/${APP_NAME}-api:latest"
echo ""
echo "Próximos passos:"
echo "1. Criar RDS PostgreSQL"
echo "2. Criar Task Definition ECS"
echo "3. Criar ECS Service"
echo "4. Configurar Load Balancer"