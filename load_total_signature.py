import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('signature')

def lambda_handler(event, context):
    try:
        total_count = 0
        last_evaluated_key = None

        while True:
            scan_kwargs = {
                'Select': 'COUNT'
            }
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

            response = table.scan(**scan_kwargs)
            total_count += response.get('Count', 0)
            last_evaluated_key = response.get('LastEvaluatedKey')

            if not last_evaluated_key:
                break

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": {"total":total_count}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": f"Error: {str(e)}"
        }
