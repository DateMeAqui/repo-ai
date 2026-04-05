# API REST

Referência completa dos endpoints REST.

## Base URL

```
http://localhost:8000/api/v1
```

## Autenticação

Adicione o header `X-API-Key` em todas as requisições:

```bash
curl -H "X-API-Key: sua-chave-api" \
  http://localhost:8000/api/v1/status
```

## Endpoints

### POST `/generate-lambda`

Gera código Lambda a partir de documentação.

**Request**

```json
{
  "documentation": "string (OpenAPI JSON/YAML ou Postman Collection)",
  "documentation_format": "openapi_json | openapi_yaml | postman | openapi_url",
  "prompt": "string (instruções opcionais)",
  "project_name": "string (nome do projeto)"
}
```

**Response** `200 OK`

```json
{
  "project_name": "pet-finder",
  "lambda_handler": "handler.lambda_handler",
  "path": "temp/pet-finder/handler.py",
  "files": [
    "handler.py",
    "requirements.txt",
    "template.yaml",
    "config.py",
    "README.md"
  ],
  "endpoints_generated": [
    "GET /pets",
    "POST /pets",
    "GET /pets/{petId}"
  ],
  "services_configured": ["lambda", "sns"]
}
```

**Error Response** `400 Bad Request`

```json
{
  "error": "invalid_documentation",
  "message": "OpenAPI specification is invalid",
  "details": {
    "line": 42,
    "field": "paths./pets.get.responses"
  }
}
```

---

### POST `/deploy`

Faz deploy do projeto para AWS.

**Request**

```json
{
  "project_name": "pet-finder",
  "environment": "dev | staging | prod",
  "lambda_settings": {
    "memory": 256,
    "timeout": 30,
    "runtime": "python3.11"
  }
}
```

**Response** `200 OK`

```json
{
  "project_name": "pet-finder",
  "status": "deployed",
  "region": "us-east-1",
  "resources": {
    "lambda": "arn:aws:lambda:us-east-1:123456:function:pet-finder",
    "api_gateway": "https://abc123.execute-api.us-east-1.amazonaws.com/prod"
  },
  "deployment_id": "dep-abc123"
}
```

---

### GET `/status/{job_id}`

Retorna status de uma operação.

**Response** `200 OK`

```json
{
  "job_id": "job-123",
  "status": "completed | pending | failed",
  "progress": 100,
  "result": { ... },
  "error": null
}
```

---

### POST `/docs/upload`

Faz upload de arquivo de documentação.

**Request** `multipart/form-data`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `file` | file | Arquivo OpenAPI/Postman |
| `project_name` | string | Nome do projeto |

**Response** `200 OK`

```json
{
  "file_id": "file-abc123",
  "filename": "swagger.json",
  "format": "openapi_json",
  "endpoints_found": 15,
  "parsed_successfully": true
}
```

---

### GET `/projects`

Lista projetos gerados.

**Query Parameters**

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| `limit` | int | 20 | Máximo de resultados |
| `offset` | int | 0 | Paginação |

**Response** `200 OK`

```json
{
  "projects": [
    {
      "name": "pet-finder",
      "created_at": "2024-01-15T10:30:00Z",
      "last_modified": "2024-01-15T14:00:00Z",
      "status": "deployed"
    }
  ],
  "total": 5
}
```

---

### GET `/projects/{project_name}`

Detalhes de um projeto.

**Response** `200 OK`

```json
{
  "name": "pet-finder",
  "created_at": "2024-01-15T10:30:00Z",
  "documentation": {
    "format": "openapi_json",
    "source": "upload"
  },
  "files": ["handler.py", "requirements.txt"],
  "lambda_config": {
    "memory": 256,
    "timeout": 30,
    "runtime": "python3.11"
  },
  "aws_resources": {
    "lambda_arn": "arn:aws:lambda:...",
    "sns_topics": ["pet-finder-notifications"]
  }
}
```

---

### DELETE `/projects/{project_name}`

Remove um projeto.

**Response** `204 No Content`

---

### GET `/health`

Health check.

**Response** `200 OK`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "openai": "connected",
    "aws": "connected"
  }
}
```

## Códigos de Erro

| Código | Significado |
|--------|-------------|
| `400` | Requisição inválida |
| `401` | API key inválida |
| `404` | Recurso não encontrado |
| `429` | Rate limit excedido |
| `500` | Erro interno do servidor |
| `503` | Serviço AWS indisponível |

## Rate Limits

| Plano | Limite |
|-------|--------|
| Free | 10 requests/min |
| Pro | 100 requests/min |
| Enterprise | Unlimited |
