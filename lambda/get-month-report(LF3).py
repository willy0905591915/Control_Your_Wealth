import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

def lambda_handler(event, context):
    # TODO implement
    # print(event)
    month = int(event['queryStringParameters']['month'])
    year = int(event['queryStringParameters']['year'])
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Define timestamp range for March 2024
    start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
    end_date = datetime(year, month + 1, 1).strftime("%Y-%m-%d")
    print(start_date,end_date)
    # Query DynamoDB for items within the specified timestamp range
    response = table.query(
        KeyConditionExpression=Key('timestamp').between(start_date, end_date) & Key('username').eq(username),
    )
    
    # Process the results
    items = response['Items']
    # Do something with the items, like returning them
    print(items) 
    
    total_amount = 0
    category = {}
    category['Food'] = 0
    category['Clothing'] = 0
    category['Living'] = 0
    category['Transportation'] = 0
    category['Others'] = 0
    
    for it in items:
        if  'category' in it and 'amount' in it:
            amount = float(it['amount'])
            total_amount += amount
            if 'F' == it['category'][0] or 'f' == it['category'][0]:
                category['Food'] += amount
            elif 'C' == it['category'][0] or 'c' == it['category'][0]:
                category['Clothing'] += amount
            elif 'L'== it['category'][0] or 'l' == it['category'][0]:
                category['Living'] += amount
            elif 'T'== it['category'][0] or 't' == it['category'][0]:
                category['Transportation'] += amount
            else:
                category['Others'] += amount
                
    json_object = {
        "total": total_amount,
        "Food": category["Food"],
        "Clothing": category['Clothing'],
        "Living": category['Living'],
        "Transportation": category["Transportation"],
        "Others": category['Others']
    }
    
    return {
        'statusCode': 200,
        "headers": { 
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(json_object)
    }
