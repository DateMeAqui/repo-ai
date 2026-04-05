# Configurar SQS

Como configurar e usar Amazon SQS nas Lambdas geradas.

## O que é SQS?

Amazon Simple Queue Service (SQS) é um serviço de filas de mensagens gerenciado que permite desacoplar microservices e serverless applications.

## Tipos de Fila

### Standard Queue

- Entrega "at least once"
- Melhor esforço de ordenação
- Throughput ilimitado

### FIFO Queue

- Entrega "exactly once"
- Ordenação garantida (FIFO)
- 300 transactions/second

## Configuração via CloudFormation

```yaml
Resources:
  MyQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: my-project-queue
      VisibilityTimeout: 30
      MessageRetentionPeriod: 345600
      ReceiveMessageWaitTimeSeconds: 20
      RedrivePolicy:
        maxReceiveCount: 3
        deadLetterTargetArn: !GetAtt DeadLetterQueue.Arn
  
  DeadLetterQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: my-project-queue-dlq
```

## Enviar Mensagens

### Envio Básico

```python
import boto3
import json

sqs = boto3.client('sqs')

def send_message(queue_url, message_body):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        DelaySeconds=0
    )
    return response['MessageId']
```

### Envio em Batch (até 10)

```python
def send_messages_batch(queue_url, messages):
    entries = [
        {
            'Id': str(i),
            'MessageBody': json.dumps(msg)
        }
        for i, msg in enumerate(messages)
    ]
    
    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )
    
    return {
        'successful': response['Successful'],
        'failed': response['Failed']
    }
```

### Delayed Message

```python
def send_delayed_message(queue_url, message, delay_seconds=300):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
        DelaySeconds=delay_seconds
    )
    return response['MessageId']
```

## Receber Mensagens

### Receber e Processar

```python
def receive_messages(queue_url, max_messages=10):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=20,
        VisibilityTimeout=30,
        MessageAttributeNames=['All']
    )
    return response.get('Messages', [])
```

### Lambda com SQS Trigger

```python
def lambda_handler(event, context):
    for record in event['Records']:
        message_body = json.loads(record['body'])
        receipt_handle = record['receiptHandle']
        
        try:
            process_message(message_body)
            delete_message(record['queue_url'], receipt_handle)
        except Exception as e:
            print(f"Error processing: {e}")
            # Não deleta - volta para fila
    
    return {'statusCode': 200}

def process_message(message):
    print(f"Processing: {message}")

def delete_message(queue_url, receipt_handle):
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
```

### Processamento Idempotente

```python
import hashlib

processed_ids = set()

def lambda_handler(event, context):
    for record in event['Records']:
        message_id = record['messageId']
        message_body = json.loads(record['body'])
        
        # Verifica se já processou
        if message_id in processed_ids:
            print(f"Skipping duplicate: {message_id}")
            continue
        
        process_message(message_body)
        processed_ids.add(message_id)
    
    return {'statusCode': 200}
```

## Dead Letter Queue

```python
def process_with_dlq(message, max_retries=3):
    try:
        process_message(message)
    except ProcessingError as e:
        # Verifica retry count
        retry_count = message.get('Attributes', {}).get('ApproximateReceiveCount', 0)
        
        if int(retry_count) >= max_retries:
            # Move para DLQ
            send_to_dlq(message, str(e))
        else:
            raise
```

## Long Polling

```python
# Melhor prática - reduz custo e latência
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling (1-20)
    ReceiveMessageWaitTimeSeconds=20
)
```

## Monitoramento

```python
import boto3

def get_queue_metrics(queue_url):
    cloudwatch = boto3.client('cloudwatch')
    
    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/SQS',
        MetricName='ApproximateNumberOfMessagesVisible',
        Dimensions=[{'Name': 'QueueName', 'Value': queue_url.split('/')[-1]}],
        StartTime=datetime.utcnow() - timedelta(hours=1),
        EndTime=datetime.utcnow(),
        Period=300,
        Statistics=['Average']
    )
    
    return metrics['Datapoints']
```

## Custo

| Operação | Preço |
|----------|-------|
| Requests | $0.40 por 1M |
| FIFO (transactions) | $0.50 por 1M |
| Data Transfer | $0.09/GB |

## Best Practices

1. **Use batching** - até 10 mensagens por batch
2. **Long polling** - WaitTimeSeconds=20
3. **Dead letter queue** - para mensagens com falha
4. **Visibility timeout** - 6x tempo médio de processamento
5. **Idempotência** - processar mesma mensagem múltiplas vezes

## Exemplo Completo

```python
import boto3
import json
from datetime import datetime

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456/my-queue'

def lambda_handler(event, context):
    messages = receive_messages(QUEUE_URL)
    
    for msg in messages:
        try:
            data = json.loads(msg['Body'])
            process(data)
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=msg['ReceiptHandle']
            )
        except Exception as e:
            print(f"Failed: {e}")
    
    return {'processed': len(messages)}

def process(data):
    print(f"Processing order: {data['order_id']}")
```

## Próximos Passos

- [Configurar SNS](./configure-sns.md) - Notificações pub/sub
- [Configurar EventBridge](./configure-eventbridge.md) - Event-driven
