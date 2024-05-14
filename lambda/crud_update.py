import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from decimal import Decimal
import json

def lambda_handler(event, context):
    # Extract parameters from the request body
    request_body = event['body']
    print(request_body)
    category = request_body['category']
    amount = Decimal(request_body['amount']) # Convert to Decimal
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    timestamp = request_body['timestamp']
    new_category = request_body['new_category']
    new_amount = Decimal(request_body['new_amount']) # Convert to Decimal
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Construct the key for the item to update
    key = {
        'username': username,
        'timestamp': timestamp
    }
    
    # Update the item in DynamoDB
    response = table.update_item(
        Key=key,
        UpdateExpression='SET #category = :category, #amount = :amount',
        ExpressionAttributeNames={
            '#category': 'category',
            '#amount': 'amount'
        },
        ExpressionAttributeValues={
            ':category': new_category,
            ':amount': new_amount
        },
        ReturnValues='ALL_NEW'
    )
    
    # Return the updated item
    updated_item = response['Attributes']
    return {
        'statusCode': 200,
        'headers': { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': updated_item # Serialize updated_item to JSON
    }
