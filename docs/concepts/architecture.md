# Arquitetura

Visão geral da arquitetura do Lambda Generator API.

## Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                        Lambda Generator API                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    │
│  │  REST API   │    │  WebSocket  │    │   Firecrawl     │    │
│  │  (FastAPI)  │    │   Server   │    │   Integration   │    │
│  └──────┬──────┘    └──────┬──────┘    └────────┬────────┘    │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             │                                  │
│                    ┌────────▼────────┐                        │
│                    │   Chat Agent    │                        │
│                    │    (OpenAI)     │                        │
│                    └────────┬────────┘                        │
│                             │                                  │
│         ┌───────────────────┼───────────────────┐              │
│         │                   │                   │              │
│  ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐      │
│  │   Parser    │    │   Generator   │   │  Validator  │      │
│  │  Module     │    │    Module     │   │   Module    │      │
│  └──────┬──────┘    └───────┬───────┘   └──────┬──────┘      │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             │                                  │
│                    ┌────────▼────────┐                        │
│                    │   Storage       │                        │
│                    │   Manager      │                        │
│                    └────────┬────────┘                        │
└─────────────────────────────┼─────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │   S3     │    │  Cloud   │    │  Local   │
        │          │    │ Formation│    │  Temp    │
        └──────────┘    └──────────┘    └──────────┘
```

## Componentes

### REST API (`/api/v1`)

Endpoints para operações síncronas:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/generate-lambda` | POST | Gera código Lambda |
| `/deploy` | POST | Faz deploy para AWS |
| `/status/{job_id}` | GET | Status de job |
| `/docs/upload` | POST | Upload de documentação |

### WebSocket (`/ws/chat/{session_id}`)

Canal para comunicação estilo chat:

1. Cliente conecta com `session_id`
2. Envia mensagens em formato JSON
3. Recebe streaming de respostas
4. Suporta upload de arquivos inline

### Parser Module

Extrai endpoints da documentação:

```
Input Formats:
├── OpenAPI JSON
├── OpenAPI YAML
├── Postman Collection
└── URL (Firecrawl)
```

### Chat Agent

Usa OpenAI GPT-4 para:

1. Analisar documentação
2. Interpretar intenções do usuário
3. Gerar código Python
4. Adicionar configurações AWS

### Generator Module

Produz:

```
output/
├── handler.py        # Lambda handler
├── requirements.txt  # Dependências
├── template.yaml     # SAM/CloudFormation
├── config.py         # Configurações
└── README.md         # Documentação
```

## Fluxo de Dados

### Via REST API

```
1. POST /generate-lambda
   └─> Validate request
       └─> Parse documentation
           └─> Extract endpoints
               └─> Call Chat Agent
                   └─> Generate Lambda code
                       └─> Save to storage
                           └─> Return metadata
```

### Via WebSocket

```
1. Client connects /ws/chat/{session_id}
2. Client sends message (text or doc)
3. Server acknowledges
4. Agent processes (streaming)
5. Server sends chunks
6. Final response with actions
```

## Armazenamento

| Tipo | Local | Uso |
|------|-------|-----|
| Código Gerado | `./temp/{project}/` | Desenvolvimento |
| Artefatos | `s3://{bucket}/artifacts/` | Deploy |
| Sessões | Memória/Redis | Chat sessions |
| Logs | CloudWatch | Operations |

## Segurança

```
┌─────────────────────────────────────────┐
│              API Gateway                 │
│  ┌───────────────────────────────────┐  │
│  │     Rate Limiting (100/min)       │  │
│  │     API Key Authentication        │  │
│  │     CORS Configuration            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Escalabilidade

- **Horizontal**: FastAPI + Uvicorn workers
- **WebSocket**: Suporte a múltiplas conexões simultâneas
- **Chat Agent**: Rate limiting por sessão
- **Storage**: Suporte a S3 para multi-instância

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| API | FastAPI, Uvicorn |
| WebSocket | FastAPI WebSockets |
| AI | OpenAI API (GPT-4) |
| AWS SDK | boto3 |
| Documentation Fetch | Firecrawl |
| Parsers | openapi-spec-validator, PyYAML |
| Deployment | AWS SAM, CloudFormation |
