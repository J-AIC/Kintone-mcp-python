# Kintone MCP Server

Kintone MCP (Model Context Protocol) Server は、MCPクライアントを通じてKintone API機能を利用できるようにするサーバーです。

## 🎯 概要

- **Python MCP Server** + **Node.js API Wrapper**アーキテクチャ
- Claude Desktopなどとの統合により自然言語でKintone操作が可能

## 🚀 主要機能

### レコード操作
- レコード検索・取得・作成・更新
- レコードコメント追加

### アプリ管理
- アプリ情報取得・作成・デプロイ
- アプリ設定の更新・管理

### フィールド・レイアウト
- フィールド追加・更新・削除
- フォームレイアウトの設計・変更

### ユーザー管理
- ユーザー・グループ情報取得
- ゲストユーザー追加

### ファイル操作
- ファイルアップロード・ダウンロード

## 📁 プロジェクト構成

```
kintone-mcp-server/
├── src/                                # メインソースコード
│   ├── python/                         # Python MCP Server
│   │   ├── main.py                     # メインサーバーファイル
│   │   ├── .env                        # 環境変数
│   │   ├── requirements.txt            # Python依存関係
│   │   └── server/                     # サーバー実装
│   └── nodejs/                         # Node.js API Wrapper
│       ├── wrapper.mjs                 # APIラッパー
│       └── package.json                # Node.js依存関係
├── config/                             # 設定ファイル
│   └── claude-desktop/                 # Claude Desktop設定
│       ├── recommended.json            # 推奨設定
│       ├── debug.json                  # デバッグ用設定
│       └── setup-guide.md              # セットアップガイド
├── tests/                              # テスト
├── tools/                              # 開発ツール
└── archive/                            # 開発履歴アーカイブ
```

## ⚡ クイックスタート

### 1. 環境設定

```bash
# リポジトリをクローン
git clone <repository-url>
cd kintone-mcp-server

# Python依存関係インストール
cd src/python
pip install -r requirements.txt

# Node.js依存関係インストール
cd ../nodejs
npm install
```

### 2. 認証設定

`src/python/.env` ファイルを作成：

```env
KINTONE_DOMAIN=your-domain.cybozu.com
KINTONE_USERNAME=your-username
KINTONE_PASSWORD=your-password
# または
KINTONE_API_TOKEN=your-api-token
```

### 3. Claude Desktop設定

`config/claude-desktop/recommended.json` の内容をClaude Desktopの設定ファイルに追加してください。

詳細は `config/claude-desktop/setup-guide.md` をご確認ください。

### 4. 動作確認

```bash
# テスト実行
cd tests/integration
python test_mcp_client.py
```

## 🔧 開発者向け情報

### アーキテクチャ

1. **Python側**: MCPプロトコル処理とツール定義管理
2. **Node.js側**: Kintone API実行 (`@kintone/rest-api-client`使用)
3. **統一実行**: 全ツールがNode.js経由で実行される

### 主要ファイル

- `src/python/main.py`: メインMCPサーバー
- `src/nodejs/wrapper.mjs`: Node.js APIラッパー
- `config/claude-desktop/recommended.json`: Claude Desktop設定例


## 📄 ライセンス

[MIT License](LICENSE)

## 注意事項
「kintone」はサイボウズ株式会社の登録商標です。
このソースコードは技術検証を目的としており、実際の動作は保証しません。
また、公開している内容は情報提供を目的としており、個別のサポートはできません。 
設定内容についてのご質問や動作しないといったお問い合わせには対応ができませんので、ご承知おきください。

