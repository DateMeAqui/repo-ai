# repo-ai

**Lambda Generator API** - API que gera Lambdas AWS com serviços serverless a partir de documentação de APIs externas, através de uma interface de chat estilo LLM.

## Quick Start

```bash
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
uvicorn main:app --reload
```

Acesse: http://localhost:8000/docs

## Documentação

📖 **[docs/README.md](docs/README.md)** - Navegação completa

| Categoria | Docs |
|-----------|------|
| **Primeiros Passos** | [Quickstart](docs/getting-started/quickstart.md), [Instalação](docs/getting-started/installation.md), [Configuração](docs/getting-started/configuration.md) |
| **Guias** | [Chat](docs/guides/chat-interface.md), [Upload](docs/guides/upload-documentation.md), [Deploy](docs/guides/deploy-lambda.md) |
| **Referência** | [API REST](docs/reference/api-rest.md), [WebSocket](docs/reference/api-websocket.md) |
| **Conceitos** | [Arquitetura](docs/concepts/architecture.md), [AWS Services](docs/concepts/aws-services.md) |

## Features

- 🤖 Interface de chat estilo LLM
- 📄 Suporte a OpenAPI (JSON/YAML), Postman Collections
- 🔗 Fetch automático de docs via Firecrawl
- ☁️ Gera Lambda + SNS, SQS, EventBridge, DynamoDB
- 🚀 Deploy direto para AWS
