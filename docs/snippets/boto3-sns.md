# Snippets boto3 - SNS

Exemplos de código boto3 para Amazon SNS.

## Cliente

```python
import boto3

sns = boto3.client('sns')
sns_resource = boto3.resource('sns')
```

## Criar Tópico

```python
# Criar tópico padrão
response = sns.create_topic(
    Name='my-topic',
    Tags=[
        {'Key': 'Environment', 'Value': 'production'}
    ]
)
topic_arn = response['TopicArn']
```

## Publicar Mensagem

```python
# Publicação simples
response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Message='Hello from Lambda!',
    Subject='Test Message'
)

# Com atributos
sns.publish(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Message=json.dumps({'default': 'Mensagem'}),
    Subject='Subject',
    MessageStructure='json',
    MessageAttributes={
        'priority': {
            'DataType': 'String',
            'StringValue': 'high'
        }
    }
)
```

## Inscrever Assinante

```python
# Lambda
sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Protocol='lambda',
    Endpoint='arn:aws:lambda:us-east-1:123456:function:my-function'
)

# SQS
sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Protocol='sqs',
    Endpoint='arn:aws:sqs:us-east-1:123456:my-queue'
)

# HTTP/HTTPS
sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Protocol='https',
    Endpoint='https://api.example.com/webhook'
)

# Email
sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Protocol='email',
    Endpoint='user@example.com'
)
```

## Filtragem de Mensagens

```python
# Subscription com filtro
sns.subscribe(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic',
    Protocol='lambda',
    Endpoint='arn:aws:lambda:us-east-1:123456:function:my-function',
    FilterPolicyScope='MessageBody',
    FilterPolicy={
        'event_type': ['order.created', 'order.updated'],
        'severity': ['high', 'critical']
    }
)
```

## Listar e Gerenciar

```python
# Listar tópicos
response = sns.list_topics()
for topic in response['Topics']:
    print(topic['TopicArn'])

# Listar subscrições de um tópico
response = sns.list_subscriptions_by_topic(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic'
)
for sub in response['Subscriptions']:
    print(f"{sub['Protocol']}: {sub['Endpoint']}")

# Confirmar subscription (para email/HTTP)
def confirm_subscription(topic_arn, token):
    return sns.confirm_subscription(
        TopicArn=topic_arn,
        Token=token
    )

# Delete subscription
sns.unsubscribe(
    SubscriptionArn='arn:aws:sns:us-east-1:123456:my-topic:abc123'
)
```

## Tags

```python
# Adicionar tag
sns.tag_resource(
    ResourceArn='arn:aws:sns:us-east-1:123456:my-topic',
    Tags=[{'Key': 'team', 'Value': 'platform'}]
)

# Listar tags
response = sns.list_tags_for_resource(
    ResourceArn='arn:aws:sns:us-east-1:123456:my-topic'
)
for tag in response['Tags']:
    print(f"{tag['Key']}: {tag['Value']}")
```

## Plataforma Notifications (Mobile Push)

```python
# Publicar para plataforma
sns.publish(
    TargetArn='arn:aws:sns:us-east-1:123456:endpoint/APNS/my-app/abc',
    Message=json.dumps({
        'APNS': json.dumps({
            'aps': {'alert': 'Hello!' }
        })
    }),
    MessageStructure='json'
)
```

## Batch Publishing (FIFO)

```python
# Publicação em lote para FIFO
response = sns.publish_batch(
    TopicArn='arn:aws:sns:us-east-1:123456:my-topic.fifo',
    PublishBatchRequestEntries=[
        {
            'Id': '1',
            'Message': 'Message 1',
            'MessageGroupId': 'group1'
        },
        {
            'Id': '2',
            'Message': 'Message 2',
            'MessageGroupId': 'group1'
        }
    ]
)
```
