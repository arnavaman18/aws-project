import boto3
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileFinderRecords')


def lambda_handler(event, context):
    # Extract bucket and file details from event
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']

        # Get file content
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj['Body'].read().decode('utf-8', errors='ignore')

        # Store in DynamoDB
        table.put_item(
            Item={
                'filename': file_key,
                'content': file_content
            }
        )
        print(f"Stored {file_key} in DynamoDB")

    return {
        'statusCode': 200,
        'body': json.dumps('Files processed and stored in DynamoDB')
    }
