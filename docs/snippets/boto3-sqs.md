# Snippets boto3 - SQS

Exemplos de código boto3 para Amazon SQS.

## Cliente

```python
import boto3

sqs = boto3.client('sqs')
sqs_resource = boto3.resource('sqs')
```

## Criar Fila

```python
# Fila padrão
response = sqs.create_queue(
    QueueName='my-queue',
    Tags={'Environment': 'production'}
)

# FIFO
response = sqs.create_queue(
    QueueName='my-queue.fifo',
    Attributes={
        'FifoQueue': 'true',
        'ContentBasedDeduplication': 'true'
    }
)

queue_url = response['QueueUrl']
```

## Enviar Mensagens

```python
# Envio simples
response = sqs.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    MessageBody='Hello, World!',
    DelaySeconds=0
)
message_id = response['MessageId']

# Com atributos
sqs.send_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    MessageBody=json.dumps({'order_id': '123'}),
    MessageAttributes={
        'priority': {
            'StringValue': 'high',
            'DataType': 'String'
        }
    }
)

# Batch (até 10)
response = sqs.send_message_batch(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    Entries=[
        {'Id': '1', 'MessageBody': 'Message 1'},
        {'Id': '2', 'MessageBody': 'Message 2'},
        {'Id': '3', 'MessageBody': 'Message 3'}
    ]
)
```

## Receber Mensagens

```python
# Receber
response = sqs.receive_message(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,
    VisibilityTimeout=30,
    MessageAttributeNames=['All']
)

messages = response.get('Messages', [])

for message in messages:
    body = message['Body']
    receipt = message['ReceiptHandle']
    msg_id = message['MessageId']
    
    # Processar...
    
    # Deletar após processar
    sqs.delete_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
        ReceiptHandle=receipt
    )
```

## Dead Letter Queue

```python
# Criar DLQ
dlq_response = sqs.create_queue(
    QueueName='my-queue-dlq.fifo',
    Attributes={
        'FifoQueue': 'true',
        'ContentBasedDeduplication': 'true'
    }
)

# Configurar DLQ na fila principal
sqs.set_queue_attributes(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    Attributes={
        'RedrivePolicy': json.dumps({
            'deadLetterTargetArn': f'arn:aws:sqs:us-east-1:123456:my-queue-dlq',
            'maxReceiveCount': '3'
        })
    }
)
```

## Purge (Limpar Fila)

```python
sqs.purge_queue(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue'
)
```

## Atributos da Fila

```python
# Obter URL
queue_url = sqs.get_queue_url(QueueName='my-queue')['QueueUrl']

# Atributos
response = sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['All']
)
attributes = response['Attributes']
print(f"Messages: {attributes['ApproximateNumberOfMessages']}")
print(f"Visibility: {attributes['VisibilityTimeout']}")
```

## Manipulação de Mensagens

```python
# Change message visibility (extender timeout)
sqs.change_message_visibility(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    ReceiptHandle=receipt_handle,
    VisibilityTimeout=60
)

# Change multiple
sqs.change_message_visibility_batch(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/123456/my-queue',
    Entries=[
        {'Id': '1', 'ReceiptHandle': 'handle1', 'VisibilityTimeout': 60},
        {'Id': '2', 'ReceiptHandle': 'handle2', 'VisibilityTimeout': 60}
    ]
)
```

## Listar e Deletar

```python
# Listar filas
response = sqs.list_queues(QueueNamePrefix='my-')
for url in response['QueueUrls']:
    print(url)

# Listar com tags
response = sqs.list_queue_tags(QueueUrl=queue_url)

# Tagging
sqs.tag_queue(
    QueueUrl=queue_url,
    Tags={'Environment': 'production', 'Team': 'platform'}
)

# Delete queue
sqs.delete_queue(QueueUrl=queue_url)
```

## SQS como Resource (Orientado a Objetos)

```python
queue = sqs_resource.Queue('my-queue')

# Enviar
queue.send_message(MessageBody='Hello')

# Receber
for message in queue.receive_messages(MaxNumberOfMessages=10):
    print(message.body)
    message.delete()

# Atributos
print(queue.attributes['ApproximateNumberOfMessages'])
```

## Lambda SQS Trigger Example

```python
import json

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            process_message(message)
            
            # Deletar manualmente se necessário
            # sqs.delete_message(
            #     QueueUrl=record['eventSourceARN'],
            #     ReceiptHandle=record['receiptHandle']
            # )
        except Exception as e:
            print(f"Error: {e}")
            raise  # Não deleta, volta para fila
    
    return {'statusCode': 200}

def process_message(message):
    print(f"Processing: {message}")
```
