# API Doc Builder — Documentação Completa do Projeto

> Versão: 1.0.0 | Status: Draft | Data: 2026-04-05
> **Stack**: Python 3.11 + FastAPI | React/Next.js | AWS SAM | OpenAI GPT-4

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Fluxo de Funcionamento](#3-fluxo-de-funcionamento)
4. [Interface do Cliente (Chat UI)](#4-interface-do-cliente-chat-ui)
5. [Integração com Firecrawl](#5-integração-com-firecrawl)
6. [Geração de AWS Lambdas](#6-geração-de-aws-lambdas)
7. [Serviços AWS Suportados](#7-serviços-aws-suportados)
8. [Estrutura de Pastas do Projeto](#8-estrutura-de-pastas-do-projeto)
9. [API Interna — Endpoints](#9-api-interna--endpoints)
10. [Variáveis de Ambiente](#10-variáveis-de-ambiente)
11. [Free Tier & Rate Limits](#11-free-tier--rate-limits)
12. [Modelos de Dados](#12-modelos-de-dados)
13. [Tratamento de Erros](#13-tratamento-de-erros)
14. [Segurança](#14-segurança)
15. [Deploy e Infraestrutura](#15-deploy-e-infraestrutura)
16. [Custos AWS Estimados](#16-custos-aws-estimados)
17. [Roadmap](#17-roadmap)

---

## 1. Visão Geral

### O que é o API Doc Builder?

O **API Doc Builder** é uma plataforma SaaS que permite a qualquer desenvolvedor ou equipe de engenharia **importar a documentação de uma API externa** (via arquivo Markdown ou URL) e, a partir dela, **gerar automaticamente AWS Lambda Functions** configuradas com os serviços necessários: SNS, SQS, EventBridge, DynamoDB, S3, e outros.

A comunicação com o usuário ocorre por meio de uma **interface de chat conversacional** — semelhante aos assistentes LLM modernos — onde o cliente descreve o que precisa, faz upload do DOC da API e recebe o código pronto para deploy.

### Problema que resolve

- Elimina o trabalho manual de criar Lambdas, filas e tópicos do zero para cada nova API integrada.
- Reduz o tempo de integração de dias para minutos.
- Padroniza a criação de serviços serverless em times de engenharia.

### Usuários-alvo

- Engenheiros de backend que integram APIs de terceiros
- Times de plataforma / DevOps
- Arquitetos de solução AWS

---

## 2. Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                        │
│                   Chat UI  ─  React / Next.js                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                      AWS API Gateway                             │
│              REST API + WebSocket API                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Chat Routes │  │ Docs Routes │  │  Projects Routes    │  │
│  │ + WebSocket │  │ + Firecrawl │  │  + S3 Upload       │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬─────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                     │
│                   ┌───────▼───────┐                             │
│                   │  OpenAI GPT-4 │                              │
│                   │  (code gen)   │                              │
│                   └───────┬───────┘                             │
└───────────────────────────┼───────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
       ┌──────▼──┐   ┌──────▼──┐  ┌──────▼──┐
       │   S3    │   │DynamoDB │  │   SNS   │
       │(outputs)│   │(sessions│  │(notific.)│
       │         │   │ /state) │  │         │
       └─────────┘   └─────────┘  └─────────┘
                            │
                   ┌────────▼────────┐
                   │    SQS Queue    │◄── Lambdas assíncronas
                   │ (job-processing)│
                   └────────┬────────┘
                            │
               ┌────────────▼────────────┐
               │  Lambdas (Python 3.11)  │
               │  ├── doc-parser         │
               │  ├── code-builder       │
               │  └── job-processor      │
               └─────────────────────────┘
```

### Componentes Principais

| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| **Chat UI** | React + Next.js | Interface conversacional do cliente |
| **API Gateway** | AWS API Gateway | Roteamento REST e WebSocket |
| **API Backend** | Python 3.11 + FastAPI | Endpoints REST, WebSocket, Business Logic |
| **Lambda: Doc Parser** | Python 3.11 | Processa Markdown ou chama Firecrawl |
| **Lambda: Code Builder** | Python 3.11 + OpenAI | Gera código Lambda + IaC |
| **Lambda: Job Processor** | Python 3.11 | Executa jobs da fila SQS |
| **IaC** | AWS SAM | Templates CloudFormation para deploy |
| **SQS** | AWS SQS | Fila de processamento assíncrono |
| **SNS** | AWS SNS | Notificações de conclusão ao cliente |
| **DynamoDB** | AWS DynamoDB | Sessões, histórico de chat, projetos |
| **S3** | AWS S3 | Artefatos gerados (zip, tf, yaml) |

---

## 3. Fluxo de Funcionamento

### Fluxo Principal — Upload de arquivo Markdown

```
1. Usuário abre o Chat UI
2. Inicia uma conversa descrevendo a API que deseja integrar
3. Faz upload do arquivo .md com a documentação da API externa
4. O sistema extrai: endpoints, métodos, payloads, autenticação
5. O LLM faz perguntas de refinamento ao usuário:
      - "Qual serviço AWS você quer usar? (SQS, SNS, DynamoDB...)"
      - "Precisa de retry automático?"
      - "Qual o timeout esperado para cada Lambda?"
6. Com base nas respostas, o Code Builder gera:
      - Lambda handlers (Node.js ou Python)
      - Terraform ou SAM YAML para provisionamento
      - Variáveis de ambiente (.env.example)
      - README com instruções de deploy
7. O usuário recebe um link para download do .zip no S3
8. Uma notificação é enviada via SNS (email / webhook)
```

### Fluxo Alternativo — URL da Documentação

```
1. Usuário informa uma URL em vez de fazer upload de arquivo
2. O sistema detecta que é uma URL (começa com http/https)
3. Chama o serviço Firecrawl API:
      POST https://api.firecrawl.dev/v2/scrape
      { "url": "<url_informada>", "formats": ["markdown"] }
4. Firecrawl retorna o conteúdo da página como Markdown limpo
5. O fluxo continua igual ao fluxo principal a partir do passo 4
```

### Diagrama de sequência — URL via Firecrawl

```
Cliente        Chat API       Firecrawl       Doc Parser     Code Builder
  │                │               │               │               │
  │──── URL ──────►│               │               │               │
  │                │──── scrape ──►│               │               │
  │                │◄─ markdown ───│               │               │
  │                │──────────────────── parse ───►│               │
  │                │◄────────────────── schema ────│               │
  │                │──────────────────────────────────── build ───►│
  │◄── artifacts ──│◄──────────────────────────────────── zip ─────│
```

---

## 4. Interface do Cliente (Chat UI)

### Descrição Geral

A interface é um **chat estilo LLM** — similar ao ChatGPT ou Claude.ai — onde toda a interação acontece em linguagem natural. O usuário não precisa preencher formulários ou configurar nada manualmente.

### Funcionalidades da Chat UI

- **Upload de arquivo Markdown** via drag-and-drop ou botão de anexo
- **Colagem de URL** diretamente na caixa de texto
- **Streaming de respostas** em tempo real (Server-Sent Events)
- **Histórico de conversas** persistido por sessão
- **Preview de código gerado** com syntax highlight
- **Botão de download** do artefato final (.zip)
- **Notificações de progresso**: "Analisando documentação...", "Gerando Lambdas...", "Pronto!"

### Estados da Conversa

```
IDLE → AWAITING_DOC → PARSING → CLARIFICATION → BUILDING → DONE
                                      ↑               │
                                      └───────────────┘
                              (loop de perguntas/respostas)
```

### Exemplos de Interação

**Usuário:**
> "Quero criar uma integração com a API do Stripe para processar webhooks de pagamento."

**Sistema:**
> "Ótimo! Pode me enviar a documentação do endpoint de webhooks do Stripe? Você pode fazer upload de um arquivo .md ou colar a URL da documentação."

**Usuário:**
> "Aqui está: https://stripe.com/docs/api/events"

**Sistema:**
> "Analisando a documentação via Firecrawl... ✅  
> Encontrei os seguintes eventos: `payment_intent.succeeded`, `payment_intent.payment_failed`, `charge.refunded`.  
> Qual serviço AWS você prefere para enfileirar os eventos recebidos? SQS, SNS ou EventBridge?"

---

## 5. Integração com Firecrawl

### O que é o Firecrawl?

O [Firecrawl](https://docs.firecrawl.dev/introduction) é uma API de scraping e crawling de páginas web que converte qualquer URL em **Markdown limpo e pronto para uso com LLMs**. Ele lida automaticamente com JavaScript rendering, proxies, anti-bots e conteúdo dinâmico.

### Como é usado neste projeto

Quando o usuário informa uma URL em vez de um arquivo, o sistema chama a API do Firecrawl para obter o conteúdo da página como Markdown, que é então processado pelo Doc Parser da mesma forma que um arquivo uploadado.

### Endpoint utilizado

```
POST https://api.firecrawl.dev/v2/scrape
Authorization: Bearer <FIRECRAWL_API_KEY>
Content-Type: application/json

{
  "url": "<url_da_doc_da_api_externa>",
  "formats": ["markdown"]
}
```

### Resposta esperada

```json
{
  "success": true,
  "data": {
    "markdown": "# Título da Documentação\n\n## Endpoint GET /users\n...",
    "metadata": {
      "title": "API Reference",
      "sourceURL": "https://exemplo.com/docs/api"
    }
  }
}
```

### Implementação no Lambda: Doc Parser

```javascript
// lambda/doc-parser/firecrawl.js
const axios = require('axios');

async function scrapeUrl(url) {
  const response = await axios.post(
    'https://api.firecrawl.dev/v2/scrape',
    {
      url,
      formats: ['markdown']
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.FIRECRAWL_API_KEY}`,
        'Content-Type': 'application/json'
      }
    }
  );

  if (!response.data.success) {
    throw new Error(`Firecrawl falhou: ${JSON.stringify(response.data)}`);
  }

  return response.data.data.markdown;
}

module.exports = { scrapeUrl };
```

### Detecção automática de URL vs. Arquivo

```javascript
// Lógica no Chat Handler
function isUrl(input) {
  try {
    const url = new URL(input);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

async function processUserInput(input, attachment) {
  if (attachment) {
    // Arquivo Markdown enviado diretamente
    return parseMarkdown(attachment.content);
  } else if (isUrl(input)) {
    // URL detectada — usar Firecrawl
    const markdown = await scrapeUrl(input);
    return parseMarkdown(markdown);
  }
}
```

### Tratamento de erros do Firecrawl

| Código HTTP | Causa | Ação |
|---|---|---|
| 401 | API Key inválida | Logar erro, informar ao usuário |
| 429 | Rate limit excedido | Retry com backoff exponencial (máx. 3x) |
| 422 | URL inválida ou inacessível | Informar ao usuário para tentar outra URL |
| 500 | Erro interno Firecrawl | Retry 1x, depois pedir upload manual |

---

## 6. Geração de AWS Lambdas

### O que é gerado

Para cada integração, o sistema produz um pacote `.zip` com:

```
output/
├── lambdas/
│   ├── webhook-receiver/
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── event-processor/
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── notifier/
│       ├── handler.py
│       └── requirements.txt
├── infrastructure/
│   ├── template.yaml        # AWS SAM
│   ├── parameters.json
│   └── .env.example
└── README.md
```

### Padrão de Lambda gerado (Python)

```python
# lambdas/webhook-receiver/handler.py
import json
import boto3
import os

sqs = boto3.client('sqs')

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))

    # Validação baseada no schema extraído da DOC
    if not body.get('type') or not body.get('data'):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Payload inválido'})
        }

    # Enfileirar para processamento assíncrono
    sqs.send_message(
        QueueUrl=os.environ['SQS_QUEUE_URL'],
        MessageBody=json.dumps(body),
        MessageAttributes={
            'EventType': {
                'StringValue': body.get('type', 'unknown'),
                'DataType': 'String'
            }
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'received': True})
    }
```

```text
# lambdas/webhook-receiver/requirements.txt
boto3>=1.28.0
```

### AWS SAM gerado (exemplo)

```yaml
# infrastructure/template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Environment:
      Variables:
        AWS_REGION: !Ref AWS::Region
        SQS_QUEUE_URL: !Ref EventQueue

Parameters:
  ProjectName:
    Type: String
    Default: my-project

Resources:
  # Lambda Function
  WebhookReceiver:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub ${ProjectName}-webhook-receiver
      Handler: handler.lambda_handler
      Policies:
        - SQSSendMessagePolicy:
            QueueName: !GetAtt EventQueue.QueueName
      Environment:
        Variables:
          SQS_QUEUE_URL: !Ref EventQueue
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /webhook
            Method: post

  # SQS Queue
  EventQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${ProjectName}-events
      VisibilityTimeout: 60
      MessageRetentionPeriod: 86400
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt EventDLQ.Arn
        maxReceiveCount: 3

  # Dead Letter Queue
  EventDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub ${ProjectName}-events-dlq

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/webhook"
```

---

## 7. Serviços AWS Suportados

### SQS (Simple Queue Service)

**Quando usar:** Processamento assíncrono de eventos, desacoplamento de serviços, filas de retry.

**O que é gerado:**
- Fila principal com Dead Letter Queue (DLQ) configurada
- Lambda trigger (Event Source Mapping)
- IAM policies para envio e recebimento
- Configuração de retry (maxReceiveCount: 3)

### SNS (Simple Notification Service)

**Quando usar:** Notificações fan-out, múltiplos consumidores para o mesmo evento, alertas.

**O que é gerado:**
- Tópico SNS com nome derivado da API
- Subscriptions (email, SQS, Lambda)
- Lambda para publicar eventos no tópico
- IAM policies de publish

### EventBridge

**Quando usar:** Event-driven architecture com roteamento por regras, integração com outros serviços AWS.

**O que é gerado:**
- Event Bus customizado
- Rules baseadas nos eventos identificados na documentação
- Targets para Lambdas downstream

### DynamoDB

**Quando usar:** Persistência de estado, cache de tokens/sessões, armazenamento de resultados.

**O que é gerado:**
- Tabela com partition key e sort key derivados do schema da API
- TTL configurado para dados temporários
- DynamoDB Streams (opcional)
- Lambda de leitura/escrita com otimistic locking

### S3

**Quando usar:** Armazenamento de payloads grandes, arquivos de resultado, logs.

**O que é gerado:**
- Bucket com versionamento
- Lifecycle policies
- Lambda trigger para novos objetos (opcional)
- Presigned URL helper function

### API Gateway + Lambda (Webhook Receiver)

**Quando usar:** Receber webhooks de APIs externas via HTTP.

**O que é gerado:**
- API Gateway HTTP API
- Lambda integrada para receber e validar requests
- Validação de assinatura HMAC (se a API usa)

---

## 8. Estrutura de Pastas do Projeto

```
api-doc-builder/
├── apps/
│   └── web/                         # Chat UI (Next.js + TypeScript)
│       ├── components/
│       │   ├── ChatWindow.tsx
│       │   ├── MessageBubble.tsx
│       │   ├── FileUploader.tsx
│       │   └── CodePreview.tsx
│       ├── pages/
│       │   ├── index.tsx
│       │   └── chat/[sessionId].tsx
│       ├── lib/
│       │   ├── api.ts
│       │   └── websocket.ts
│       └── package.json
├── backend/                         # Backend Python (FastAPI)
│   ├── main.py                      # Entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── docs.py
│   │   │   └── projects.py
│   │   ├── models/
│   │   │   ├── session.py
│   │   │   └── project.py
│   │   └── schemas/
│   │       └── requests.py
│   ├── services/
│   │   ├── firecrawl.py
│   │   ├── openai_client.py
│   │   ├── code_generator.py
│   │   └── storage.py
│   ├── lambdas/
│   │   ├── doc-parser/              # Lambda: Parseia Markdown
│   │   │   ├── handler.py
│   │   │   └── requirements.txt
│   │   ├── code-builder/            # Lambda: Gera código
│   │   │   ├── handler.py
│   │   │   └── requirements.txt
│   │   └── job-processor/           # Lambda: Processa SQS
│   │       ├── handler.py
│   │       └── requirements.txt
│   └── templates/
│       ├── lambda_sqs.py.j2
│       ├── lambda_sns.py.j2
│       ├── sam_template.yaml.j2
│       └── readme.md.j2
├── infrastructure/
│   ├── platform/                    # IaC da plataforma (SAM)
│   │   ├── template.yaml
│   │   ├── parameters.json
│   │   └── samconfig.toml
│   └── modules/
│       ├── api-backend/
│       ├── lambda-functions/
│       └── queue-system/
├── packages/
│   ├── shared-types/                # TypeScript types (apps/web)
│   └── python-sdk/                  # SDK cliente Python (futuro)
├── docs/                            # Esta documentação
├── tests/
│   ├── python/                      # pytest
│   │   ├── unit/
│   │   └── integration/
│   └── web/                         # Jest/Playwright
│       ├── unit/
│       └── e2e/
├── .env.example
├── requirements.txt                 # Python deps
├── package.json                     # Node.js deps (monorepo)
├── pyproject.toml                   # Python project config
├── turbo.json                       # Turborepo config
└── README.md
```

---

## 9. API Interna — Endpoints

### Chat

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/sessions` | Cria nova sessão de chat |
| `GET` | `/sessions/:id` | Retorna histórico da sessão |
| `POST` | `/sessions/:id/messages` | Envia mensagem (streaming via SSE) |
| `DELETE` | `/sessions/:id` | Encerra e limpa sessão |

### Documentação

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/docs/upload` | Upload de arquivo Markdown |
| `POST` | `/docs/scrape` | Envia URL para scraping via Firecrawl |
| `GET` | `/docs/:id/schema` | Retorna schema extraído da documentação |

### Projetos / Geração

| Método | Path | Descrição |
|---|---|---|
| `POST` | `/projects` | Cria projeto de geração de código |
| `GET` | `/projects/:id` | Status do projeto |
| `GET` | `/projects/:id/download` | URL pré-assinada do .zip no S3 |
| `GET` | `/projects` | Lista projetos do usuário |

### Exemplo: POST /sessions/:id/messages (Streaming)

**Request:**
```json
POST /api/v1/sessions/sess_abc123/messages
{
  "content": "Quero usar SQS para enfileirar os webhooks do Stripe",
  "attachment": {
    "type": "markdown",
    "content": "# Stripe API\n## Webhooks\n..."
  }
}
```

**Response (Server-Sent Events):**
```
text/event-stream
data: {"type":"text","content":"Entendi! "}
data: {"type":"text","content":"Vou configurar uma fila SQS..."}
data: {"type":"progress","step":"parsing","status":"done"}
data: {"type":"progress","step":"building","status":"running"}
data: {"type":"done","projectId":"proj_xyz789"}
```

### Exemplo: FastAPI Route (Python)

```python
# backend/api/routes/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Processa mensagem com OpenAI
            async for chunk in process_message(session_id, message):
                await websocket.send_text(chunk)
    except WebSocketDisconnect:
        await cleanup_session(session_id)

@router.post("/api/v1/sessions/{session_id}/messages")
async def send_message(session_id: str, message: MessageRequest):
    return StreamingResponse(
        stream_response(session_id, message),
        media_type="text/event-stream"
    )
```

---

## 10. Variáveis de Ambiente

```bash
# ── Firecrawl ──────────────────────────────
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxx

# ── OpenAI ─────────────────────────────────
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# ── AWS ────────────────────────────────────
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# ── DynamoDB ───────────────────────────────
SESSIONS_TABLE=api-doc-builder-sessions
PROJECTS_TABLE=api-doc-builder-projects

# ── SQS ────────────────────────────────────
JOB_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/api-doc-builder-jobs
JOB_QUEUE_DLQ_URL=https://sqs.us-east-1.amazonaws.com/123456789012/api-doc-builder-jobs-dlq

# ── SNS ────────────────────────────────────
NOTIFICATIONS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:api-doc-builder-notifications

# ── S3 ─────────────────────────────────────
OUTPUT_BUCKET=api-doc-builder-outputs
OUTPUT_BUCKET_PREFIX=generated/

# ── API Gateway ────────────────────────────
API_GATEWAY_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod
WEBSOCKET_API_URL=wss://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod

# ── FastAPI (Backend) ──────────────────────
APP_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://app.example.com
```

---

## 11. Free Tier & Rate Limits

### Free Tier da Plataforma

| Recurso | Limite | Observações |
|---------|--------|-------------|
| Gerações de Lambda | 10/mês | Por conta |
| Processamento de documentação | 100MB/mês | Upload + scraping |
| Presigned URL para download | 24h | Expiração do link |
| Sessões de chat ativas | 50 simultâneas | Por conta |
| Histórico de projetos | 20 projetos | Armazenados |

### Rate Limits por Serviço

| Serviço | Plano Free | Plano Pro |
|---------|------------|-----------|
| **Firecrawl API** | 100 req/dia (sem key) | 1.000 req/dia |
| **OpenAI API** | Conforme plano do usuário | Conforme plano |
| **API Gateway** | 100 req/min | 1.000 req/min |
| **WebSocket** | 60 conexões/min | 600 conexões/min |
| **S3 Upload** | 50 uploads/hora | 500 uploads/hora |

### Limites Técnicos

| Item | Limite | Ação ao Exceder |
|------|--------|-----------------|
| Tamanho arquivo upload | 10MB | Rejeitar com erro |
| Caracteres por mensagem | 4.000 | Truncar + aviso |
| Tempo de processamento | 5 min | Timeout + notificação |
| Tamanho output .zip | 50MB | Notificar usuário |
| Concurrent Lambda builds | 3 | Fila de espera |

### Planos (Futuro)

```
┌─────────────┬──────────────┬──────────────┐
│   Recurso   │    Free      │     Pro     │
├─────────────┼──────────────┼──────────────┤
│ Gerações    │ 10/mês       │ 100/mês     │
│ Docs size   │ 100MB        │ 1GB         │
│ Projetos    │ 20           │ Unlimited    │
│ Suporte     │ Community    │ Email       │
│ Deploy auto │ Não          │ Sim         │
└─────────────┴──────────────┴──────────────┘
```

---

## 12. Modelos de Dados

### Session (DynamoDB)

```json
{
  "sessionId": "sess_abc123",
  "userId": "user_xyz",
  "createdAt": "2026-04-05T12:00:00Z",
  "updatedAt": "2026-04-05T12:05:00Z",
  "status": "active",
  "messages": [
    {
      "role": "user",
      "content": "Quero integrar a API do Stripe",
      "timestamp": "2026-04-05T12:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Pode me enviar a documentação?",
      "timestamp": "2026-04-05T12:00:01Z"
    }
  ],
  "context": {
    "docId": "doc_stripe_001",
    "projectId": "proj_xyz789",
    "selectedServices": ["sqs", "sns"]
  },
  "ttl": 1754390400
}
```

### Project (DynamoDB)

```json
{
  "projectId": "proj_xyz789",
  "sessionId": "sess_abc123",
  "userId": "user_xyz",
  "status": "done",
  "createdAt": "2026-04-05T12:05:00Z",
  "completedAt": "2026-04-05T12:06:30Z",
  "apiName": "Stripe Webhooks",
  "sourceType": "url",
  "sourceUrl": "https://stripe.com/docs/api/events",
  "services": ["sqs", "lambda", "sns"],
  "lambdaCount": 3,
  "outputS3Key": "generated/proj_xyz789/output.zip",
  "outputDownloadUrl": "https://s3.amazonaws.com/...",
  "downloadUrlExpiresAt": "2026-04-06T12:06:30Z"
}
```

### DocSchema (estrutura extraída da documentação)

```json
{
  "docId": "doc_stripe_001",
  "title": "Stripe Events API",
  "baseUrl": "https://api.stripe.com/v1",
  "authentication": {
    "type": "bearer",
    "header": "Authorization"
  },
  "endpoints": [
    {
      "method": "POST",
      "path": "/webhooks",
      "description": "Recebe eventos de webhook",
      "requestBody": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "example": "payment_intent.succeeded" },
          "data": { "type": "object" }
        }
      }
    }
  ],
  "events": [
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.refunded"
  ]
}
```

---

## 13. Tratamento de Erros

### Estratégia Geral

Todos os erros são capturados e classificados em três categorias:

| Categoria | Exemplos | Ação |
|---|---|---|
| **Erros de usuário** | URL inválida, arquivo corrompido | Mensagem amigável no chat, pedir nova tentativa |
| **Erros de integração** | Firecrawl indisponível, LLM timeout | Retry automático + fallback para upload manual |
| **Erros de sistema** | Lambda falha, DynamoDB timeout | Alertar via SNS, registrar em CloudWatch |

### Dead Letter Queue (DLQ)

Jobs que falham 3 vezes consecutivas são movidos para a DLQ. Uma Lambda de monitoramento processa a DLQ e:
1. Notifica o usuário via email (SNS)
2. Salva o job para re-processamento manual
3. Registra o erro no CloudWatch

### Mensagens de erro no Chat (exemplos)

```
❌ "Não consegui acessar a URL informada. O site pode estar bloqueando scrapers,
    ou a URL pode estar incorreta. Tente fazer upload do arquivo Markdown diretamente."

⚠️ "A análise da documentação levou mais tempo que o esperado. 
    Estou processando em background e você receberá uma notificação por email quando estiver pronto."

✅ "Pronto! Seu pacote de Lambdas está disponível para download por 24 horas."
```

---

## 14. Segurança

### Autenticação

- Usuários autenticam via **Cognito User Pool** (JWT tokens)
- Tokens são validados no API Gateway via Lambda Authorizer
- Sessions são associadas ao `userId` do token

### Validação de Inputs

- Arquivos Markdown: máximo 10MB, apenas `.md` e `.txt`
- URLs: validadas com allowlist de domínios confiáveis (opcional) e timeout de 30s no Firecrawl
- Mensagens de chat: máximo 4.000 caracteres por mensagem

### Segurança do S3

- Buckets privados (sem acesso público)
- Downloads via **presigned URLs** com expiração de 24h
- Server-side encryption (SSE-S3)

### IAM Principle of Least Privilege

Cada Lambda possui uma role com apenas as permissões necessárias:

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:us-east-1:123456789:api-doc-builder-jobs"
    }
  ]
}
```

---

## 15. Deploy e Infraestrutura

### Pré-requisitos

- AWS CLI configurado com permissões de admin
- AWS SAM CLI >= 1.88
- Python >= 3.11
- Node.js >= 18 (para UI)
- Chave de API do Firecrawl (https://firecrawl.dev)
- Chave de API da OpenAI

### Deploy da Plataforma

```bash
# 1. Clonar o repositório
git clone https://github.com/org/api-doc-builder
cd api-doc-builder

# 2. Criar ambiente virtual Python
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instalar dependências Python
pip install -r requirements.txt

# 4. Instalar dependências Node.js
npm install

# 5. Configurar variáveis de ambiente
cp .env.example .env
# editar .env com suas chaves (FIRECRAWL_API_KEY, OPENAI_API_KEY)

# 6. Build da aplicação Python
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 7. Deploy da infraestrutura AWS (SAM)
sam build
sam deploy --guided

# 8. Deploy da UI
cd apps/web
npm run build
# deploy no Vercel, Amplify, ou S3+CloudFront
```

### Deploy SAM Detalhado

```bash
# Configuração inicial SAM
sam init --name api-doc-builder --runtime python3.11
cd api-doc-builder

# Deploy com configuração
sam deploy \
  --template-file infrastructure/template.yaml \
  --stack-name api-doc-builder-prod \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --parameter-overrides \
    Environment=prod \
    FirecrawlApiKey=$FIRECRAWL_API_KEY \
    OpenAiApiKey=$OPENAI_API_KEY

# Verificar outputs
aws cloudformation describe-stacks \
  --stack-name api-doc-builder-prod \
  --query 'Stacks[0].Outputs'
```

### Ambientes

| Ambiente | Branch | URL | Notas |
|---|---|---|---|
| **dev** | `develop` | `dev.api-doc-builder.com` | Firecrawl sandbox key |
| **staging** | `staging` | `staging.api-doc-builder.com` | Produção espelho |
| **prod** | `main` | `api-doc-builder.com` | Rate limits reais |

---

## 16. Custos AWS Estimados

### Custos por Projeto Gerado (Free Tier)

Para um usuário típico com Free Tier AWS:

| Serviço | Utilização | Custo Mensal |
|---------|------------|--------------|
| **Lambda** | 100 execuções, 1s cada | **$0.00** |
| **SQS** | 10.000 mensagens | **$0.00** |
| **SNS** | 1.000 notificações | **$0.00** |
| **DynamoDB** | 1GB armazenamento | **$0.00** |
| **S3** | 100MB outputs | **$0.00** |
| **API Gateway** | 50.000 req | **$0.00** |
| **TOTAL** | | **$0.00** |

### Custos Além do Free Tier

| Serviço | Beyond Free Tier | Preço |
|---------|-----------------|-------|
| **Lambda** | >400K GB-seg/mês | $0.0000166667/GB-s |
| **Lambda** | >1M req/mês | $0.20/1M |
| **SQS** | >1M req/mês | $0.40/1M |
| **SNS** | >1M publishes | $0.50/1M |
| **DynamoDB** | >25GB | $0.25/GB |
| **S3** | >5GB | $0.023/GB |
| **API Gateway** | >50K req | $3.50/1M |

### Custos da Plataforma (Operação)

Para operar a plataforma (não os projetos gerados):

| Componente | Estimativa | Custo Mensal |
|------------|------------|--------------|
| **Backend API (Lambda)** | 500K invocations | ~$0.50 |
| **DynamoDB** | 1GB, 100K WCU | ~$5.00 |
| **S3** | 1GB storage | ~$0.023 |
| **CloudWatch Logs** | 10GB | ~$0.50 |
| **API Gateway** | 100K req | ~$0.35 |
| **TOTAL Plataforma** | | **~$6.37/mês** |

### Estimativa para 100 Usuários Ativos

| Cenário | Gerações/mês | Custo AWS |
|---------|--------------|-----------|
| **Pessimista** | 1.000 | ~$15-20/mês |
| **Realista** | 500 | ~$8-10/mês |
| **Otimista** | 200 | ~$3-5/mês |

### Dicas para Reduzir Custos

1. **Lambda**: Definir timeout adequado (evitar 300s desnecessários)
2. **SQS**: Usar batching para enviar múltiplas mensagens
3. **DynamoDB**: Modo on-demand para cargas variáveis
4. **S3**: Lifecycle policies para limpar outputs antigos
5. **CloudWatch**: Configurar retenção de logs (7 dias para dev)

### Custo por Tipo de Lambda Gerada

| Tipo | Serviços | Estimativa/mês |
|------|----------|----------------|
| **Webhook Receiver** | Lambda + SQS + API GW | ~$0.05 |
| **Event Processor** | Lambda + DynamoDB | ~$0.03 |
| **Notifier** | Lambda + SNS | ~$0.02 |
| **Full Stack** | Lambda + SQS + SNS + DynamoDB | ~$0.10 |

---

## 17. Roadmap

### v1.0 (MVP) - **Corrente**

- [x] Backend Python/FastAPI
- [x] Chat UI conversacional (React/Next.js)
- [x] Upload de arquivo Markdown
- [x] Integração com Firecrawl para URLs
- [x] Geração de Lambda Python + SQS
- [x] Download do artefato (.zip)
- [x] AWS SAM para IaC

### v1.1

- [ ] Suporte a OpenAPI / Swagger (além de Markdown)
- [ ] Suporte a EventBridge além de SQS/SNS
- [ ] Preview do código no chat antes do download
- [ ] Histórico de projetos na UI
- [ ] Autenticação via Cognito

### v1.2

- [ ] Deploy direto na conta AWS do usuário (via OIDC)
- [ ] Suporte a DynamoDB e S3
- [ ] Templates customizáveis por time
- [ ] Notificações SNS por email

### v2.0

- [ ] SDK público Python para integração programática
- [ ] Planos de assinatura (Free / Pro / Enterprise)
- [ ] Marketplace de templates de integração
- [ ] Dashboard de métricas e custos

---

*Documentação atualizada em 2026-04-05 — API Doc Builder v1.0.0*
*Stack: Python/FastAPI | React/Next.js | AWS SAM | OpenAI GPT-4 | boto3*