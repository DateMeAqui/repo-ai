# Upload de Documentação

Como fazer upload de documentação OpenAPI ou Postman.

## Formatos Suportados

| Formato | Extensões | Descrição |
|---------|-----------|-----------|
| OpenAPI JSON | `.json` | OpenAPI 3.0/3.1 em JSON |
| OpenAPI YAML | `.yaml`, `.yml` | OpenAPI 3.0/3.1 em YAML |
| Swagger | `.json` | Swagger 2.0 |
| Postman | `.json` | Postman Collection v2.1 |

## Via REST API

### Upload de Arquivo

```bash
curl -X POST http://localhost:8000/api/v1/docs/upload \
  -H "X-API-Key: sua-chave" \
  -F "file=@./swagger.json" \
  -F "project_name=my-api"
```

### Response

```json
{
  "file_id": "file-abc123",
  "filename": "swagger.json",
  "format": "openapi_json",
  "endpoints_found": 15,
  "operations": [
    "GET /products",
    "POST /products",
    "GET /products/{id}",
    "PUT /products/{id}",
    "DELETE /products/{id}"
  ],
  "parsed_successfully": true
}
```

## Via WebSocket

### Enviar Documentação Base64

```python
import base64
import json

with open("swagger.json", "rb") as f:
    content = base64.b64encode(f.read()).decode()

ws.send(json.dumps({
    "type": "upload",
    "filename": "swagger.json",
    "content": content,
    "format": "openapi_json",
    "project_name": "my-api"
}))
```

### Inline no Chat

```python
ws.send(json.dumps({
    "type": "message",
    "content": "Crie uma Lambda usando esta documentação:",
    "metadata": {
        "documentation": openapi_json_string,
        "documentation_format": "openapi_json"
    }
}))
```

## Exemplo: OpenAPI 3.0

```json
{
  "openapi": "3.0.3",
  "info": {
    "title": "Product API",
    "version": "1.0.0"
  },
  "paths": {
    "/products": {
      "get": {
        "summary": "List products",
        "operationId": "listProducts",
        "responses": {
          "200": {
            "description": "A list of products",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": { "$ref": "#/components/schemas/Product" }
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Product": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" },
          "price": { "type": "number" }
        }
      }
    }
  }
}
```

## Exemplo: Postman Collection

```json
{
  "info": {
    "name": "Product API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "List Products",
      "request": {
        "method": "GET",
        "url": "https://api.example.com/products",
        "header": []
      }
    },
    {
      "name": "Create Product",
      "request": {
        "method": "POST",
        "url": "https://api.example.com/products",
        "header": [
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{ \"name\": \"Product\", \"price\": 9.99 }"
        }
      }
    }
  ]
}
```

## Validação

O parser valida automaticamente:

- Estrutura válida do formato
- Endpoints reconhecíveis
- Schemas bem formados
- Segurança (se presente)

### Erros Comuns

| Erro | Solução |
|------|---------|
| `invalid_json` | Verifique se o JSON é válido |
| `invalid_openapi` | Use OpenAPI 3.0+ |
| `no_paths_found` | Adicione `paths` ao spec |
| `unsupported_version` | Use Swagger 2.0 ou OpenAPI 3.0+ |

## Dicas

1. **Valide antes**: Use [Swagger Editor](https://editor.swagger.io/) para validar
2. **Simplifique**: Remova paths desnecessários
3. **Schemas**: Defina schemas para melhor geração de código
4. **Segurança**: Mantenha credenciais fora do spec
