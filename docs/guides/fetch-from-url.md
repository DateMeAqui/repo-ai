# Buscar Documentação de URL

Como usar Firecrawl para extrair documentação de sites e URLs.

## O que é Firecrawl?

[Firecrawl](https://docs.firecrawl.dev) é um serviço que transforma sites em dados estruturados (Markdown, JSON), ideal para extrair documentação de APIs de páginas web.

## Uso Básico

### Via API REST

```bash
curl -X POST http://localhost:8000/api/v1/generate-lambda \
  -H "Content-Type: application/json" \
  -d '{
    "documentation": "https://api.example.com/docs",
    "documentation_format": "openapi_url",
    "prompt": "Crie uma Lambda para integrar com esta API",
    "project_name": "example-integration"
  }'
```

### Via WebSocket

```python
ws.send(json.dumps({
    "type": "message",
    "content": "Crie uma Lambda para buscar previsão do tempo",
    "metadata": {
        "documentation_url": "https://openweathermap.org/api",
        "documentation_format": "openapi_url"
    }
}))
```

## Configuração

### API Key (Opcional)

```bash
export FIRECRAWL_API_KEY="fc-..."
```

Sem API key: uso limitado a 100 requests/dia.

### Opções de Fetch

```yaml
firecrawl:
  api_key: "fc-..."
  timeout: 60
  max_depth: 2
  page_options:
    only_main_content: true
    remove_special_elements: true
```

## URLs Suportadas

| Tipo | Exemplo |
|------|---------|
| OpenAPI hosted | `https://petstore.swagger.io/v2/swagger.json` |
| Páginas de documentação | `https://docs.example.com/api` |
| GitHub raw files | `https://raw.githubusercontent.com/.../openapi.yaml` |
| Postman docs | `https://documenter.getpostman.com/...` |
| ReadMe.io | `https://api.example.com/docs` |
| ReadTheDocs | `https://example.readthedocs.io/en/latest/` |

## Fluxo

```
1. URL recebida
   │
   ▼
2. Firecrawl fetch
   ├── Sucesso → Extrai Markdown/OpenAPI
   │              │
   │              ▼
   │           3. Parser processa
   │              │
   │              ▼
   │           4. Gera Lambda
   │
   └── Falha → Tenta alternativas
               ├── Try: /openapi.json
               ├── Try: /swagger.json
               └── Fallback: Erro usuário
```

## Exemplos

### OpenAPI Online

```python
# Stripe API
url = "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"

ws.send(json.dumps({
    "type": "message",
    "content": "Crie uma Lambda para processar pagamentos Stripe",
    "metadata": {
        "documentation_url": url,
        "documentation_format": "openapi_url"
    }
}))
```

### Documentação Web

```python
# Weather API com docs web
url = "https://openweathermap.org/api"

ws.send(json.dumps({
    "type": "message",
    "content": """
    Crie uma Lambda que busca previsão do tempo.
    A documentação está em: https://openweathermap.org/api
    """,
    "metadata": {
        "documentation_url": url,
        "documentation_format": "openapi_url"
    }
}))
```

## Tratamento de Erros

| Erro | Causa | Solução |
|------|-------|---------|
| `url_not_found` | 404 | Verifique a URL |
| `fetch_timeout` | Timeout | Tente URL mais específica |
| `parse_error` | Conteúdo inválido | Use URL direta do JSON |
| `rate_limited` | Firecrawl limit | Use API key ou tente depois |

## Boas Práticas

1. **Prefira URLs diretas** para OpenAPI JSON/YAML
2. **Timeout**: Aumente para páginas lentas
3. **Cache**: Firecrawl pode cachear docs fetched
4. **Fallback**: Tenha arquivo local como backup

## Alternativa: Download Manual

Se Firecrawl falhar:

```bash
# Baixar manualmente
curl -O https://petstore.swagger.io/v2/swagger.json

# E usar via upload
curl -X POST http://localhost:8000/api/v1/docs/upload \
  -F "file=@swagger.json" \
  -F "project_name=pet-store"
```
