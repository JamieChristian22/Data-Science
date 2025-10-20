import os
import json
import logging
import boto3

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
log = logging.getLogger()
log.setLevel(logging.INFO)

sns = boto3.client("sns")

def lambda_handler(event, context):
    # Triggered by DynamoDB Streams (INSERT only)
    for record in event.get("Records", []):
        if record.get("eventName") != "INSERT":
            continue
        new_image = record["dynamodb"]["NewImage"]
        message = json.dumps({"new_record": new_image}, default=str)
        log.info("Publishing to SNS topic %s", SNS_TOPIC_ARN)
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject="New Order Inserted")
    return {"status": "ok"}
