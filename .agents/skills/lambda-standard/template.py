import json


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    # Lógica gerada pelo agent

    return {
        "statusCode": 200,
        "body": json.dumps({...})
    }
