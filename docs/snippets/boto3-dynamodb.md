# Snippets boto3 - DynamoDB

Exemplos de código boto3 para Amazon DynamoDB.

## Cliente e Resource

```python
import boto3

# Cliente de baixo nível
dynamodb = boto3.client('dynamodb')

# Resource de alto nível (mais Pythonic)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('my-table')
```

## Criar Tabela

```python
# Tabela simples
dynamodb.create_table(
    TableName='users',
    KeySchema=[
        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'user_id', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'
)

# Tabela com GSI e Provisioned
dynamodb.create_table(
    TableName='orders',
    KeySchema=[
        {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
        {'AttributeName': 'order_id', 'KeyType': 'RANGE'}
    ],
    AttributeDefinitions=[
        {'AttributeName': 'customer_id', 'AttributeType': 'S'},
        {'AttributeName': 'order_id', 'AttributeType': 'S'},
        {'AttributeName': 'status', 'AttributeType': 'S'}
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'status-index',
            'KeySchema': [
                {'AttributeName': 'status', 'KeyType': 'HASH'},
                {'AttributeName': 'customer_id', 'KeyType': 'RANGE'}
            ],
            'Projection': {'ProjectionType': 'ALL'},
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
```

## Operações com Resource

```python
table = dynamodb.Table('users')

# Put item
table.put_item(
    Item={
        'user_id': '123',
        'name': 'John',
        'email': 'john@example.com',
        'age': 30
    }
)

# Get item
response = table.get_item(Key={'user_id': '123'})
user = response.get('Item')

# Update item
table.update_item(
    Key={'user_id': '123'},
    UpdateExpression='SET age = :age, #name = :name',
    ExpressionAttributeNames={'#name': 'name'},
    ExpressionAttributeValues={
        ':age': 31,
        ':name': 'John Updated'
    }
)

# Delete item
table.delete_item(Key={'user_id': '123'})
```

## Operações com Cliente

```python
# Put item
dynamodb.put_item(
    TableName='users',
    Item={
        'user_id': {'S': '123'},
        'name': {'S': 'John'},
        'age': {'N': '30'}
    }
)

# Get item
response = dynamodb.get_item(
    TableName='users',
    Key={'user_id': {'S': '123'}}
)
item = response.get('Item')

# Update com condicional
dynamodb.update_item(
    TableName='users',
    Key={'user_id': {'S': '123'}},
    UpdateExpression='SET age = :new_age',
    ConditionExpression='age < :new_age',
    ExpressionAttributeValues={
        ':new_age': {'N': '31'},
        ':current_age': {'N': '30'}
    }
)
```

## Batch Operations

```python
# Batch write (até 25 items)
with table.batch_writer() as batch:
    batch.put_item(Item={'user_id': '1', 'name': 'User 1'})
    batch.put_item(Item={'user_id': '2', 'name': 'User 2'})
    batch.delete_item(Key={'user_id': '3'})

# Batch get (até 100 items)
response = dynamodb.meta.client.batch_get_item(
    RequestItems={
        'users': {
            'Keys': [
                {'user_id': '1'},
                {'user_id': '2'},
                {'user_id': '3'}
            ]
        }
    }
)
```

## Query

```python
# Query simples por key
response = table.query(
    KeyConditionExpression=Key('customer_id').eq('123')
)
items = response['Items']

# Query com filtro
response = table.query(
    KeyConditionExpression=Key('customer_id').eq('123'),
    FilterExpression=Attr('status').eq('pending')
)

# Query com GSI
response = table.query(
    IndexName='status-index',
    KeyConditionExpression=Key('status').eq('shipped')
)

# Query com ordenação
response = table.query(
    KeyConditionExpression=Key('customer_id').eq('123') & Key('created_at').between('2024-01-01', '2024-12-31')
)
```

## Scan

```python
# Scan completo
response = table.scan()
items = response['Items']

# Scan com filtro
response = table.scan(
    FilterExpression=Attr('age').gte(18) & Attr('active').eq(True)
)

# Scan paginado
last_evaluated_key = None
all_items = []

while True:
    if last_evaluated_key:
        response = table.scan(
            ExclusiveStartKey=last_evaluated_key
        )
    else:
        response = table.scan()
    
    all_items.extend(response['Items'])
    last_evaluated_key = response.get('LastEvaluatedKey')
    
    if not last_evaluated_key:
        break
```

## Expressions

```python
from boto3.dynamodb.conditions import Key, Attr, Or, And

# Condições
Attr('name').eq('John')
Attr('age').lt(30)
Attr('tags').contains('premium')
Attr('scores').is_type()
Or(Attr('a').eq(1), Attr('b').eq(2))

# Update expressions
'SET age = :age, #tag = :tag ADD scores :inc'
'REMOVE description'
'SET #counter = #counter + :inc'

# Projection expression
'user_id, name, email'

# Condition expression
'attribute_not_exists(user_id) AND age > :min_age'
```

## Transactions

```python
# Transação de escrita
dynamodb.meta.client.transact_write_items(
    TransactItems=[
        {
            'Put': {
                'TableName': 'orders',
                'Item': {'order_id': '1', 'status': 'pending'}
            }
        },
        {
            'Update': {
                'TableName': 'customers',
                'Key': {'customer_id': '123'},
                'UpdateExpression': 'SET order_count = order_count + :inc',
                'ExpressionAttributeValues': {':inc': {'N': '1'}}
            }
        }
    ]
)

# Transação de leitura
response = dynamodb.meta.client.transact_get_items(
    TransactItems=[
        {'Get': {'TableName': 'orders', 'Key': {'order_id': {'S': '1'}}}},
        {'Get': {'TableName': 'customers', 'Key': {'customer_id': {'S': '123'}}}}
    ]
)
```

## TTL

```python
# Habilitar TTL
dynamodb.update_time_to_live(
    TableName='sessions',
    TimeToLiveSpecification={
        'Enabled': True,
        'AttributeName': 'expires_at'
    }
)

# TTL em item (timestamp Unix)
import time
expires = int(time.time()) + 3600  # 1 hora
table.put_item(Item={'session_id': 'abc', 'expires_at': expires})
```

## Streams

```python
# Habilitar streams
dynamodb.update_table(
    TableName='users',
    StreamSpecification={
        'StreamEnabled': True,
        'StreamViewType': 'NEW_AND_OLD_IMAGES'  # KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES
    }
)

# Lambda trigger com streams
def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            print(f"New user: {new_image}")
        elif record['eventName'] == 'MODIFY':
            old = record['dynamodb']['OldImage']
            new = record['dynamodb']['NewImage']
            print(f"Updated: {old} -> {new}")
        elif record['eventName'] == 'REMOVE':
            old_image = record['dynamodb']['OldImage']
            print(f"Deleted: {old_image}")
```
