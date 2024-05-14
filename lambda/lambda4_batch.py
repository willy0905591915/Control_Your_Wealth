import json
import boto3
import email
import re
import os
from datetime import datetime, timedelta


def get_body(message: email.message.Message):
    if message.is_multipart():
        # multipart messages can have multiple parts
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))

            if ctype == "text/plain" and "attachment" not in cdispo:
                return part.get_payload(decode=True).decode()
            elif ctype == "text/html" and "attachment" not in cdispo:
                return part.get_payload(decode=True).decode()
    else:
        return message.get_payload(decode=True).decode()


def comprehend(body: str):
    client = boto3.client("comprehend")
    response = client.detect_entities(Text=body, LanguageCode="en")
    return response


def extract_total(response):
    entities = response["Entities"]
    quantities = [entity for entity in entities if entity["Type"] == "QUANTITY"]
    total = quantities[-1]["Text"]
    total = re.sub("[^0-9.]", "", total)
    return float(total)


def extract_email(s: str):
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = re.findall(pattern, s)
    return emails[-1]


def recognize_user(email):
    client = boto3.client("cognito-idp")
    try:
        filter_email = """email = \"""" + email + """\""""
        response = client.list_users(
            UserPoolId=os.environ["UserPoolId"], Filter=filter_email
        )
        return response["Users"]
    except:
        print("Error Querying Cognito")


def put_record(username: str, amount: float, category: str):
    client = boto3.client("dynamodb")
    try:
        now = datetime.now() - timedelta(hours=4)
        response = client.put_item(
            TableName=os.environ["TableName"],
            Item={
                "username": {"S": username},
                "timestamp": {"S": now.strftime("%Y-%m-%d %H:%M:%S")},
                "amount": {"N": str(amount)},
                "category": {"S": category},
            },
        )
    except:
        print("Error from dynamo!")

def lambda_handler(event, context):
    # triggered by SQS, each event consists of a batch of message
    s3 = boto3.client("s3")
    records = event["Records"]

    for record in records:
        body = json.loads(record["body"])
        bucket_name = body["bucket_name"]
        object_key = body["object_key"]

        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        message = response["Body"]

        if message.readable():
            content = message.read() # Get email content
            email_data = email.message_from_bytes(content)
            body = get_body(email_data) # We only use email body(containing receipt)
            embeddings = comprehend(body) # embeddings contain a list of message content and corresponding type
            total = extract_total(embeddings)
            print("========Total========")
            print(total)
            email_address = extract_email(email_data["From"])
            print("========Email========")
            print(email_address)
            users = recognize_user(email_address)
            print("========Users========")
            print(users)
            put_record(username=users[0]["Username"], amount=total, category="E-RECEIPT")