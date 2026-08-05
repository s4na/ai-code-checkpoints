import json
import os
from datetime import datetime, timezone
from urllib.parse import unquote_plus


def _clients():
    import boto3

    return boto3.client("s3"), boto3.client("dynamodb")


def process_record(record, s3, dynamodb, now=None):
    event = json.loads(record["body"])
    if event.get("Event") == "s3:TestEvent":
        return False

    s3_record = event["Records"][0]["s3"]
    input_bucket = s3_record["bucket"]["name"]
    object_key = unquote_plus(s3_record["object"]["key"])

    source = s3.get_object(Bucket=input_bucket, Key=object_key)["Body"].read()
    payload = json.loads(source)
    processed_at = (now or datetime.now(timezone.utc)).isoformat()
    result_key = f"processed/{object_key}"
    result = {"input": payload, "processed_at": processed_at}

    s3.put_object(
        Bucket=os.environ["RESULT_BUCKET"],
        Key=result_key,
        Body=json.dumps(result, ensure_ascii=False).encode(),
        ContentType="application/json",
    )
    dynamodb.put_item(
        TableName=os.environ["STATUS_TABLE"],
        Item={
            "object_key": {"S": object_key},
            "status": {"S": "SUCCEEDED"},
            "updated_at": {"S": processed_at},
            "result_key": {"S": result_key},
        },
    )
    return True


def handler(event, _context):
    s3, dynamodb = _clients()
    processed = sum(process_record(record, s3, dynamodb) for record in event["Records"])

    return {"processed": processed}
