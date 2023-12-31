import os

import boto3
from dotenv import load_dotenv

from .parser import (
    map_word_id,
    extract_table_info,
    get_key_map,
    get_value_map,
    get_kv_map,
)

load_dotenv()

# Configuration
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
REGION_NAME = 'ap-south-1'  # Change as needed
BUCKET_NAME = 'billmunshi'


def remove_duplicates(table, form):
    # Flatten all table data into a single list and convert to set for faster lookup
    all_table_data = set(cell for sublist in table.values() for row in sublist for cell in row)

    # Check each form data key against all table data
    for key in list(form.keys()):
        if key in all_table_data:
            del form[key]
    return form


def analyze_document(bucketName, filename):
    textract = boto3.client("textract", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY,
                            region_name=REGION_NAME)
    response = textract.analyze_document(
        Document={
            "S3Object": {
                "Bucket": bucketName,
                "Name": filename,
            }
        },
        FeatureTypes=["FORMS", "TABLES"],
    )

    # Filtering data without bounding boxes
    form_data = []
    table_data = []

    for item in response['Blocks']:
        # Remove bounding box information
        item.pop('Geometry', None)
        if item['BlockType'] == 'KEY_VALUE_SET':
            form_data.append(item)
        elif item['BlockType'] == 'TABLE':
            table_data.append(item)

    # Process further extraction
    word_map = map_word_id(response)
    table = extract_table_info(response, word_map)
    key_map = get_key_map(response, word_map)
    value_map = get_value_map(response, word_map)
    kv_map = get_kv_map(key_map, value_map)

    # Removing duplicates between form_data and table_data
    form_data_cleaned = remove_duplicates(table, kv_map)

    final_json = {
        "table_data": table,
        "form_data": form_data_cleaned
    }
    # print(final_json)
    # print(table)
    # return final_json
    return form_data_cleaned, table
