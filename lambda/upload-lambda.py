import boto3
import json
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = "filefinder-s3-bucket"
    filename = event['queryStringParameters']['filename']

    # Generate presigned URL
    upload_url = s3.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket_name, 'Key': filename},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({'uploadURL': upload_url})
    }
