import json
import uuid
import boto3
from datetime import datetime
from ulid import ULID

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('signature')

def lambda_handler(event, context):
    # Handle CORS preflight OPTIONS request
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')

    if http_method == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # For dev, allow all origins
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": ""
        }

    try:
        print(event)
        body = json.loads(event.get('body', '{}'))

        # Extract fields
        first_name = body.get('firstName')
        last_name = body.get('lastName')
        home_address = body.get('homeAddress')
        current_address = body.get('currentAddress')
        email = body.get('email')
        phone = body.get('phone')
        signature = body.get('signatureBase64')

        required_fields = [
            'firstName', 'lastName', 'homeAddress',
            'currentAddress', 'email', 'phone', 'signatureBase64'
        ]

        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            return response(400, f"Missing required fields: {', '.join(missing_fields)}")
            
        signature_id = str(ULID())

        item = {
            'signature_id': signature_id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'phone': phone,
            'home_address': home_address,
            'current_address': current_address,
            'timestamp': datetime.utcnow().isoformat(),
        }

        if signature:
            item['signatureBase64'] = signature

        # Put item into DynamoDB
        table.put_item(Item=item)

        return response(200, f"Form registered with ID: {signature_id}")

    except Exception as e:
        return response(500, f"Internal server error: {str(e)}")


def response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Allow all origins (for dev)
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps({"message": message})
    }
