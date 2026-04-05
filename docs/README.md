# Lambda Generator API

API que gera Lambdas AWS com serviços serverless (SNS, SQS, EventBridge, DynamoDB) a partir de documentação de APIs externas, através de uma interface de chat estilo LLM.

## Navegação Rápida

### Primeiros Passos
- [Quickstart](./getting-started/quickstart.md) - Primeira Lambda em 5 minutos
- [Instalação](./getting-started/installation.md) - Setup completo do ambiente
- [Configuração](./getting-started/configuration.md) - Credenciais AWS

### Guias Práticos
- [Interface de Chat](./guides/chat-interface.md) - Como usar o chat
- [Upload de Documentação](./guides/upload-documentation.md) - Upload OpenAPI/Postman
- [Buscar de URL](./guides/fetch-from-url.md) - Usar Firecrawl
- [Deploy Lambda](./guides/deploy-lambda.md) - Deploy para AWS
- [Configurar SNS](./guides/configure-sns.md) - Pub/Sub
- [Configurar SQS](./guides/configure-sqs.md) - Filas de mensagens
- [Configurar EventBridge](./guides/configure-eventbridge.md) - Event-driven

### Referência
- [API REST](./reference/api-rest.md) - Endpoints
- [API WebSocket](./reference/api-websocket.md) - Protocolo de chat
- [Schemas](./reference/schemas.md) - JSON Schemas
- [CLI](./reference/cli.md) - Comandos

### Conceitos
- [Arquitetura](./concepts/architecture.md) - Visão geral
- [AWS Services](./concepts/aws-services.md) - Lambda + serviços serverless
- [Firecrawl Integration](./concepts/firecrawl-integration.md) - Fetch de URLs
- [Estrutura do Código](./concepts/generated-code-structure.md) - Código gerado

## Características

- **Interface Chat** - Converse com a API como um assistente LLM
- **Multi-format** - Suporta OpenAPI (JSON/YAML) e Postman Collections
- **Firecrawl** - Busca documentação automaticamente de URLs
- **AWS Serverless** - Gera Lambda + SNS, SQS, EventBridge, DynamoDB
- **Templates** - Código Python otimizado para AWS Lambda

## Começando

```bash
# 1. Clone o repositório
git clone <repo-url>

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure AWS credentials
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>

# 4. Inicie a API
uvicorn main:app --reload

# 5. Acesse http://localhost:8000/docs
```

## Links

- [Changelog](./CHANGELOG.md) - Histórico de versões
- Snippets: [SNS](./snippets/boto3-sns.md), [SQS](./snippets/boto3-sqs.md), [DynamoDB](./snippets/boto3-dynamodb.md)
