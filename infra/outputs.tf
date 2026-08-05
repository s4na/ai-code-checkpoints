output "input_bucket" {
  value = aws_s3_bucket.input.bucket
}

output "result_bucket" {
  value = aws_s3_bucket.result.bucket
}

output "status_table" {
  value = aws_dynamodb_table.status.name
}

output "dead_letter_queue_url" {
  value = aws_sqs_queue.dead_letter.id
}

