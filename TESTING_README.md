# Kintone MCP Server テスト実行ガイド

## 🎯 概要

このガイドでは、実装済みのKintone MCPサーバーを実際のMCPクライアントとして動作テストする方法を説明します。

## 🚀 クイックスタート

### 1. 環境セットアップ

```bash
# testフォルダに移動
cd test

# セットアップスクリプトを実行
python setup_test_environment.py
```

### 2. 認証情報の設定

`py/.env` ファイルを編集してKintone認証情報を設定：

```bash
# パスワード認証の場合
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password

# または APIトークン認証の場合
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_API_TOKEN=your-api-token
```

### 3. 自動テスト実行

```bash
# testフォルダから実行
cd test
python test_mcp_server.py
```

## 📋 テスト内容

### 自動テストで確認される項目

- ✅ **前提条件チェック**
  - Python/Node.js依存関係
  - 環境変数設定
  
- ✅ **サーバー起動テスト**
  - MCPサーバーの正常起動
  - ヘルスチェックエンドポイント
  
- ✅ **Node.jsラッパーテスト**
  - Kintone APIクライアントの動作確認
  
- ✅ **MCPツールテスト**
  - 基本的なMCPツールの実行確認

### 手動テスト項目

自動テスト成功後、以下の手動テストも実施可能：

#### Claude Desktopでのテスト

1. **設定ファイルの更新**
   
   自動テスト成功時に出力されるClaude Desktop設定をコピー：
   
   ```json
   {
     "mcpServers": {
       "kintone": {
         "command": "python",
         "args": ["-m", "src.main"],
         "cwd": "/path/to/kintone-mcp-server/py",
         "env": {
           "KINTONE_DOMAIN": "your-domain.cybozu.com",
           "KINTONE_USERNAME": "your-username",
           "KINTONE_PASSWORD": "your-password"
         }
       }
     }
   }
   ```

2. **Claude Desktopでのテスト**
   
   Claude Desktopを再起動後、以下のプロンプトでテスト：
   
   ```
   Kintoneのアプリ一覧を取得してください
   ```
   
   ```
   アプリID 123 のレコードを取得してください
   ```

#### MCP Inspectorでのテスト

```bash
# MCP Inspectorを起動
npx @modelcontextprotocol/inspector python -m src.main

# ブラウザで http://localhost:5173 にアクセス
```

## 🛠️ 利用可能なMCPツール

現在実装されているMCPツール：

### レコード操作
- `kintone_get_records` - レコード取得
- `kintone_create_record` - レコード作成
- `kintone_update_record` - レコード更新
- `kintone_delete_record` - レコード削除

### アプリ操作
- `kintone_get_apps` - アプリ一覧取得
- `kintone_get_app` - アプリ情報取得
- `kintone_get_app_form_fields` - フォーム設定取得

### ファイル操作
- `kintone_upload_file` - ファイルアップロード
- `kintone_download_file` - ファイルダウンロード

### その他
- `kintone_get_users` - ユーザー一覧取得
- `kintone_get_spaces` - スペース一覧取得

## 🔍 トラブルシューティング

### よくある問題

#### 1. サーバー起動エラー
```
❌ MCPサーバーの起動に失敗しました
```

**解決方法:**
- ポート7000が使用中でないか確認
- Python依存関係を再インストール: `pip install -r py/requirements.txt`
- 環境変数の設定を確認

#### 2. 認証エラー
```
❌ Node.jsラッパーエラー: Authentication failed
```

**解決方法:**
- Kintone認証情報を確認
- ドメイン名の形式を確認（例：`your-domain.cybozu.com`）
- APIトークンの権限を確認

#### 3. Node.js依存関係エラー
```
❌ Node.js依存関係が見つかりません
```

**解決方法:**
```bash
cd js
npm install
```

### ログの確認

詳細なログを確認したい場合：

```bash
# デバッグモードでサーバー起動
cd py
DEBUG=true python -m src.main
```

## 📊 期待される結果

### 成功時の出力例

```
🧪 Kintone MCPサーバー 動作テスト開始
==================================================

🔧 前提条件をチェック中...
✅ Python依存関係: OK
✅ Node.js依存関係: OK
✅ 環境変数: OK

🚀 MCPサーバーを起動中...
✅ MCPサーバー起動: OK

--- ヘルスチェックテスト ---
🏥 ヘルスチェックテスト...
✅ ヘルスチェック: healthy

--- Node.jsラッパーテスト ---
🔧 Node.jsラッパーテスト...
✅ Node.jsラッパー: OK

--- MCPツールテスト ---
🛠️ MCPツールテスト...
✅ アプリ一覧取得: OK
📊 MCPツールテスト結果: 1/1

==================================================
📊 テスト結果サマリー
==================================================
✅ 成功: 3
❌ 失敗: 0
📈 成功率: 100.0%

🎉 全てのテストが成功しました！

📋 Claude Desktop設定:
{
  "mcpServers": {
    "kintone": {
      ...
    }
  }
}
```

## 📚 詳細ドキュメント

より詳細なテスト手順については以下を参照：

- [詳細テストガイド](dev_docs/mcp_server_testing_guide.md)
- [実装計画書](dev_docs/nodejs_integration_implementation_plan.md)
- [testフォルダのREADME](test/README.md)

## 🎯 次のステップ

テストが成功したら：

1. **Claude Desktopでの実際の利用**
2. **追加機能のテスト**
3. **パフォーマンステスト**
4. **本番環境での利用検討**

問題が発生した場合は、ログを確認して適切に対処してください。 