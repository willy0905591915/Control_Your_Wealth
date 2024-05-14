import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from decimal import Decimal
import json

def lambda_handler(event, context):
    # Extract parameters from the request body
    timestamp = event['queryStringParameters']['timestamp']
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Construct the key for the item to delete
    key = {
        'username': username,
        'timestamp': timestamp
    }
    
    # Delete the item from DynamoDB
    response = table.delete_item(
        Key=key,
        ReturnValues='ALL_OLD'  # Optional, returns the deleted item
    )
    
    # Return the response
    deleted_item = response.get('Attributes', None)
    if deleted_item:
        return {
            'statusCode': 200,
            'headers': { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'success'})
        }
    else:
        return {
            'statusCode': 404,
            'headers': { 
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Item not found'})
        }
