#!/usr/bin/env bash
set -euo pipefail

endpoint="http://localhost:4566"
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL="$endpoint"

input_bucket="$(terraform output -raw input_bucket)"
result_bucket="$(terraform output -raw result_bucket)"
status_table="$(terraform output -raw status_table)"
dlq_url="$(terraform output -raw dead_letter_queue_url)"

valid_file="$(mktemp)"
invalid_file="$(mktemp)"
trap 'rm -f "$valid_file" "$invalid_file"' EXIT
printf '{"message":"hello"}\n' >"$valid_file"
printf 'not-json\n' >"$invalid_file"

aws s3 cp "$valid_file" "s3://$input_bucket/valid.json"
for _ in $(seq 1 60); do
  if aws s3api head-object --bucket "$result_bucket" --key processed/valid.json >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
aws s3api head-object --bucket "$result_bucket" --key processed/valid.json >/dev/null
status_result="$(aws dynamodb get-item --table-name "$status_table" --key '{"object_key":{"S":"valid.json"}}' \
  --query '[Item.status.S, Item.result_key.S]' --output text)"
[ "$status_result" = $'SUCCEEDED\tprocessed/valid.json' ]

aws sqs purge-queue --queue-url "$dlq_url"
invalid_key="invalid-$(date +%s).json"
aws s3 cp "$invalid_file" "s3://$input_bucket/$invalid_key"
for _ in $(seq 1 360); do
  body="$(aws sqs receive-message --queue-url "$dlq_url" --wait-time-seconds 1 \
    --query 'Messages[0].Body' --output text)"
  if [[ "$body" == *"$invalid_key"* ]]; then
    exit 0
  fi
done

echo "不正JSONが制限時間内にDead Letter Queueへ移動しませんでした" >&2
exit 1
