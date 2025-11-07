import boto3
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileFinderRecords')

def lambda_handler(event, context):
    filename = event['queryStringParameters']['filename']

    # Delete from S3
    bucket_name = "filefinder-s3-bucket"
    s3.delete_object(Bucket=bucket_name, Key=filename)

    # Delete from DynamoDB
    table.delete_item(Key={'filename': filename})

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({'message': f'{filename} deleted successfully'})
    }
