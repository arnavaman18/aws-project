import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileFinderRecords')

def lambda_handler(event, context):
    # 'query' will be passed from frontend
    query = event.get('queryStringParameters', {}).get('student', '')

    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing student parameter'})
        }

    # Scan all items and look for the student record
    response = table.scan()
    items = response.get('Items', [])

    results = [item for item in items if query.lower() in item['content'].lower()]

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',  # allows frontend access
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': json.dumps({'results': results})
    }
