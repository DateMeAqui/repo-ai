# Quickstart

Crie sua primeira Lambda AWS em 5 minutos.

## Pré-requisitos

- Python 3.10+
- Conta AWS com credenciais configuradas
- Docker (para builds locais)

## 1. Instalação Rápida

```bash
pip install lambda-generator-api
```

## 2. Configure Credenciais

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
```

## 3. Inicie a API

```bash
lambda-generator-api serve
# ou via Python
python -m lambda_generator.main
```

A API estará disponível em `http://localhost:8000`.

## 4. Acesse a Interface de Chat

1. Abra `http://localhost:8000/docs`
2. Vá para **WebSocket** > `/ws/chat/{session_id}`
3. Conecte e envie mensagens

## 5. Crie sua Primeira Lambda

### Via WebSocket

Conecte ao WebSocket e envie:

```json
{
  "type": "message",
  "content": "Crie uma Lambda que busca produtos do catálogo usando este OpenAPI: [cole o JSON ou URL aqui]"
}
```

### Via REST API

```bash
curl -X POST http://localhost:8000/api/v1/generate-lambda \
  -H "Content-Type: application/json" \
  -d '{
    "documentation": "https://petstore.swagger.io/v2/swagger.json",
    "documentation_format": "openapi_url",
    "prompt": "Crie uma lambda que busca a lista de pets",
    "project_name": "pet-finder"
  }'
```

## 6. Faça Deploy

```bash
cd temp/pet-finder
lambda-generator-api deploy --service pet-finder
```

## Próximos Passos

- [Instalação Detalhada](./installation.md) - Mais opções de setup
- [Interface de Chat](./guides/chat-interface.md) - Como usar o chat
- [Upload de Documentação](./guides/upload-documentation.md) - Upload de arquivos
