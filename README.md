# 業務タスク管理システム

AIアシスタント機能付きのタスク管理Webアプリケーション

## 機能

- タスクの追加、完了、削除
- AIによるタスク実行のアドバイス提案
- フィルタリング（全件表示/作業中/完了）
- モダンで使いやすいUI
- レスポンシブデザイン

## 技術スタック

### バックエンド
- Python 3.13
- Flask 3.0.0
- SQLite
- OpenRouter API (Mistral-7B)

### フロントエンド
- HTML5
- CSS3
- JavaScript (Vanilla)

### インフラ
- Vercel (ホスティング)
- SQLite (/tmp/database.db)

## ローカル開発環境のセットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/hikiroku/turbo-happiness.git
cd turbo-happiness
```

2. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

3. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定：
```
OPENROUTER_API_KEY=your_api_key_here
```

4. アプリケーションの起動
```bash
python app.py
```

5. ブラウザでアクセス
```
http://localhost:5000
```

## デプロイ

このアプリケーションはVercelにデプロイされています。
デプロイ時には以下の環境変数を設定してください：

- `OPENROUTER_API_KEY`: OpenRouter APIのキー

注意：Vercel環境では、データベースは `/tmp/database.db` に作成されます。
これは一時的なストレージであり、デプロイごとにデータはリセットされます。

## ライセンス

MIT License
