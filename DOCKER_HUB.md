# Como fazer Push para Docker Hub

## Pré-requisitos

1. **Conta no Docker Hub** - Crie em https://hub.docker.com
2. **Docker instalado** e funcionando
3. **Aplicação funcionando localmente**

## Passo a Passo

### 1. Criar conta no Docker Hub
- Acesse https://hub.docker.com
- Crie sua conta gratuita
- Anote seu username

### 2. Configurar o script
Edite o arquivo `push-to-dockerhub.sh` e substitua:
```bash
DOCKER_USERNAME="seu-usuario-dockerhub"  # Seu username do Docker Hub
```

### 3. Executar o push
```bash
# Dar permissão de execução (se necessário)
chmod +x push-to-dockerhub.sh

# Executar o script
./push-to-dockerhub.sh
```

### 4. Verificar no Docker Hub
Após o push, suas imagens estarão disponíveis em:
- `https://hub.docker.com/r/seu-usuario/rag-app-api`
- `https://hub.docker.com/r/seu-usuario/rag-app-postgres`

## Comando Manual (alternativo)

Se preferir fazer manualmente:

```bash
# 1. Login
docker login

# 2. Build (se necessário)
docker build -t rag-app-api .

# 3. Tag
docker tag rag-app-api:latest seu-usuario/rag-app-api:latest

# 4. Push
docker push seu-usuario/rag-app-api:latest
```

## Usar as imagens públicas

Depois do push, qualquer pessoa pode usar suas imagens:

```bash
# Baixar suas imagens
docker pull seu-usuario/rag-app-api:latest
docker pull seu-usuario/rag-app-postgres:latest

# Usar o docker-compose modificado
docker compose -f docker-compose.dockerhub.yml up
```

## Atualizar imagens

Para atualizar suas imagens no Docker Hub:

```bash
# 1. Fazer mudanças no código
# 2. Rebuild da imagem
docker build -t rag-app-api .

# 3. Tag com nova versão
docker tag rag-app-api:latest seu-usuario/rag-app-api:v1.1

# 4. Push da nova versão
docker push seu-usuario/rag-app-api:v1.1
docker push seu-usuario/rag-app-api:latest  # Também atualizar latest
```

## Deploy no ECS usando Docker Hub

Se quiser usar suas imagens do Docker Hub no ECS, edite o `ecs-task-definition.json`:

```json
{
  "image": "seu-usuario/rag-app-api:latest"
}
```

## Vantagens do Docker Hub

✅ **Gratuito** para repositórios públicos  
✅ **Fácil de usar** e compartilhar  
✅ **Integração** com muitas plataformas  
✅ **Versionamento** automático  
✅ **Documentação** integrada  

## Desvantagens

❌ **Público** (qualquer um pode baixar)  
❌ **Limites** de pull para contas gratuitas  
❌ **Menos controle** que ECR privado  

## Repositórios Privados

Para repositórios privados:
- **Docker Hub Pro**: $5/mês (repositórios privados ilimitados)
- **Docker Hub Team**: $7/usuário/mês

## Segurança

⚠️ **Importante**: Não inclua:
- Senhas ou tokens no código
- Chaves de API
- Dados sensíveis

Use variáveis de ambiente ou secrets externos!