# ⏸️ Pausar e Reativar Serviços AWS

## 😴 **Para Dormir Tranquilo - Pausar Recursos**

### **🛑 1. Parar ECS Service (OBRIGATÓRIO)**
**💰 Economia: ~$15/mês**

1. **Acessar ECS Console**
2. **Ir para** cluster `rag-app-cluster`
3. **Clicar** no service `rag-app-service`
4. **Clicar** em "Update service"
5. **Alterar** "Desired tasks" de `1` para `0`
6. **Clicar** em "Update"

**⏱️ Tempo**: 30 segundos

---

### **🛑 2. Parar RDS Database (OPCIONAL)**
**💰 Economia: ~$15/mês adicional**

1. **Acessar RDS Console**
2. **Ir para** "Databases"
3. **Selecionar** `rag-app-postgres`
4. **Actions** → "Stop temporarily"
5. **Confirmar** (para por 7 dias automaticamente)

**⏱️ Tempo**: 1 minuto

---

## 🌅 **Para Reativar - Acordar os Serviços**

### **▶️ 1. Religar ECS Service**
1. **ECS Console** → cluster `rag-app-cluster`
2. **Clicar** no service `rag-app-service`
3. **Update service**
4. **Alterar** "Desired tasks" de `0` para `1`
5. **Update**

**⏱️ Tempo**: 2-3 minutos para container iniciar

---

### **▶️ 2. Religar RDS (se parou)**
1. **RDS Console** → "Databases"
2. **Selecionar** `rag-app-postgres`
3. **Actions** → "Start"
4. **Confirmar**

**⏱️ Tempo**: 3-5 minutos para database iniciar

---

## 💰 **Custos Durante a Pausa**

| Componente | Status | Custo/dia |
|------------|--------|-----------|
| **ECS Service** | Parado (0 tasks) | $0 |
| **RDS** | Parado | $0 |
| **Load Balancer** | Ativo | ~$0.60 |
| **VPC/Subnets** | Ativo | $0 |
| **Security Groups** | Ativo | $0 |
| **Task Definition** | Ativo | $0 |

**💸 Total durante pausa**: ~$0.60/dia (só ALB)

---

## 🚀 **Método Ultra-Rápido**

### **Para Pausar:**
```
ECS → rag-app-cluster → rag-app-service → Update → Desired tasks: 0
```

### **Para Reativar:**
```
ECS → rag-app-cluster → rag-app-service → Update → Desired tasks: 1
```

---

## ⚠️ **Recursos que NÃO Precisam Parar**

- ✅ **VPC e Subnets**: Gratuitos sempre
- ✅ **Security Groups**: Gratuitos sempre
- ✅ **ECS Cluster vazio**: Gratuito quando sem tasks
- ✅ **Task Definition**: Gratuito sempre
- ✅ **Load Balancer**: Baixo custo (~$22/mês, pode manter)

---

## 🔄 **Rotina Diária Recomendada**

### **🌙 Antes de Dormir:**
1. Parar ECS Service (0 tasks)
2. Opcionalmente parar RDS

### **🌅 Ao Acordar:**
1. Religar ECS Service (1 task)
2. Religar RDS (se parou)
3. Aguardar 2-3 minutos
4. Testar: `http://SEU-ALB-DNS/docs`

---

## 📊 **Monitoramento de Status**

### **✅ Verificar se está Parado:**
- **ECS**: Running tasks = 0
- **RDS**: Status = "Stopped"

### **✅ Verificar se está Ativo:**
- **ECS**: Running tasks = 1, Status = "RUNNING"
- **RDS**: Status = "Available"
- **API**: Responde em `/docs`

---

## 💡 **Dicas de Economia**

1. **Pause sempre** quando não estiver desenvolvendo
2. **RDS pode ficar parado** até 7 dias seguidos
3. **ECS Task** é cobrado por segundo (pause sem medo)
4. **ALB** custa pouco, pode manter sempre ativo
5. **Considere usar** AWS Budget para alertas de custo

---

## 🧹 **Deletar Tudo (Só em Emergência)**

Se quiser **deletar permanentemente** todos os recursos:

### **Ordem de Deleção:**
1. **ECS Service** → Delete service
2. **ECS Cluster** → Delete cluster  
3. **Load Balancer** → Delete
4. **Target Group** → Delete
5. **RDS Instance** → Delete (sem snapshot)
6. **VPC** → Delete VPC (remove tudo)

**⚠️ ATENÇÃO**: Isso remove TUDO permanentemente!

---

## 📞 **Suporte**

- **Problemas para reativar?** Verifique logs no CloudWatch
- **Task não inicia?** Verifique se RDS está "Available"
- **API não responde?** Aguarde 2-3 minutos após reativação
- **Custos inesperados?** Verifique AWS Billing Dashboard

**😴 Boa noite e economia garantida!** 💰