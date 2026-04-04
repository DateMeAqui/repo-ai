# Lambda Generator API

API FastAPI que gera lambdas Python a partir de documentação de APIs externas.

## Endpoint

**POST** `/generate-lambda`

### Request

```json
{
  "documentation": "<conteúdo OpenAPI JSON/YAML ou Postman Collection>",
  "documentation_format": "openapi_json | openapi_yaml | postman",
  "prompt": "Crie uma lambda que busca produtos do catálogo...",
  "project_name": "nome-do-projeto"
}
```

### Response

```json
{
  "project_name": "nome-do-projeto",
  "lambda_handler": "handler.lambda_handler",
  "path": "temp/nome-do-projeto/handler.py",
  "files": ["handler.py", "requirements.txt"]
}
```

## Formatos de Documentação Suportados

| Formato | Descrição |
|---------|------------|
| `openapi_json` | OpenAPI/Swagger em JSON |
| `openapi_yaml` | OpenAPI/Swagger em YAML |
| `postman` | Postman Collection |

## Fluxo

1. Recebe documentação + prompt
2. Parser extrai endpoints disponíveis
3. Agent OpenAI gera código
4. Salva em `temp/projeto-<nome>/`
5. Retorna metadados

## Estrutura do Projeto Gerado

```
temp/<project_name>/
├── handler.py
├── requirements.txt
└── README.md
```

## Template Lambda

```python
import json

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    
    # Lógica gerada
    
    return {
        "statusCode": 200,
        "body": json.dumps({...})
    }
```

## Componentes

| Módulo | Função |
|--------|--------|
| `main.py` | FastAPI app |
| `parsers/` | Parse OpenAPI/Postman |
| `agent/` | Cliente OpenAI |
| `templates/` | Template lambda |
| `storage/` | Gerenciador de arquivos |

## Skill

Usa a skill `lambda-standard` para definição do template.
