import json
import boto3
import base64
import logging
from datetime import datetime
import pytz
import re


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('records')

def lambda_handler(event, context):
    logger.info(f'Received event: {json.dumps(event)}')  # Log the entire event for debugging
    try:
        base64_image = event.get('body', None)
        username = event.get('username', 'anonymous')
        category = event.get('category', 'uncategorized')

        try:
            file_content = base64.b64decode(base64_image)
            logger.info("Successfully decoded base64 image.")
        except Exception as e:
            raise ValueError(f"Error decoding base64: {e}")

        file_name = 'uploaded_receipt.jpg'
        s3_bucket_name = 'upload-receipt-images'

        s3.put_object(Body=file_content, Bucket=s3_bucket_name, Key=file_name)
        
        response = s3.get_object(Bucket=s3_bucket_name, Key=file_name)
        document_bytes = response['Body'].read()

        textract_response = textract.analyze_document(
            Document={'Bytes': document_bytes},
            FeatureTypes=["FORMS"]
        )

        total_value = process_textract_response(textract_response)
        
        new_york_tz = pytz.timezone('America/New_York')
        timestamp = datetime.now(new_york_tz).strftime('%Y-%m-%d %H:%M:%S')

        table.put_item(Item={
            'username': username,
            'timestamp': timestamp,
            'amount': total_value,
            'category': category
        })

        return {
            'statusCode': 200,
            'headers': { 
                "Content-Type": "application/json",
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Extraction successful',
                'amount': total_value,
                'timestamp': timestamp,
                'username': username,
                'category': category
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_textract_response(textract_response):
    blocks = textract_response['Blocks']
    key_map, value_map, block_map = categorize_blocks(blocks)
    total_value = find_total_value(key_map, value_map, block_map)
    return total_value

def categorize_blocks(blocks):
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            elif 'VALUE' in block['EntityTypes']:
                value_map[block_id] = block
    return key_map, value_map, block_map


def find_total_value(key_map, value_map, block_map):
    # Regex pattern to find amounts
    amount_pattern = re.compile(r'[\$£€]? ?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b')
    
    preferred_keys = ['total', 'grand total', 'final total', 'total amount', 'total due']
    possible_keys = preferred_keys + ['sum', 'amount', 'balance', 'final']
    
    max_value = None

    for block_id, key_block in key_map.items():
        key_text = get_text(key_block, block_map).lower()

        if any(key in key_text for key in possible_keys):
            value_block = find_value_block(key_block, value_map, block_map)
            if value_block:
                value_text = get_text(value_block, block_map)
                match = amount_pattern.search(value_text)
                if match:
                    value = float(match.group().replace(',', '').replace('$', ''))
                    if max_value is None or value > max_value:
                        max_value = value

    return str(max_value) if max_value is not None else "Value not found"



def find_value_block(key_block, value_map, block_map):
    for relationship in key_block.get('Relationships', []):
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                if value_id in value_map:
                    return value_map[value_id]
    return None

def get_text(block, block_map):
    text = ""
    if 'Relationships' in block:
        for relationship in block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child_block = block_map[child_id]
                    if 'Text' in child_block:
                        text += child_block['Text'] + ' '
    return text.strip()




