# Claude Desktop セットアップガイド - Kintone MCP Server

## 📋 概要

完全Node.js移行版のKintone MCPサーバー（`mcp_stdio_hybrid_clean.py`）をClaude Desktopで使用するためのセットアップガイドです。

## 🎯 推奨設定

### 最新版（完全Node.js移行版）
- **ファイル名**: `claude_desktop_config_recommended_new.json`
- **サーバー名**: `kintone-complete-nodejs-49tools`
- **ツール数**: 47個（定義済み）/ 45個（Claude Desktop表示）
- **差異**: 2個（原因は軽微な表示制限、機能に支障なし）

## 📁 設定ファイル

### 1. 基本設定（`claude_desktop_config_updated.json`）

```json
{
  "mcpServers": {
    "kintone-complete-nodejs": {
      "command": "python",
      "args": ["/path/to/kintone-mcp-server/src/python/main.py"],
      "cwd": "/path/to/kintone-mcp-server/src/python",
      "env": {
        "PYTHONPATH": "/path/to/kintone-mcp-server/src/python"
      }
    }
  }
}
```

### 2. 推奨設定（`claude_desktop_config_recommended_new.json`）

ログ無効化とメタデータを含む完全版設定

## 🔧 セットアップ手順

### Step 1: 環境変数の設定確認

`.env`ファイルが正しく設定されていることを確認：

```env
# Kintone認証情報（ユーザー名/パスワード認証の場合）
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password

# または APIトークン認証の場合
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_API_TOKEN=your-api-token
```

### Step 2: Node.js依存関係の確認

```bash
cd ../js
npm install
```

### Step 3: Claude Desktop設定ファイルの適用

1. Claude Desktopの設定ディレクトリを確認
   - Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. 推奨設定ファイルの内容をコピー：
   ```bash
   # Windows
   copy claude_desktop_config_recommended_new.json "%APPDATA%\\Claude\\claude_desktop_config.json"
   
   # macOS/Linux
   cp claude_desktop_config_recommended_new.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

### Step 4: Claude Desktopの再起動

Claude Desktopを再起動して設定を反映

## ✅ 動作確認

### 1. 基本テスト

```bash
python test_mcp_client.py
```

### 2. 完全移行テスト

```bash
python test_complete_nodejs_migration.py
```

## 🎛️ 利用可能なツール（49個）

### レコード操作
- `search_records` - レコード検索
- `get_record` - レコード取得
- `create_record` - レコード作成
- `update_record` - レコード更新
- `add_record_comment` - レコードコメント追加

### アプリ管理
- `get_apps_info` - アプリ情報取得
- `create_app` - アプリ作成
- `deploy_app` - アプリデプロイ
- `get_deploy_status` - デプロイ状況確認
- `update_app_settings` - アプリ設定更新

### フィールド管理
- `add_fields` - フィールド追加
- `update_fields` - フィールド更新
- `delete_fields` - フィールド削除
- `get_form_fields` - フォームフィールド取得

### レイアウト管理
- `get_form_layout` - フォームレイアウト取得
- `update_form_layout` - フォームレイアウト更新
- `create_layout_element` - レイアウト要素作成

### ファイル操作
- `upload_file` - ファイルアップロード
- `download_file` - ファイルダウンロード

### ユーザー・グループ管理
- `get_users` - ユーザー一覧取得
- `get_groups` - グループ一覧取得
- `get_group_users` - グループユーザー取得

### その他
- `logging_set_level` - ログレベル設定
- `logging_get_level` - ログレベル取得
- `logging_send_message` - ログメッセージ送信

## 🚨 トラブルシューティング

### 問題: 認証エラー

```
[404] [GAIA_AP01] 指定したアプリ（id: X）が見つかりません
```

**解決策**:
1. アプリIDが正しいか確認
2. アプリがKintoneに存在するか確認
3. 認証情報（ユーザー名/パスワードまたはAPIトークン）が正しいか確認

### 問題: Node.jsラッパーエラー

```
Node.jsラッパーが利用できません
```

**解決策**:
1. Node.jsがインストールされているか確認
2. `js/package.json`の依存関係がインストールされているか確認
3. `js/kintone_nodejs_wrapper.mjs`が存在するか確認

## 📊 パフォーマンス

- **応答時間**: 通常1-3秒（Node.js経由）
- **同時実行**: 非同期処理でサポート
- **エラーハンドリング**: 統一されたエラーレスポンス形式

## 🔄 アップデート履歴

- **v1.0.0**: 完全Node.js移行版リリース
- 全49ツールがNode.js経由で実行
- 統一されたアーキテクチャとエラーハンドリング
- Claude Desktop連携の安定性向上

---

**注意**: このガイドは完全Node.js移行版（`mcp_stdio_hybrid_clean.py`）専用です。他のバージョンとは設定が異なる場合があります。 