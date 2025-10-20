import os
import json
import uuid
import logging
import boto3

DDB_TABLE = os.environ.get("DDB_TABLE", "orders")
ORDER_ID_FIELD = os.environ.get("ORDER_ID_FIELD", "orderID")

log = logging.getLogger()
log.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DDB_TABLE)

def lambda_handler(event, context):
    # Triggered by SQS
    for record in event.get("Records", []):
        body = record.get("body", "")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            # Accept raw strings too
            payload = {"raw": body}

        # Use caller-supplied orderID if present; otherwise generate one
        order_id = str(payload.get(ORDER_ID_FIELD) or uuid.uuid4())

        item = {
            ORDER_ID_FIELD: order_id,
            "order": payload
        }
        log.info("Writing item to DynamoDB: %s", item)
        table.put_item(Item=item)
    return {"status": "ok"}
