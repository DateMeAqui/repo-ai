# Interface de Chat

Como usar a interface de chat estilo LLM para criar Lambdas.

## Conexão

Conecte ao WebSocket em:

```
ws://localhost:8000/ws/chat/{session_id}
```

### Exemplo JavaScript

```javascript
const sessionId = crypto.randomUUID();
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);

ws.onopen = () => {
  console.log('Conectado ao chat');
  
  // Enviar mensagem
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Crie uma Lambda para buscar usuários'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Recebido:', data);
};
```

## Tipos de Mensagem

### Cliente → Servidor

#### `message`

Envia uma mensagem de texto ou com documentação.

```json
{
  "type": "message",
  "content": "Crie uma Lambda que envia notificações via SNS",
  "metadata": {
    "documentation_url": "https://api.example.com/openapi.json",
    "documentation_format": "openapi_url"
  }
}
```

#### `upload`

Upload de arquivo de documentação.

```json
{
  "type": "upload",
  "filename": "swagger.json",
  "content": "base64_encoded_content",
  "format": "openapi_json"
}
```

#### `generate`

Solicita geração direta (sem streaming).

```json
{
  "type": "generate",
  "prompt": "Lambda para processar mensagens SQS",
  "services": ["sqs", "sns"]
}
```

#### `ping`

Mantém conexão viva.

```json
{
  "type": "ping"
}
```

---

### Servidor → Cliente

#### `ack`

Confirmação de receipt.

```json
{
  "type": "ack",
  "message_id": "msg-123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### `streaming`

Chunk de resposta em streaming.

```json
{
  "type": "streaming",
  "content": "Vou criar uma Lambda...",
  "done": false
}
```

#### `message`

Mensagem completa.

```json
{
  "type": "message",
  "role": "assistant",
  "content": "Criei a Lambda com as seguintes configurações...",
  "actions": [
    {
      "type": "code_generated",
      "path": "temp/my-lambda/handler.py"
    },
    {
      "type": "service_added",
      "service": "sns",
      "config": { ... }
    }
  ]
}
```

#### `error`

Erro no processamento.

```json
{
  "type": "error",
  "code": "invalid_documentation",
  "message": "Não foi possível parsear o OpenAPI"
}
```

## Fluxo Completo

```
Cliente                          Servidor
   │                                 │
   │──── connect ──────────────────▶│
   │◀─── connected ────────────────│
   │                                 │
   │──── { type: message, ... } ──▶│
   │◀─── { type: ack } ───────────│
   │◀─── { type: streaming, ... } ─│
   │◀─── { type: streaming, ... } ─│
   │◀─── { type: message, actions }│
   │                                 │
   │──── { type: ping } ──────────▶│
   │◀─── { type: pong } ───────────│
   │                                 │
   │──── disconnect ───────────────▶│
```

## Exemplo Prático

### 1. Conectar

```python
import websocket
import json

ws = websocket.create_connection("ws://localhost:8000/ws/chat/test-session")
```

### 2. Criar Lambda com URL

```python
message = {
    "type": "message",
    "content": """
    Crie uma Lambda Python para gerenciar um catálogo de produtos.
    A API externa tem endpoints para listar, criar e buscar produtos.
    Adicione integração com SNS para notificar sobre novos produtos.
    """,
    "metadata": {
        "documentation_url": "https://petstore.swagger.io/v2/swagger.json",
        "documentation_format": "openapi_url"
    }
}

ws.send(json.dumps(message))
```

### 3. Receber Resposta

```python
while True:
    response = ws.recv()
    data = json.loads(response)
    
    if data["type"] == "streaming":
        print(data["content"], end="")
    elif data["type"] == "message":
        print("\n\nAções:", data.get("actions"))
        break
```

### 4. Fazer Deploy

```python
deploy_msg = {
    "type": "message",
    "content": "Faça deploy do projeto pet-finder para produção"
}
ws.send(json.dumps(deploy_msg))
```

## Interface Web

Acesse `http://localhost:8000/chat` para uma interface visual:

- Editor de código integrado
- Preview do arquivo gerado
- Botões para ações rápidas
- Histórico de sessões

## Rate Limits

- 60 mensagens por minuto por sessão
- Timeout de conexão: 30 minutos
- Max message size: 1MB
