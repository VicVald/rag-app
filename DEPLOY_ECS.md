# Deploy da Aplicação RAG no AWS ECS - Tutorial Interface Gráfica

## Pré-requisitos

1. **Conta AWS** ativa
2. **Imagens Docker** já disponíveis no Docker Hub:
   - `vhusertest/rag-app-api:latest`
   - `vhusertest/rag-app-postgres:latest`
3. **Permissões AWS** para ECS, RDS, VPC, IAM

## 🎯 Visão Geral do Deploy

Vamos criar a infraestrutura seguindo esta ordem:
1. **VPC e Networking** (subnets, security groups)
2. **RDS PostgreSQL** (banco de dados)
3. **ECS Cluster** (ambiente de containers)
4. **Task Definition** (definição dos containers)
5. **ECS Service** (executar e gerenciar containers)
6. **Load Balancer** (distribuir tráfego)

---

## 📋 Passo 1: Criar VPC e Networking

### 1.1. Acessar VPC Console
1. **Fazer login** no [AWS Console](https://console.aws.amazon.com)
2. **Buscar** por "VPC" na barra de pesquisa
3. **Clicar** em "VPC"

### 1.2. Criar VPC
1. **Clicar** em "Create VPC"
2. **Selecionar** "VPC and more"
3. **Configurar:**
   - **Name tag**: `rag-app-vpc`
   - **IPv4 CIDR**: `10.0.0.0/16`
   - **Number of Availability Zones**: `2`
   - **Number of public subnets**: `2`
   - **Number of private subnets**: `2`
   - **NAT gateways**: `In 1 AZ` (para economizar)
   - **VPC endpoints**: `None`
4. **Clicar** em "Create VPC"
5. **Aguardar** a criação (pode levar alguns minutos)

### 1.3. Criar Security Groups

#### Security Group para Load Balancer:
1. **Ir para** "Security Groups" no menu lateral
2. **Clicar** em "Create security group"
3. **Configurar:**
   - **Name**: `rag-app-alb-sg`
   - **Description**: `Security group for RAG app load balancer`
   - **VPC**: Selecionar `rag-app-vpc`
4. **Inbound rules:**
   - **Type**: HTTP, **Port**: 80, **Source**: 0.0.0.0/0
   - **Type**: HTTPS, **Port**: 443, **Source**: 0.0.0.0/0
5. **Clicar** em "Create security group"

#### Security Group para ECS:
1. **Clicar** em "Create security group"
2. **Configurar:**
   - **Name**: `rag-app-ecs-sg`
   - **Description**: `Security group for RAG app ECS tasks`
   - **VPC**: Selecionar `rag-app-vpc`
3. **Inbound rules:**
   - **Type**: Custom TCP, **Port**: 8080, **Source**: Selecionar `rag-app-alb-sg`
4. **Clicar** em "Create security group"

#### Security Group para RDS:
1. **Clicar** em "Create security group"
2. **Configurar:**
   - **Name**: `rag-app-rds-sg`
   - **Description**: `Security group for RAG app RDS`
   - **VPC**: Selecionar `rag-app-vpc`
3. **Inbound rules:**
   - **Type**: PostgreSQL, **Port**: 5432, **Source**: Selecionar `rag-app-ecs-sg`
4. **Clicar** em "Create security group"

---

## 📋 Passo 2: Criar RDS PostgreSQL

### 2.1. Acessar RDS Console
1. **Buscar** por "RDS" na barra de pesquisa
2. **Clicar** em "RDS"

### 2.2. Criar Subnet Group
1. **Clicar** em "Subnet groups" no menu lateral
2. **Clicar** em "Create DB subnet group"
3. **Configurar:**
   - **Name**: `rag-app-db-subnet-group`
   - **Description**: `Subnet group for RAG app database`
   - **VPC**: Selecionar `rag-app-vpc`
   - **Subnets**: Selecionar as **2 subnets privadas** criadas anteriormente
4. **Clicar** em "Create"

### 2.3. Criar Instância RDS
1. **Clicar** em "Databases" no menu lateral
2. **Clicar** em "Create database"
3. **Configurar:**
   - **Database creation method**: Standard create
   - **Engine type**: PostgreSQL
   - **Engine version**: 15.4 (ou mais recente)
   - **Templates**: Free tier
   - **DB instance identifier**: `rag-app-postgres`
   - **Master username**: `agno_user`
   - **Master password**: `agno_password_123`
   - **DB instance class**: db.t3.micro
   - **Storage**: 20 GB
   - **VPC**: Selecionar `rag-app-vpc`
   - **DB subnet group**: Selecionar `rag-app-db-subnet-group`
   - **VPC security groups**: Selecionar `rag-app-rds-sg`
   - **Database name**: `agno_db`
4. **Clicar** em "Create database"
5. **Aguardar** a criação (pode levar 10-15 minutos)
6. **Anotar o endpoint** da database quando estiver pronta

---

## 📋 Passo 3: Criar ECS Cluster

### 3.1. Acessar ECS Console
1. **Buscar** por "ECS" na barra de pesquisa
2. **Clicar** em "Elastic Container Service"

### 3.2. Criar Cluster
1. **Clicar** em "Clusters" no menu lateral
2. **Clicar** em "Create cluster"
3. **Configurar:**
   - **Cluster name**: `rag-app-cluster`
   - **Infrastructure**: AWS Fargate (serverless)
4. **Clicar** em "Create"

---

## 📋 Passo 4: Criar Task Definition

### 4.1. Criar IAM Roles

#### Execution Role:
1. **Buscar** por "IAM" na barra de pesquisa
2. **Ir para** "Roles" → "Create role"
3. **Trusted entity**: AWS service → ECS → ECS Task
4. **Permissions**: Anexar `AmazonECSTaskExecutionRolePolicy`
5. **Role name**: `rag-app-execution-role`
6. **Create role**

#### Task Role:
1. **Create role** novamente
2. **Trusted entity**: AWS service → ECS → ECS Task
3. **Permissions**: (nenhuma por enquanto)
4. **Role name**: `rag-app-task-role`
5. **Create role**

### 4.2. Criar Task Definition
1. **Voltar para ECS Console**
2. **Clicar** em "Task definitions" no menu lateral
3. **Clicar** em "Create new task definition"
4. **Configurar:**
   - **Task definition family**: `rag-app-task`
   - **Launch type**: AWS Fargate
   - **CPU**: 1 vCPU
   - **Memory**: 2 GB
   - **Task execution role**: `rag-app-execution-role`
   - **Task role**: `rag-app-task-role`

### 4.3. Configurar Container da API
1. **Na seção Container definitions**, clicar em "Add container"
2. **Configurar:**
   - **Container name**: `rag-api`
   - **Image URI**: `vhusertest/rag-app-api:latest`
   - **Port mappings**: 8080 (TCP)
   - **Environment variables**:
     - `POSTGRES_HOST`: [ENDPOINT_DO_RDS_CRIADO]
     - `POSTGRES_PORT`: 5432
     - `POSTGRES_USER`: agno_user
     - `POSTGRES_PASSWORD`: agno_password_123
     - `POSTGRES_DB`: agno_db
   - **Log configuration**: awslogs
     - **Log group**: `/ecs/rag-app` (será criado automaticamente)
     - **Region**: us-east-1
     - **Stream prefix**: ecs

### 4.4. Finalizar Task Definition
1. **Clicar** em "Create"
2. **Aguardar** a criação

---

## 📋 Passo 5: Criar Application Load Balancer

### 5.1. Acessar EC2 Console
1. **Buscar** por "EC2" na barra de pesquisa
2. **Clicar** em "EC2"

### 5.2. Criar Load Balancer
1. **Clicar** em "Load Balancers" no menu lateral
2. **Clicar** em "Create load balancer"
3. **Selecionar** "Application Load Balancer"
4. **Configurar:**
   - **Name**: `rag-app-alb`
   - **Scheme**: Internet-facing
   - **VPC**: Selecionar `rag-app-vpc`
   - **Subnets**: Selecionar as **2 subnets públicas**
   - **Security groups**: Selecionar `rag-app-alb-sg`

### 5.3. Criar Target Group
1. **Em "Listeners and routing"**, clicar em "Create target group"
2. **Nova aba abrirá**, configurar:
   - **Target type**: IP addresses
   - **Target group name**: `rag-app-tg`
   - **Protocol**: HTTP, **Port**: 8080
   - **VPC**: Selecionar `rag-app-vpc`
   - **Health check path**: `/docs`
3. **Clicar** em "Next" → "Create target group"
4. **Voltar** para a aba do Load Balancer
5. **Refresh** e selecionar o target group criado
6. **Clicar** em "Create load balancer"

---

## 📋 Passo 6: Criar ECS Service

### 6.1. Criar Service
1. **Voltar** para ECS Console
2. **Clicar** no cluster `rag-app-cluster`
3. **Na aba Services**, clicar em "Create"
4. **Configurar:**
   - **Launch type**: Fargate
   - **Task definition**: `rag-app-task:1`
   - **Service name**: `rag-app-service`
   - **Number of tasks**: 1

### 6.2. Configurar Networking
1. **Em "Networking":**
   - **VPC**: Selecionar `rag-app-vpc`
   - **Subnets**: Selecionar as **2 subnets públicas**
   - **Security groups**: Selecionar `rag-app-ecs-sg`
   - **Auto-assign public IP**: ENABLED

### 6.3. Configurar Load Balancer
1. **Em "Load balancing":**
   - **Load balancer type**: Application Load Balancer
   - **Load balancer**: Selecionar `rag-app-alb`
   - **Target group**: Selecionar `rag-app-tg`
   - **Container**: `rag-api:8080`
2. **Clicar** em "Create"

---

## 📋 Passo 7: Verificar Deployment

### 7.1. Aguardar Inicialização
1. **No ECS Console**, ir para o cluster `rag-app-cluster`
2. **Clicar** na aba "Tasks"
3. **Aguardar** até que o status seja "RUNNING"
4. **Se falhar**, verificar os logs no CloudWatch

### 7.2. Obter URL da Aplicação
1. **Ir para EC2 Console** → "Load Balancers"
2. **Clicar** em `rag-app-alb`
3. **Copiar** o "DNS name"
4. **Testar** no navegador: `http://SEU-DNS-DO-ALB/docs`

### 7.3. Verificar Funcionamento
1. **Acessar** a documentação da API: `/docs`
2. **Testar** endpoints básicos
3. **Verificar** se a conexão com o banco está funcionando

---

## 🔧 Troubleshooting

### ❌ Task não inicia
**Soluções:**
1. **Ir para CloudWatch** → "Log groups" → `/ecs/rag-app`
2. **Verificar logs** para erros
3. **Verificar** se o RDS endpoint está correto nas variáveis de ambiente
4. **Confirmar** que o RDS está no status "Available"

### ❌ Health check falhando
**Soluções:**
1. **Verificar** se o endpoint `/docs` responde
2. **Ir para EC2** → "Security Groups"
3. **Verificar** se `rag-app-ecs-sg` permite tráfego na porta 8080
4. **Verificar** se `rag-app-alb-sg` permite tráfego HTTP (porta 80)

### ❌ Não consegue acessar via Load Balancer
**Soluções:**
1. **Verificar** se o Target Group está "healthy"
2. **Ir para EC2** → "Target Groups" → `rag-app-tg`
3. **Na aba Targets**, verificar se o status é "healthy"
4. **Se unhealthy**, verificar security groups e health check path

### ❌ Erro de conexão com banco
**Soluções:**
1. **Verificar** se o RDS está na mesma VPC
2. **Confirmar** security group `rag-app-rds-sg` permite conexões do ECS
3. **Verificar** endpoint, usuário e senha nas variáveis de ambiente
4. **Testar** conectividade do ECS para o RDS

---

## 📊 Monitoramento

### CloudWatch Logs
- **Log Group**: `/ecs/rag-app`
- **Acessar**: CloudWatch Console → Log groups

### Métricas ECS
- **CPU e Memory utilization**
- **Task count**
- **Service events**

### Métricas RDS
- **Connections**
- **CPU utilization**
- **Storage**

---

## 💰 Custos Estimados (us-east-1)

- **ECS Fargate**: ~$15/mês (1 task, 1 vCPU, 2GB RAM)
- **RDS db.t3.micro**: ~$15/mês
- **Application Load Balancer**: ~$22/mês
- **Data Transfer**: Variável
- **CloudWatch Logs**: ~$2/mês

**Total estimado**: ~$54/mês

---

## 🔒 Configurações de Segurança

### Variáveis de Ambiente Importantes
- `POSTGRES_HOST`: [Endpoint do RDS criado]
- `POSTGRES_PORT`: 5432
- `POSTGRES_USER`: agno_user
- `POSTGRES_PASSWORD`: agno_password_123
- `POSTGRES_DB`: agno_db
- `GROQ_API_KEY`: [Sua chave da API Groq]

### Security Best Practices
1. **Use AWS Secrets Manager** para senhas em produção
2. **Configure HTTPS** no ALB com certificado SSL
3. **Mantenha RDS em subnets privadas**
4. **Configure backup automático** do RDS
5. **Monitore logs** regularmente
6. **Use least privilege** nas IAM roles

---

## 🧹 Limpeza de Recursos

Para evitar custos, delete os recursos na ordem:
1. **ECS Service** → Delete service
2. **ECS Cluster** → Delete cluster  
3. **Load Balancer** → Delete
4. **Target Group** → Delete
5. **RDS Instance** → Delete (sem snapshot para teste)
6. **VPC** → Delete VPC (deleta subnets, gateways, etc.)

---

## ✅ Checklist Final

- [ ] VPC e subnets criadas
- [ ] Security groups configurados
- [ ] RDS PostgreSQL funcionando
- [ ] ECS Cluster criado
- [ ] Task Definition configurada
- [ ] Load Balancer configurado
- [ ] ECS Service rodando
- [ ] Aplicação acessível via ALB
- [ ] Health checks passando
- [ ] Logs funcionando no CloudWatch