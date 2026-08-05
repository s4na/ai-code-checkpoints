# 設計レビュー

## 対応すべき問題

### S3からSQSへ送信する権限が不足していた

設計にはLambdaのIAM権限だけが記載され、S3がSQSへメッセージを送信するためのキューポリシーが明示されていなかった。入力バケットを送信元として限定したSQSキューポリシーをTerraformの管理対象へ追加する。

参考: https://docs.aws.amazon.com/AmazonS3/latest/userguide/grant-destinations-permissions-to-s3.html

### 再試行設定が未決定のままだった

Lambdaのタイムアウト、SQSのvisibility timeout、Dead Letter Queueへ移動するまでの受信回数が決まっておらず、不正なJSONが最終的にDead Letter Queueへ送られるという受け入れ条件を一意に実装できなかった。

Lambdaのタイムアウトを10秒、visibility timeoutを60秒、maxReceiveCountを5とする。AWSはvisibility timeoutをLambdaタイムアウトの6倍以上、maxReceiveCountを少なくとも5にすることを推奨しており、この小規模な検証にもそのまま適用できる。

参考: https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html

### 重複イベントの扱いが不明確だった

S3イベント通知は重複する可能性があるため、入力オブジェクトキーから結果のS3キーとDynamoDBの主キーを決定する。同じ入力が再処理された場合は同じ保存先を上書きする。厳密な一度だけの処理やロック機構は今回の対象外とする。

### Floci非対応時の判断が不明確だった

エミュレーターの不足を独自スクリプトや別のイベント経路で回避すると、本来検証したいTerraform構成が変わってしまう。S3からSQS、SQSからLambdaのどちらかが再現できない場合は、互換性上の実験結果として記録し、実装を拡張せず作業を止める。

## 採用しない提案とその理由

### DynamoDBを削除する

単純なファイル変換だけならS3だけで完結できるが、今回は複数リソース間の設計レビューを検証することが目的である。処理状態の保存という明確な責務があるため残す。

### FIFOキューを使用する

S3イベント通知はSQS FIFOキューを直接の送信先にできず、EventBridgeが追加で必要になる。順序保証は要件にないため、Standardキューを使用する。

参考: https://docs.aws.amazon.com/AmazonS3/latest/userguide/notification-how-to-event-types-and-destinations.html

### 部分バッチ応答を実装する

バッチサイズを1にするため効果がなく、Lambda実装だけが複雑になる。今回の検証には導入しない。

### 汎用Terraformモジュールへ分割する

対象はローカルの単一構成であり、再利用要件がない。AWS向けリソース定義を保ちながら、Floci固有のprovider設定だけを分離する。

### 監視、通知、暗号鍵を追加する

本番運用は対象外であり、ローカルでイベント連携と失敗経路を確認する目的には不要である。

## 最終評価

設計の目的とスコープは妥当で、S3、SQS、Lambda、DynamoDB、Dead Letter Queueの連携はインフラ設計レビューの実験として十分な複雑さがある。

不足していた権限、再試行、重複処理、エミュレーター非対応時の判断を設計へ反映した。追加のサービスや抽象化は不要であり、反映後の設計で実装へ進める。
