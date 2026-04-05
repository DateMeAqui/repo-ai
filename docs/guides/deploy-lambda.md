# Deploy para AWS

Como fazer deploy das Lambdas geradas para AWS.

## Pré-requisitos

- AWS CLI configurada (`aws configure`)
- Permissões IAM adequadas
- SAM CLI instalada (opcional)

## Via REST API

```bash
curl -X POST http://localhost:8000/api/v1/deploy \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{
    "project_name": "pet-finder",
    "environment": "prod",
    "lambda_settings": {
      "memory": 512,
      "timeout": 60
    }
  }'
```

## Via CLI

```bash
# Deploy básico
lambda-generator deploy pet-finder

# Com opções
lambda-generator deploy pet-finder \
  --env staging \
  --memory 512 \
  --timeout 120

# Com文化的文化
lambda-generator deploy pet-finder \
  --env prod \
  --stack-name pet-finder-prod
```

## Via WebSocket

```python
ws.send(json.dumps({
    "type": "message",
    "content": "Faça deploy do projeto pet-finder para produção"
}))
```

## Fluxo de Deploy

```
1. Valida projeto local
   │
   ▼
2. Compacta código (ZIP)
   │
   ▼
3. Faz upload para S3
   │
   ▼
4. Cria/atualiza CloudFormation stack
   │
   ▼
5. Cria Lambda function
   │
   ▼
6. Configura triggers (SQS, SNS, etc)
   │
   ▼
7. Atualiza permissões IAM
   │
   ▼
8. Deploy completo
```

## Ambientes

### Desenvolvimento

```yaml
environment: dev
lambda:
  memory: 256
  timeout: 30
sns:
  prefix: dev-
sqs:
  prefix: dev-
```

### Produção

```yaml
environment: prod
lambda:
  memory: 1024
  timeout: 300
sns:
  prefix: prod-
sqs:
  prefix: prod-
```

## Recursos Criados

| Recurso | Nome | Descrição |
|---------|------|-----------|
| Lambda | `{project}-{env}` | Função principal |
| IAM Role | `{project}-{env}-role` | Permissões |
| SNS Topic | `{project}-{env}-notifications` | Notificações |
| SQS Queue | `{project}-{env}-queue` | Fila de mensagens |
| API Gateway | `{project}-{env}-api` | HTTP endpoint |

## Outputs

Após deploy:

```json
{
  "status": "deployed",
  "resources": {
    "lambda": "arn:aws:lambda:us-east-1:123456:function:pet-finder-prod",
    "api_gateway": "https://abc123.execute-api.us-east-1.amazonaws.com/prod",
    "sns_topic": "arn:aws:sns:us-east-1:123456:pet-finder-prod-notifications",
    "sqs_queue": "https://sqs.us-east-1.amazonaws.com/123456/pet-finder-prod-queue"
  }
}
```

## Rollback

```bash
# Rollback último deploy
lambda-generator rollback pet-finder

# Rollback para versão específica
lambda-generator rollback pet-finder --version v2
```

## Monitoramento

### CloudWatch Logs

```bash
# Ver logs
aws logs tail /aws/lambda/pet-finder-prod --follow

# Filtrar erros
aws logs filter-log-events \
  --log-group-name /aws/lambda/pet-finder-prod \
  --filter-pattern "ERROR"
```

### X-Ray Tracing

Ativado por padrão:

```python
def lambda_handler(event, context):
    # Tracing automático via X-Ray
    return {"status": "ok"}
```

## Cleanup

```bash
# Remove todos os recursos
lambda-generator delete pet-finder-prod

# Confirmação
lambda-generator delete pet-finder-prod --force
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `AccessDenied` | Verifique permissões IAM |
| `ResourceConflict` | Recurso já existe - use update |
| `Timeout` | Aumente timeout ou simplify Lambda |
| `MemoryExceeded` | Aumente memory size |
