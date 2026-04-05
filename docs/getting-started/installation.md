# Instalação

Guia completo de instalação do Lambda Generator API.

## Requisitos

- Python 3.10, 3.11 ou 3.12
- AWS Account com permissões adequadas
- Docker (opcional, para builds locais)
- Git

## Instalação via pip

```bash
pip install lambda-generator-api
```

## Instalação do Código Fonte

```bash
git clone <repo-url>
cd lambda-generator-api
pip install -e .
```

## Dependências

### Core

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
pydantic>=2.0.0
httpx>=0.25.0
```

### AWS

```txt
boto3>=1.28.0
botocore>=1.31.0
```

### AI/ML

```txt
openai>=1.0.0
```

### Parsers

```txt
pyyaml>=6.0
openapi-spec-validator>=0.6.0
postman-to-openapi>=1.8.0
```

### Firecrawl

```txt
firecrawl-py>=0.1.0
```

## Ambiente Virtual (Recomendado)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

pip install lambda-generator-api
```

## Instalação com Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t lambda-generator .
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  lambda-generator
```

## Verificação da Instalação

```bash
lambda-generator-api --version
# lambda-generator-api 1.0.0

lambda-generator-api serve --check
# ✓ Configurações válidas
# ✓ Credenciais AWS conectadas
# ✓ Pronto para uso
```

## Problemas Comuns

### `ModuleNotFoundError`

```bash
pip install --upgrade pip
pip install -e .
```

### Credenciais AWS inválidas

```bash
aws configure
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region: us-east-1
```

### Porta em uso

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```
