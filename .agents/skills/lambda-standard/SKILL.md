# Skill: lambda-standard

Gera código lambda Python no padrão API Gateway a partir de documentação de API externa e prompt de lógica.

## Entrada

```yaml
- documentation: string      # OpenAPI JSON/YAML ou Postman Collection
- documentation_format: openapi_json | openapi_yaml | postman
- prompt: string              # Lógica de negócio desejada
- project_name: string        # opcional
```

## Processo

1. Parse da documentação → extrai endpoints disponíveis
2. Prepara contexto com serviços da API externa
3. Aplica template lambda com lógica solicitada
4. Valida sintaxe Python

## Template Base

```python
import json

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    
    # Lógica gerada pelo agent
    
    return {
        "statusCode": 200,
        "body": json.dumps({...})
    }
```

## Output

Código lambda Python pronto para deploy em AWS Lambda com API Gateway.
