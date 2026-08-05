import io
import json
import os
import unittest
from datetime import datetime, timezone

import handler


class FakeS3:
    def __init__(self, source):
        self.source = source
        self.puts = []

    def get_object(self, **_kwargs):
        return {"Body": io.BytesIO(self.source)}

    def put_object(self, **kwargs):
        self.puts.append(kwargs)


class FakeDynamoDB:
    def __init__(self):
        self.puts = []

    def put_item(self, **kwargs):
        self.puts.append(kwargs)


def sqs_record(key="dir%2Finput.json"):
    body = {"Records": [{"s3": {"bucket": {"name": "input"}, "object": {"key": key}}}]}
    return {"body": json.dumps(body)}


class ProcessRecordTest(unittest.TestCase):
    def setUp(self):
        os.environ["RESULT_BUCKET"] = "result"
        os.environ["STATUS_TABLE"] = "status"

    def test_writes_result_and_status_using_decoded_object_key(self):
        s3 = FakeS3(b'{"message":"hello"}')
        dynamodb = FakeDynamoDB()
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

        handler.process_record(sqs_record(), s3, dynamodb, now=now)

        self.assertEqual(s3.puts[0]["Key"], "processed/dir/input.json")
        self.assertEqual(json.loads(s3.puts[0]["Body"])["input"], {"message": "hello"})
        self.assertEqual(dynamodb.puts[0]["Item"]["object_key"], {"S": "dir/input.json"})
        self.assertEqual(dynamodb.puts[0]["Item"]["status"], {"S": "SUCCEEDED"})

    def test_invalid_json_is_raised_for_sqs_retry(self):
        with self.assertRaises(json.JSONDecodeError):
            handler.process_record(sqs_record(), FakeS3(b"not-json"), FakeDynamoDB())

    def test_s3_test_event_is_ignored(self):
        s3 = FakeS3(b"")
        dynamodb = FakeDynamoDB()

        processed = handler.process_record(
            {"body": json.dumps({"Event": "s3:TestEvent"})}, s3, dynamodb
        )

        self.assertFalse(processed)
        self.assertEqual(s3.puts, [])
        self.assertEqual(dynamodb.puts, [])


if __name__ == "__main__":
    unittest.main()
