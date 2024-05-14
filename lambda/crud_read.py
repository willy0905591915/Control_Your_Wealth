import boto3
import json
from boto3.dynamodb.conditions import Key
from datetime import datetime

def lambda_handler(event, context):
    # TODO implement
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Query DynamoDB for items for the specified user
    response = table.query(
        KeyConditionExpression=Key('username').eq(username),
    )
    
    # Process the results
    items = response['Items']
    
    # Extract category and amount fields and include them in the response
    result = [{'category': item['category'], 'amount': float(item['amount']), 'timestamp': item['timestamp']} for item in items]
    
    return {
        'statusCode': 200,
        "headers": { 
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(result)
    }
