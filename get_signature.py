import json
import boto3
import base64

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('signature')

def lambda_handler(event, context):
    try:
        params = event.get('queryStringParameters') or {}

        limit = int(params.get('limit', 2))
        last_evaluated_key_encoded = params.get('lastEvaluatedKey')

        exclusive_start_key = None
        if last_evaluated_key_encoded:
            try:
                decoded_bytes = base64.b64decode(last_evaluated_key_encoded)
                exclusive_start_key = json.loads(decoded_bytes)
            except Exception as e:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({"error": f"Invalid lastEvaluatedKey: {str(e)}"})
                }

        scan_kwargs = {
            'Limit': limit
        }
        if exclusive_start_key:
            scan_kwargs['ExclusiveStartKey'] = exclusive_start_key

        response = table.scan(**scan_kwargs)

        items = response.get('Items', [])
        last_key = response.get('LastEvaluatedKey')

        # Encode lastEvaluatedKey as base64 JSON string
        last_key_encoded = None
        if last_key:
            last_key_encoded = base64.b64encode(json.dumps(last_key).encode()).decode()

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET",
                "Access-Control-Allow-Headers": "*"
            },
            "body": json.dumps({
                "items": items,
                "lastEvaluatedKey": last_key_encoded
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
