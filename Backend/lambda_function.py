import json
import boto3
import random
import string

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlTable')

def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    # CREATE SHORT URL
    if method == "POST":
        body = json.loads(event.get("body", "{}"))
        long_url = body.get("url")

        short_id = generate_short_id()

        table.put_item(Item={
            "shortId": short_id,
            "longUrl": long_url
        })

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "shortUrl": short_id
            })
        }

    # REDIRECT
    if method == "GET":
        short_id = event.get("pathParameters", {}).get("id")

        response = table.get_item(Key={"shortId": short_id})

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": "URL not found"
            }

        return {
            "statusCode": 302,
            "headers": {
                "Location": response["Item"]["longUrl"]
            }
        }
