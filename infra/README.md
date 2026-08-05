# ローカル検証手順

Docker、Terraform 1.10以降、AWS CLIが必要です。AWSアカウントや認証トークンは不要です。

```sh
cd infra
docker compose up -d
curl --fail --retry 30 --retry-delay 2 --retry-all-errors http://localhost:4566/_localstack/health
terraform init
terraform apply -auto-approve
bash verify.sh
terraform destroy -auto-approve
docker compose down
```

`verify.sh`は正常JSONのS3/DynamoDBへの保存と、不正JSONが5回の試行後にDead Letter Queueへ移ることを確認します。後者には約5分かかります。
