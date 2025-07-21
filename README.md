## asset-management-simulation-backend

- 自作の WebApp である資産管理シミュレーションのバックエンドに関するレポジトリです。
- フロントエンドのレポジトリは [こちら](https://github.com/spider-man-tm/asset-management-simulation-frontend)をご参照ください。

![fig](architect.png)

### Overview

- Web フレームワークは Flask を使用しています。
- デプロイ先は Google Cloud Run です。
- develop branch への PR が発行されたタイミングで、GitHub Actions を利用した自動テスト(pytest)が実施されます。
- develop branch への PR がマージされたタイミングで main branch へのリリース PR が自動作成されます。
- main branch へ push、あるいは PR がマージされたタイミングで GitHub Actions を利用した Cloud Run への自動デプロイが実施されます。

### Usage

#### ローカル開発

- 準備
  - Makefile.dev などを用意し、以下のように GCP のプロジェクト ID、リージョン、Artifact Registry リポジトリ名、任意のイメージ名、タグ名、firebase プロジェクト名、ローカルホスト名、（必要に応じて）postman header などを記述
  - Makefile を読み込む必要があるため、`include Makefile`も合わせて記述
  - **注意**: Artifact Registry 対応のため、REGION と REPOSITORY_NAME の設定が新たに必要です

```
PROJECT_ID := xxx
REGION := asia-northeast1
REPOSITORY_NAME := xxx
IMAGE := xxx
TAG := xxx

FIREBASE_PROJECT_NAME := xxx
LOCAL_HOST := http://localhost:3000
POSTMAN_HEADER := http://postman

include Makefile
```

- Docker コンテナを起動する場合

```shell
# ビルド
make build -f Makefile.dev
# ローカルでコンテナ起動
make run-local -f Makefile.dev
# まとめてやる場合
make build run-local -f Makefile.dev
```

- poetry で直接`.venv`を作成する場合

```shell
make install
```

- ローカルで`.venv`環境を使った pytest を実行する場合

```shell
make test-local
```

#### 手動デプロイ

- 事前準備：Artifact Registry にリポジトリを作成

```shell
# Artifact Registry APIを有効化
gcloud services enable artifactregistry.googleapis.com

# Dockerリポジトリを作成
gcloud artifacts repositories create REPOSITORY_NAME \
    --repository-format=docker \
    --location=REGION \
    --description="Docker repository"

# Docker認証を設定
gcloud auth configure-docker REGION-docker.pkg.dev
```

- Makefile.prd などを用意する。あとは以下のコマンドで deploy まで行う
- デプロイ時に`FRONTEND_URL_hoge`や`FIREBASE_PROJECT_NAME`を環境変数として渡す必要があるので Makefile.prd で事前に定義する
- **注意**: IMAGE の形式が Artifact Registry 用に変更されています

```
PROJECT_ID := xxx
IMAGE := REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY_NAME/IMAGE_NAME:TAG
TAG := xxx

FIREBASE_PROJECT_NAME := xxx
FRONTEND_URL_1 := xxx
FRONTEND_URL_2 := xxx
FRONTEND_URL_3 := xxx

include Makefile
```

```shell
# ビルド
make build -f Makefile.prd
# イメージをpush
make push -f Makefile.prd
# Cloud runにデプロイ
make deploy -f Makefile.prd
# まとめてやる場合
make build push deploy -f Makefile.prd
```

#### CI/CD

- 事前準備：Artifact Registry にリポジトリを作成

```shell
# Artifact Registry APIを有効化
gcloud services enable artifactregistry.googleapis.com

# Dockerリポジトリを作成
gcloud artifacts repositories create REPOSITORY_NAME \
    --repository-format=docker \
    --location=REGION \
    --description="Docker repository for CI/CD"
```

- GCP 上に新規サービスアカウントを以下のロールを付与した状態で作成

  - ストレージ管理者
  - Cloud Run 管理者
  - サービスアカウントユーザー
  - Artifact Registry 書き込み権限

- 以下のスクリプトを実行
  - サービスアカウントで発行された json 鍵を使う認証は非推奨のため、workload-identity を使用
  - 実行後、workload_identity_provider が表示されるが、後工程で必要

```shell
PROJECT_ID=xxx
SERVICE_ACCOUNT_NAME=xxx   # 上記で作成したサービスアカウント
POOL_NAME=xxx
POOL_DISPLAY_NAME=xxx
PROVIDER_NAME=xxx
GITHUB_REPO=xxx


# IAM Service Account Credentialsの有効化
gcloud services enable iamcredentials.googleapis.com \
  --project "${PROJECT_ID}"

# Workload Identity Pool 作成
gcloud iam workload-identity-pools create "${POOL_NAME}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="${POOL_DISPLAY_NAME}"
# Pool IDを取得
export WORKLOAD_IDENTITY_POOL_ID=$( \
     gcloud iam workload-identity-pools describe "${POOL_NAME}" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --format="value(name)" \
)

# Workload Identity Provider 設定
gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_NAME}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_NAME}" \
  --display-name="${PROVIDER_DISPLAY_NAME}" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor,attribute.aud=assertion.aud" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# サービス アカウントの権限借用の設定
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"

# workload_identity_providerを表示
echo
echo 'workload_identity_provider:'
echo $(gcloud iam workload-identity-pools providers describe "${PROVIDER_NAME}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_NAME}" \
  --format='value(name)')

```

- GitHub 上で各種 Secrets を設定

| Secrets                    | 説明                                       |
| -------------------------- | ------------------------------------------ |
| ARTIFACT_REGISTRY_REPO     | Artifact Registry のリポジトリ名           |
| FIREBASE_PROJECT_NAME      | Firebase のプロジェクト ID                 |
| FRONTEND_URL_1             | Firebase Hosting の URL (デフォルト 1)     |
| FRONTEND_URL_2             | Firebase Hosting の URL (デフォルト 2)     |
| FRONTEND_URL_3             | Firebase Hosting の URL (カスタムドメイン) |
| GCP_PROJECT_ID             | デプロイ先のプロジェクト ID                |
| GCP_REGION                 | デプロイ先のリージョン                     |
| SERVICE_ACCOUNT_NAME       | 作成したサービスアカウント名               |
| SERVICE_NAME               | Docker Image 名                            |
| WORKLOAD_IDENTITY_PROVIDER | 作成したプロバイダー名                     |
