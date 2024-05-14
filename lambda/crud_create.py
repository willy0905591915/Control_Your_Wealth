import boto3
from decimal import Decimal
import json

def lambda_handler(event, context):
    # Extract parameters from the request body
    request_body = json.loads(event['body'])
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    category = request_body['category']
    amount = Decimal(request_body['amount']) # Convert to Decimal
    timestamp = request_body['timestamp']
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Construct the item to insert into DynamoDB
    item = {
        'username': username,
        'category': category,
        'amount': amount,
        'timestamp': timestamp
    }
    
    # Insert the item into DynamoDB
    table.put_item(Item=item)
    
    # Return a success response
    return {
        'statusCode': 200,
        'headers': { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'message':'success'})
    }
