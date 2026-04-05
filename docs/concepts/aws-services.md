# AWS Lambda Services

Visão geral dos serviços AWS disponíveis para Lambdas geradas.

## Lambda

Função serverless principal.

```yaml
# template.yaml
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-lambda
      Runtime: python3.11
      Handler: handler.lambda_handler
      MemorySize: 256
      Timeout: 30
      CodeUri: ./
      Environment:
        Variables:
          ENV: !Ref Environment
      Policies:
        - AWSLambdaBasicExecutionRole
```

## Amazon SNS

Simple Notification Service - Pub/Sub.

```python
import boto3

sns = boto3.client('sns')

def publish_notification(topic_arn, message, subject="Notification"):
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject,
        MessageAttributes={
            'priority': {
                'DataType': 'String',
                'StringValue': 'normal'
            }
        }
    )
    return response['MessageId']
```

### Configuração na Lambda

```python
class SNSConfig:
    def __init__(self):
        self.client = boto3.client('sns')
    
    def create_topic(self, name):
        return self.client.create_topic(Name=name)
    
    def subscribe(self, topic_arn, protocol, endpoint):
        return self.client.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,
            Endpoint=endpoint
        )
```

## Amazon SQS

Simple Queue Service - Filas de mensagens.

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

def receive_messages(queue_url, max_messages=10):
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=20
    )
    return response.get('Messages', [])
```

### SQS como Trigger

```yaml
Resources:
  MyQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: my-queue
      VisibilityTimeout: 30
      MessageRetentionPeriod: 345600
  
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      # ...
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !GetAtt MyQueue.Arn
            BatchSize: 10
```

## Amazon EventBridge

Event-driven rules e event bus.

```python
import boto3
from datetime import datetime

events = boto3.client('events')

def put_rule(name, schedule_expression):
    return events.put_rule(
        Name=name,
        ScheduleExpression=schedule_expression,  # cron(0 * * * ? *) ou rate(5 minutes)
        State='ENABLED',
        Description=f'Rule: {name}'
    )

def add_target(rule_name, lambda_arn):
    events.put_targets(
        Rule=rule_name,
        Targets=[{
            'Id': '1',
            'Arn': lambda_arn,
            'Input': '{}'
        }]
    )
```

### EventBridge como Trigger

```yaml
Resources:
  MyRule:
    Type: AWS::Events::Rule
    Properties:
      Name: my-scheduled-rule
      ScheduleExpression: rate(1 day)
      Targets:
        - Id: MyLambdaTarget
          Arn: !GetAtt MyFunction.Arn

  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      # ...
      Events:
        EventBridgeTrigger:
          Type: EventBridge::Rule
          Properties:
            RuleName: my-scheduled-rule
```

## Amazon DynamoDB

Banco de dados NoSQL serverless.

```python
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')

def put_item(item):
    return table.put_item(Item=item)

def get_item(key):
    response = table.get_item(Key=key)
    return response.get('Item')

def query_items(index_name, key_condition, expression_values):
    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=key_condition,
        ExpressionAttributeValues=expression_values
    )
    return response.get('Items', [])
```

### DynamoDB Stream como Trigger

```yaml
Resources:
  MyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: my-table
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
  
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      # ...
      Events:
        DynamoDBTrigger:
          Type: DynamoDB
          Properties:
            StartingPosition: LATEST
            Stream:
              !GetAtt MyTable.StreamArn
```

## API Gateway

Expor Lambda como HTTP API.

```yaml
Resources:
  MyApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: my-api
      ProtocolType: HTTP
  
  MyIntegration:
    Type: AWS::ApiGatewayV2::Integration
    Properties:
      ApiId: !Ref MyApi
      IntegrationType: AWS_PROXY
      IntegrationUri: !GetAtt MyFunction.Arn
  
  MyRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref MyApi
      RouteKey: ANY /{proxy+}
      Target: !Join /, ['integrations', !Ref MyIntegration]
```

## Custo Estimado

| Serviço | Free Tier | Pay-per-use |
|---------|-----------|-------------|
| Lambda | 400K GB-seg | $0.0000166667/GB-s |
| SNS | 1M publishes | $0.50/1M |
| SQS | 1M requests | $0.40/1M |
| DynamoDB | 25 GB | $0.25/GB |
| EventBridge | 1M events | $1.00/1M events |
