# Configuração

Como configurar credenciais AWS e opções da aplicação.

## Credenciais AWS

### Variáveis de Ambiente (Recomendado)

```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="us-east-1"
```

### Arquivo `~/.aws/credentials`

```ini
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[lambda-generator]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### AWS CLI

```bash
aws configure
aws configure set region us-east-1 --profile lambda-generator
```

## Arquivo de Configuração

Crie `config.yaml` no diretório do projeto:

```yaml
aws:
  region: us-east-1
  profile: default
  runtime: python3.11
  memory: 256
  timeout: 30

firecrawl:
  api_key: "fc-..."  # Opcional
  timeout: 60

openai:
  api_key: "sk-..."
  model: "gpt-4-turbo-preview"
  temperature: 0.7

storage:
  temp_dir: "./temp"
  cleanup_after_deploy: true

server:
  host: "0.0.0.0"
  port: 8000
  debug: false
```

## Configuração via `.env`

```bash
# .env
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

OPENAI_API_KEY=sk-...

FIRECRAWL_API_KEY=fc-...

LOG_LEVEL=INFO
```

## Permissões IAM Necessárias

A função AWS usada precisa ter:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:ListFunctions",
        "lambda:DeleteFunction"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole"
      ],
      "Resource": "arn:aws:iam::*:role/lambda-generator-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:CreateTopic",
        "sns:Subscribe",
        "sns:Publish"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:CreateQueue",
        "sqs:SendMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "*"
    }
  ]
}
```

## Validação

```bash
lambda-generator-api verify
```

Saída esperada:

```
✓ AWS credentials valid (us-east-1)
✓ IAM permissions OK
✓ SNS permissions OK
✓ SQS permissions OK
✓ OpenAI API key valid
```

## Ambientes Múltiplos

```bash
# Desenvolvimento
lambda-generator-api serve --env dev

# Staging
lambda-generator-api serve --env staging

# Produção
lambda-generator-api serve --env prod --config config.prod.yaml
```
