import json
import boto3
import datetime
from boto3.dynamodb.conditions import Key

# Initialize the Amazon Cognito Identity client
cognito_client = boto3.client('cognito-idp')

def get_users_and_emails(user_pool_id):
    # Initialize an empty dictionary to store user IDs and emails
    users_and_emails = {}
    
    # List all users in the user pool
    response = cognito_client.list_users(
        UserPoolId=user_pool_id
    )
    
    # Extract user IDs and email addresses
    for user in response['Users']:
        user_id = user['Username']
        email = None
        # Iterate through the attributes of each user to find the email address
        for attribute in user['Attributes']:
            if attribute['Name'] == 'email':
                email = attribute['Value']
                break
        # Store the user ID and email address in the dictionary
        if email:
            users_and_emails[user_id] = email
    
    return users_and_emails

def get_year_month():
    # Get today's date
    today = datetime.date.today()
    # Calculate the first day of the current month
    first_day_of_current_month = today.replace(day=1)
    # Subtract one day to get the last day of the previous month
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    # Extract month and year from the last day of the previous month
    last_month = last_day_of_previous_month.month
    last_year = last_day_of_previous_month.year
    return last_year,last_month


def get_message_dyno(username, year, month):
    
    # Set up DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('records') 
    
    # Define timestamp range for March 2024
    start_date = datetime.datetime(year, month, 1).strftime("%Y-%m-%d")
    end_date = datetime.datetime(year, month + 1, 1).strftime("%Y-%m-%d")
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
       
       
                
    msg = 'Hello! Here are your monthly report in {},{}: \n'.format(
        month, year)
    msg += 'The total_amount is: ${} \n'.format(total_amount)
    for c, amount in category.items():
        msg += '{}: ${} \n'.format(c, amount)
    return msg

def send_email(message, email, year, month):
    client = boto3.client("ses")
    response = client.send_email(
        Destination={
            "ToAddresses": [
                email,
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": message,
                }
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Monthly Bill Report " + str(year) + "." + str(month),
            },
        },
        Source="claudcomputinnyu@gmail.com",
    )
    
def send_month_report(user_id, email):
    year, month = get_year_month()
    message = get_message_dyno(user_id, year, month)
    try:
        send_email(message, email, year, month)
    except Exception as error:
        print("An exception occurred:", error) 
    

def lambda_handler(event, context):
    # TODO implement
    
    # Replace 'your_user_pool_id' with the actual ID of your user pool
    user_pool_id = 'us-east-1_nNwDVvZ4T'

    # Get all users and their email addresses from the specified user pool
    users_and_emails = get_users_and_emails(user_pool_id)
    
    # Print the dictionary containing user IDs and emails
    for user_id, email in users_and_emails.items():
        send_month_report(user_id, email)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
