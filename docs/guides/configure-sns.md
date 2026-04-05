# Configurar SNS

Como configurar e usar Amazon SNS nas Lambdas geradas.

## O que é SNS?

Amazon Simple Notification Service (SNS) é um serviço de pub/sub que permite enviar notificações para múltiplos assinantes (Lambda, SQS, HTTP, Email, SMS).

## Arquitetura Típica

```
┌─────────────┐
│   Lambda    │───publish──▶ SNS Topic ───▶ Multiplos subscribers
└─────────────┘              │
                             ├──▶ Lambda
                             ├──▶ SQS Queue
                             ├──▶ HTTP Endpoint
                             └──▶ Email
```

## Configuração Inicial

### Via CloudFormation

```yaml
Resources:
  NotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: my-project-notifications
      DisplayName: My Project Notifications
      Subscription:
        - Protocol: lambda
          Endpoint: !GetAtt MyFunction.Arn
  
  LambdaPermission:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref NotificationTopic
      Protocol: lambda
      Endpoint: !GetAtt MyFunction.Arn
```

## Publicar Mensagens

### Publicação Básica

```python
import boto3
import json

sns = boto3.client('sns')

def publish_notification(topic_arn, message):
    response = sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        Subject='Notification from Lambda',
        MessageAttributes={
            'priority': {
                'DataType': 'String',
                'StringValue': 'normal'
            }
        }
    )
    return response['MessageId']
```

### Publicação com JSON Estruturado

```python
def publish_order_update(topic_arn, order_id, status, items):
    message = {
        'order_id': order_id,
        'status': status,
        'items': items,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    response = sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        Subject=f'Order {order_id} - {status}',
        MessageStructure='json'
    )
    return response['MessageId']
```

### Publicação para Múltiplos Tópicos (Fanout)

```python
def publish_fanout(event, topics):
    published = []
    
    for topic_arn in topics:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(event),
            Subject='New Event'
        )
        published.append({
            'topic': topic_arn,
            'message_id': response['MessageId']
        })
    
    return published
```

## Receber Notificações (Lambda Trigger)

```python
def lambda_handler(event, context):
    for record in event['Records']:
        if 'Sns' in record:
            sns_message = json.loads(record['Sns']['Message'])
            topic_arn = record['Sns']['TopicArn']
            subject = record['Sns']['Subject']
            
            print(f"Received from {topic_arn}: {sns_message}")
            
            # Processar mensagem
            process_notification(sns_message)
    
    return {'statusCode': 200}

def process_notification(message):
    # Implementar lógica de processamento
    pass
```

## SNS + SQS (Fanout Pattern)

```python
# Setup - SNS para múltiplas filas
def setup_fanout():
    # Tópico SNS
    topic = sns.create_topic(Name='order-events')
    topic_arn = topic['TopicArn']
    
    # Filas SQS
    queue_analytics = sqs.create_queue(
        QueueName='order-analytics-queue',
        Attributes={
            'VisibilityTimeout': '60',
            'MessageRetentionPeriod': '86400'
        }
    )
    
    queue_notifications = sqs.create_queue(
        QueueName='order-notifications-queue'
    )
    
    # Inscreve filas no tópico
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_analytics['QueueUrl']
    )
    
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_notifications['QueueUrl']
    )
```

## Message Filtering

```python
# Publicar com atributos para filtragem
sns.publish(
    TopicArn=topic_arn,
    Message=json.dumps(payload),
    MessageAttributes={
        'event_type': {
            'DataType': 'String',
            'StringValue': 'order.created'
        },
        'severity': {
            'DataType': 'String',
            'StringValue': 'high'
        }
    }
)
```

## Best Practices

### Idempotência

```python
import hashlib

def publish_idempotent(topic_arn, payload, idempotency_key):
    message_id = hashlib.md5(
        f"{topic_arn}:{idempotency_key}".encode()
    ).hexdigest()
    
    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({**payload, 'message_id': message_id}),
        MessageDeduplicationId=message_id
    )
```

### Error Handling

```python
import botocore

def safe_publish(topic_arn, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message)
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                import time
                time.sleep(2 ** attempt)
            else:
                raise
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## Custo

| Operações | Preço |
|-----------|-------|
| Publicação | $0.50 por 1M |
| Assinaturas | Gratuito |
| Transferência | $0.09/GB |

## Próximos Passos

- [Configurar SQS](./configure-sqs.md) - Filas de mensagens
- [Configurar EventBridge](./configure-eventbridge.md) - Event-driven
