# Serverless POC (API Gateway → SQS → Lambda → DynamoDB → Streams → Lambda → SNS)

This SAM template deploys the exact flow from your exercise with **least‑privilege IAM**, a **dead‑letter queue**, and sane defaults.

## Prereqs
- AWS CLI configured for **us-east-1**
- AWS SAM CLI
- Python 3.12

## Deploy
```bash
sam build
sam deploy --guided   --stack-name serverless-poc   --region us-east-1   --parameter-overrides EmailSubscription=you@example.com
```
Note: Confirm the SNS email subscription you'll receive after deploy.

## Test
```bash
curl -X POST "$(sam list endpoints --output json | jq -r '.[0].Uri')"   -H "Content-Type: application/json"   -d '{"item":"latex gloves","customerID":"12345"}'
```
Or find the URL in the CloudFormation **Outputs** as `ApiInvokeUrl` and POST to `/order`.

## Tear down
```bash
sam delete --stack-name serverless-poc --region us-east-1
```

## Files
- `template.yaml` – All resources (DynamoDB, SQS(+DLQ), Lambda x2, SNS(+subscription), API Gateway + IAM role)
- `src/lambda_sqs_to_ddb.py` – SQS consumer that writes to DynamoDB
- `src/lambda_stream_to_sns.py` – Streams consumer that publishes to SNS
```

