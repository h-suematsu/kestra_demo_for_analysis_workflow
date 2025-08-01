# ここは

Kestra が解析 DB の脱 dbt(workflow 導入)の要件に合うかを検証する場

## 背景

現在 ML モデルによる複数の解析結果を dbt によって作成される複数のクエリ群によって加工・集約され解析 DB と呼ばれるデータベースに保存されています。

ML 解析結果(PubSub) -> BigQuery -> dbt クエリ -> BigQuery

ただ SQL で表現するにはあまりに複雑なクエリになっていることもあり、メンテナンス・監視ができていないのが現状です。

## Workflow に求める要件

- dbt のクエリ群を workflow の step に分解して IO を明確にすることで、テストを容易にする
- 数時間の間で解析された結果を丸ごとクエリするのではなく、解析処理ごとに workflow を実行させるようにしたい（バッチ処理よりはイベント処理に近い）
  - ロジックの簡素化を実現したい
- step 間の中間生成物はインメモリーに限定する
- workflow の最終生成物のみを DB あるいはファイル出力する
- 解析結果は PubSub の Topic に送信されるため、結果を push で取得する必要がある
  - workflow 開始時にはまだ出力が完了していない可能性があり、完了まで待機する必要がある
  - workflow の中で複数の解析結果を取得するが、同じ job_id の解析結果を取得する必要がある
- 20K events/min 程度の workflow run に耐えることができる耐久性とスケーラビリティ
- 品質
  - 各 step は単体テストによって品質が担保される
  - workflow はローカルで検証できる状態になっている
- 言語
  - 各 step は Python を基本とする

## Workflow の構成

- PubSub の push event を受け取る用の Proxy Workflow
  - 検証では PubSub の用意は不要で、REST API 経由で worflow がトリガーされるところから再現したい
  - Proxy Workflow では PubSub のメッセージ（リクエスト body）から job_id, analysis_type を取得し、KV ストアに記録する
    - key: <job_id>.<analysis_type>
    - value: <message>
- 解析 DB のデータを生成するための Analysis Workflow
  - Proxy Workflow と同様に、PubSub から REST API 形式でトリガーされる。
  - Analysis Workflow では KV ストア に保存された各 analysis_type の結果を元に必要なデータが揃ったら処理を開始するようにする
  - Analysis Workflow で生成された各データはファイルに出力され蓄積される
  - step は役割に応じて分割して実装すること（適宜共通化も行う）

## 環境構築

### 開発ツールのセットアップ

### 依存関係のセットアップ

```bash
# uv のインストール（必要な場合）
brew install uv

# 仮想環境の作成
uv venv

# 依存関係のインストール
uv sync --all-package --all-groups
```

### Kestra サーバーのセットアップ

```bash
docker compose up -d
```

access to http://localhost:8080

## ワークフローの実行

```bash
curl -v -X POST -H 'Content-Type: multipart/form-data' \
-F 'message={"job_id": "aaaaaa", "analysis_type": "type_a", "data": {"value": 40}}' \
'http://localhost:8080/api/v1/main/executions/events.demo/proxy_workflow'
```

## ワークフローの validate

https://kestra.io/docs/api-reference/open-source#post-/api/v1/flows/validate

```bash
curl -v -X POST -H 'Content-Type: application/x-yaml' \
--data-binary @flows/local/<workflow_name>.yml \
'http://localhost:8080/api/v1/flows/validate'
```

## テストの実行

```bash
# 依存関係の同期
uv sync --all-packages --all-groups

# テストの実行
uv run pytest test/
```

## リントとフォーマット

```bash
# Ruff でリントチェック
uv run ruff check .

# 自動修正可能な問題を修正
uv run ruff check --fix .

# コードフォーマット
uv run ruff format .
```

## ローカルでのワークフロー開発

ローカルと Kestra UI でワークフローを同期します。
https://kestra.io/docs/how-to-guides/local-flow-sync

- `flows/local` ディレクトリに配置
- ファイル名を、`<namespace>.<flow_id>.yml` に設定する

作成・削除もローカル <=> Kestra UI で同期されます。
