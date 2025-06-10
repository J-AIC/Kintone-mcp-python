"""
Documentation tools implementation for kintone MCP Server.
"""

from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

def get_field_type_documentation(field_type: str) -> str:
    """
    フィールドタイプに基づいてドキュメントを取得する
    
    Args:
        field_type: フィールドタイプ（大文字）
        
    Returns:
        str: ドキュメント文字列
    """
    field_type = field_type.upper()
    
    if field_type in ['SINGLE_LINE_TEXT', 'MULTI_LINE_TEXT']:
        return get_text_field_documentation(field_type)
    elif field_type == 'NUMBER':
        return get_number_field_documentation()
    elif field_type == 'DATE':
        return get_date_field_documentation()
    elif field_type == 'TIME':
        return get_time_field_documentation()
    elif field_type == 'DATETIME':
        return get_datetime_field_documentation()
    elif field_type == 'RICH_TEXT':
        return get_rich_text_documentation()
    elif field_type == 'FILE':
        return get_file_field_documentation()
    elif field_type in ['USER_SELECT', 'GROUP_SELECT', 'ORGANIZATION_SELECT']:
        return get_user_select_documentation(field_type)
    elif field_type == 'SUBTABLE':
        return get_subtable_documentation()
    elif field_type == 'CALC':
        return get_calc_field_documentation()
    elif field_type in ['DROP_DOWN', 'RADIO_BUTTON', 'CHECK_BOX', 'MULTI_SELECT']:
        return get_choice_field_documentation(field_type)
    elif field_type == 'LINK':
        return get_link_field_documentation()
    elif field_type == 'LOOKUP':
        return get_lookup_documentation()
    elif field_type == 'REFERENCE_TABLE':
        return get_reference_table_documentation()
    elif field_type in ['RECORD_NUMBER', 'CREATOR', 'MODIFIER', 'CREATED_TIME', 'UPDATED_TIME']:
        return get_system_field_documentation()
    elif field_type in ['LAYOUT', 'FORM_LAYOUT', 'GROUP']:
        return get_layout_field_documentation(field_type)
    else:
        return f"# {field_type}フィールドのドキュメント\n\n申し訳ありませんが、このフィールドタイプのドキュメントはまだ準備されていません。"

def get_available_field_types() -> Dict[str, Any]:
    """
    利用可能なフィールドタイプの一覧を取得する
    
    Returns:
        Dict[str, Any]: フィールドタイプの一覧（カテゴリ別）
    """
    return {
        "basic": [
            {"type": "SINGLE_LINE_TEXT", "name": "1行テキスト"},
            {"type": "MULTI_LINE_TEXT", "name": "複数行テキスト"},
            {"type": "RICH_TEXT", "name": "リッチテキスト"},
            {"type": "NUMBER", "name": "数値"},
            {"type": "CALC", "name": "計算"}
        ],
        "selection": [
            {"type": "DROP_DOWN", "name": "ドロップダウン"},
            {"type": "RADIO_BUTTON", "name": "ラジオボタン"},
            {"type": "CHECK_BOX", "name": "チェックボックス"},
            {"type": "MULTI_SELECT", "name": "複数選択"}
        ],
        "dateTime": [
            {"type": "DATE", "name": "日付"},
            {"type": "TIME", "name": "時刻"},
            {"type": "DATETIME", "name": "日時"}
        ],
        "reference": [
            {"type": "USER_SELECT", "name": "ユーザー選択"},
            {"type": "GROUP_SELECT", "name": "グループ選択"},
            {"type": "ORGANIZATION_SELECT", "name": "組織選択"},
            {"type": "LOOKUP", "name": "ルックアップ"},
            {"type": "REFERENCE_TABLE", "name": "関連テーブル"}
        ],
        "system": [
            {"type": "RECORD_NUMBER", "name": "レコード番号"},
            {"type": "CREATOR", "name": "作成者"},
            {"type": "MODIFIER", "name": "更新者"},
            {"type": "CREATED_TIME", "name": "作成日時"},
            {"type": "UPDATED_TIME", "name": "更新日時"}
        ],
        "other": [
            {"type": "LINK", "name": "リンク"},
            {"type": "FILE", "name": "添付ファイル"},
            {"type": "SUBTABLE", "name": "テーブル"}
        ]
    }

def get_documentation_tool_description() -> str:
    """
    フィールドタイプのドキュメントツールの説明を取得する
    
    Returns:
        str: ドキュメントツールの説明
    """
    return """
# kintoneフィールドタイプドキュメントツール

このツールは、kintoneのフィールドタイプに関する詳細なドキュメントを提供します。
各フィールドタイプの仕様、プロパティ、使用例、応用例、注意事項などを確認できます。

## 重要な注意事項

### フォームレイアウトとフィールドの関係
- **通常のフィールドは、レイアウトに含める前に必ず事前に作成しておく必要があります**
- 存在しないフィールドコードをレイアウトに含めると、エラーが発生します
- システムフィールド（RECORD_NUMBER, CREATOR, MODIFIER, CREATED_TIME, UPDATED_TIME）は事前作成不要です
- レイアウト要素（LABEL, SPACER, HR）も事前作成不要です

### 推奨されるワークフロー
1. `add_fields` ツールでフィールドを作成（システムフィールドとレイアウト要素を除く）
2. `get_form_fields` ツールで作成されたフィールドを確認
3. `update_form_layout` ツールでレイアウトを更新

詳細は `get_field_type_documentation({ field_type: "LAYOUT" })` で確認できます。

## 利用可能なフィールドタイプ

### 基本フィールド
- SINGLE_LINE_TEXT（1行テキスト）
- MULTI_LINE_TEXT（複数行テキスト）
- RICH_TEXT（リッチテキスト）
- NUMBER（数値）
- CALC（計算）

### 選択フィールド
- DROP_DOWN（ドロップダウン）
- RADIO_BUTTON（ラジオボタン）
- CHECK_BOX（チェックボックス）
- MULTI_SELECT（複数選択）

### 日付・時刻フィールド
- DATE（日付）
- TIME（時刻）
- DATETIME（日時）

### 参照フィールド
- USER_SELECT（ユーザー選択）
- GROUP_SELECT（グループ選択）
- ORGANIZATION_SELECT（組織選択）
- LOOKUP（ルックアップ）
- REFERENCE_TABLE（関連テーブル）

### システムフィールド
- RECORD_NUMBER（レコード番号）
- CREATOR（作成者）
- MODIFIER（更新者）
- CREATED_TIME（作成日時）
- UPDATED_TIME（更新日時）

### その他のフィールド
- LINK（リンク）
- FILE（添付ファイル）
- SUBTABLE（テーブル）
"""

def get_field_creation_tool_description() -> str:
    """
    フィールド作成ツールの説明を取得する
    
    Returns:
        str: フィールド作成ツールの説明
    """
    return """
# kintoneフィールド作成ツール

このツールは、kintoneのフィールドを簡単に作成するためのヘルパー関数を提供します。
各フィールドタイプに特化した関数を使用して、適切なフィールド定義を生成できます。

## 重要な注意事項

### フォームレイアウトとフィールドの関係
- **通常のフィールドは、レイアウトに含める前に必ず事前に作成しておく必要があります**
- フィールド作成ツールで生成したフィールド定義は、必ず `add_fields` ツールを使用してkintoneアプリに追加してください
- レイアウト更新前に `get_form_fields` ツールを使用して、フィールドの存在を確認することを推奨します
- システムフィールド（RECORD_NUMBER, CREATOR, MODIFIER, CREATED_TIME, UPDATED_TIME）は事前作成不要です
- レイアウト要素（LABEL, SPACER, HR）も事前作成不要です

### 推奨されるワークフロー
1. フィールド作成ツールでフィールド定義を生成
2. `add_fields` ツールでフィールドをkintoneアプリに追加
3. `get_form_fields` ツールで作成されたフィールドを確認
4. `update_form_layout` ツールでレイアウトを更新

## 利用可能なツール

- create_choice_field: 選択肢フィールド（ドロップダウン、ラジオボタン、チェックボックス、複数選択）を作成
- create_lookup_field: ルックアップフィールドを作成
- create_reference_table_field: 関連テーブルフィールドを作成
- create_form_layout: フォームレイアウトを自動生成
- add_layout_element: 既存のフォームレイアウトに要素を追加
- create_group_layout: グループ要素を作成
- create_table_layout: テーブルレイアウトを作成

詳細な使用方法は各ツールのドキュメントを参照してください。
"""

# 以下、各フィールドタイプのドキュメント関数

def get_text_field_documentation(field_type: str) -> str:
    """テキストフィールドのドキュメント"""
    if field_type == 'SINGLE_LINE_TEXT':
        return """
# 1行テキストフィールド（SINGLE_LINE_TEXT）の仕様

## 概要
1行のテキストを入力するフィールドです。名前、タイトル、短い説明文など、簡潔なテキスト情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（文字列、省略可）
2. `maxLength`: 最大文字数（1-64000、省略可）
3. `minLength`: 最小文字数（0以上、省略可）
4. `unique`: 重複禁止（true/false、省略可）
5. `expression`: 自動計算式（文字列、省略可）

## 使用例

### 基本的な1行テキストフィールド
```json
{
  "type": "SINGLE_LINE_TEXT",
  "code": "title",
  "label": "タイトル",
  "required": true,
  "maxLength": 100
}
```

### 重複禁止の1行テキストフィールド
```json
{
  "type": "SINGLE_LINE_TEXT",
  "code": "product_code",
  "label": "商品コード",
  "required": true,
  "unique": true,
  "maxLength": 20
}
```

## 注意事項
1. maxLengthは1-64000の範囲で指定してください
2. uniqueをtrueにすると、同じ値のレコードは作成できません
3. expressionを指定すると、自動計算フィールドになります
"""
    else:  # MULTI_LINE_TEXT
        return """
# 複数行テキストフィールド（MULTI_LINE_TEXT）の仕様

## 概要
複数行のテキストを入力するフィールドです。長い説明文、コメント、メモなど、改行を含むテキスト情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（文字列、省略可）
2. `maxLength`: 最大文字数（1-64000、省略可）
3. `minLength`: 最小文字数（0以上、省略可）

## 使用例

### 基本的な複数行テキストフィールド
```json
{
  "type": "MULTI_LINE_TEXT",
  "code": "description",
  "label": "説明",
  "required": false,
  "maxLength": 1000
}
```

## 注意事項
1. maxLengthは1-64000の範囲で指定してください
2. 改行文字も文字数にカウントされます
3. HTMLタグは使用できません（リッチテキストが必要な場合はRICH_TEXTを使用）
"""

def get_number_field_documentation() -> str:
    """数値フィールドのドキュメント"""
    return """
# 数値フィールド（NUMBER）の仕様

## 概要
数値を入力するフィールドです。金額、数量、点数など、計算に使用する数値データを格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（数値、省略可）
2. `maxValue`: 最大値（数値、省略可）
3. `minValue`: 最小値（数値、省略可）
4. `digit`: 桁区切り表示（true/false、省略可）
5. `unique`: 重複禁止（true/false、省略可）
6. `unit`: 単位記号（文字列、省略可）
7. `unitPosition`: 単位記号の位置（"BEFORE"/"AFTER"、省略可）

## 使用例

### 基本的な数値フィールド
```json
{
  "type": "NUMBER",
  "code": "price",
  "label": "価格",
  "required": true,
  "digit": true,
  "unit": "円",
  "unitPosition": "AFTER"
}
```

### 範囲制限付きの数値フィールド
```json
{
  "type": "NUMBER",
  "code": "score",
  "label": "点数",
  "required": true,
  "minValue": 0,
  "maxValue": 100
}
```

## 注意事項
1. 小数点以下の桁数は自動的に調整されます
2. digitをtrueにすると、3桁区切りで表示されます
3. 通貨記号（¥, $, €など）はBEFORE、単位記号（kg, cm, 個など）はAFTERに配置することを推奨します
"""

def get_date_field_documentation() -> str:
    """日付フィールドのドキュメント"""
    return """
# 日付フィールド（DATE）の仕様

## 概要
日付を入力するフィールドです。誕生日、開始日、終了日など、日付情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（"YYYY-MM-DD"形式、省略可）
2. `defaultExpression`: 初期値の計算式（"TODAY"など、省略可）
3. `unique`: 重複禁止（true/false、省略可）

## 使用例

### 基本的な日付フィールド
```json
{
  "type": "DATE",
  "code": "start_date",
  "label": "開始日",
  "required": true
}
```

### 今日の日付を初期値とする日付フィールド
```json
{
  "type": "DATE",
  "code": "created_date",
  "label": "作成日",
  "required": true,
  "defaultExpression": "TODAY"
}
```

## 注意事項
1. 日付形式は"YYYY-MM-DD"で指定してください
2. defaultExpressionには"TODAY"が使用できます
3. 時刻も含める場合はDATETIMEフィールドを使用してください
"""

def get_time_field_documentation() -> str:
    """時刻フィールドのドキュメント"""
    return """
# 時刻フィールド（TIME）の仕様

## 概要
時刻を入力するフィールドです。開始時刻、終了時刻、予定時刻など、時刻情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（"HH:MM"形式、省略可）
2. `defaultExpression`: 初期値の計算式（"NOW"など、省略可）

## 使用例

### 基本的な時刻フィールド
```json
{
  "type": "TIME",
  "code": "start_time",
  "label": "開始時刻",
  "required": true
}
```

### 現在時刻を初期値とする時刻フィールド
```json
{
  "type": "TIME",
  "code": "created_time",
  "label": "作成時刻",
  "required": true,
  "defaultExpression": "NOW"
}
```

## 注意事項
1. 時刻形式は"HH:MM"で指定してください（24時間形式）
2. defaultExpressionには"NOW"が使用できます
3. 日付も含める場合はDATETIMEフィールドを使用してください
"""

def get_datetime_field_documentation() -> str:
    """日時フィールドのドキュメント"""
    return """
# 日時フィールド（DATETIME）の仕様

## 概要
日付と時刻を入力するフィールドです。イベント開始日時、締切日時、更新日時など、正確な日時情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（"YYYY-MM-DDTHH:MM:SSZ"形式、省略可）
2. `defaultExpression`: 初期値の計算式（"NOW"など、省略可）
3. `unique`: 重複禁止（true/false、省略可）

## 使用例

### 基本的な日時フィールド
```json
{
  "type": "DATETIME",
  "code": "event_datetime",
  "label": "イベント日時",
  "required": true
}
```

### 現在日時を初期値とする日時フィールド
```json
{
  "type": "DATETIME",
  "code": "updated_at",
  "label": "更新日時",
  "required": true,
  "defaultExpression": "NOW"
}
```

## 注意事項
1. 日時形式は"YYYY-MM-DDTHH:MM:SSZ"で指定してください（ISO 8601形式）
2. defaultExpressionには"NOW"が使用できます
3. タイムゾーンはkintoneの設定に従います
"""

def get_rich_text_documentation() -> str:
    """リッチテキストフィールドのドキュメント"""
    return """
# リッチエディタフィールド（RICH_TEXT）の仕様

## 概要
書式付きテキストを入力するフィールドです。太字、斜体、下線、リスト、表などの書式を設定できます。マニュアル、詳細な説明文、書式付きの議事録など、リッチなテキストコンテンツを扱うのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（HTML形式の文字列、省略可）

## 使用例

### 基本的なリッチテキストフィールド
```json
{
  "type": "RICH_TEXT",
  "code": "description",
  "label": "詳細説明",
  "required": true,
  "defaultValue": ""
}
```

### 初期値を設定したリッチテキストフィールド
```json
{
  "type": "RICH_TEXT",
  "code": "template",
  "label": "テンプレート",
  "required": false,
  "defaultValue": "<h2>見出し</h2><p>本文をここに入力してください。</p>"
}
```

## 注意事項
1. defaultValueはHTML形式の文字列で指定します
2. リッチエディタフィールドは、kintoneの画面上でWYSIWYGエディタとして表示されます
3. 入力されたデータはHTML形式で保存されます
4. HTMLタグの一部は制限されている場合があります（セキュリティ上の理由から）
"""

def get_file_field_documentation() -> str:
    """ファイルフィールドのドキュメント"""
    return """
# 添付ファイルフィールド（FILE）の仕様

## 概要
ファイルをアップロードするフィールドです。画像、文書、資料など、様々な形式のファイルを添付できます。

## 主要なプロパティ
1. `thumbnailSize`: サムネイルサイズ（"150"/"250"/"500"、省略可）

## 使用例

### 基本的な添付ファイルフィールド
```json
{
  "type": "FILE",
  "code": "attachments",
  "label": "添付ファイル",
  "required": false,
  "thumbnailSize": "150"
}
```

## 注意事項
1. アップロード可能なファイルサイズには制限があります
2. 一部のファイル形式は制限されている場合があります
3. 画像ファイルの場合、サムネイルが自動生成されます
"""

def get_user_select_documentation(field_type: str) -> str:
    """ユーザー選択フィールドのドキュメント"""
    if field_type == 'USER_SELECT':
        return """
# ユーザー選択フィールド（USER_SELECT）の仕様

## 概要
kintoneのユーザーを選択するフィールドです。担当者、承認者、作成者など、ユーザー情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（ユーザーコードの配列、省略可）
2. `entities`: 選択可能なユーザー（配列、省略可）

## 使用例

### 基本的なユーザー選択フィールド
```json
{
  "type": "USER_SELECT",
  "code": "assignee",
  "label": "担当者",
  "required": true
}
```

## 注意事項
1. 選択されたユーザーはユーザーコードで保存されます
2. 無効化されたユーザーは選択できません
"""
    elif field_type == 'GROUP_SELECT':
        return """
# グループ選択フィールド（GROUP_SELECT）の仕様

## 概要
kintoneのグループを選択するフィールドです。部署、チーム、プロジェクトグループなど、グループ情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（グループコードの配列、省略可）
2. `entities`: 選択可能なグループ（配列、省略可）

## 使用例

### 基本的なグループ選択フィールド
```json
{
  "type": "GROUP_SELECT",
  "code": "department",
  "label": "部署",
  "required": true
}
```

## 注意事項
1. 選択されたグループはグループコードで保存されます
2. 削除されたグループは選択できません
"""
    else:  # ORGANIZATION_SELECT
        return """
# 組織選択フィールド（ORGANIZATION_SELECT）の仕様

## 概要
kintoneの組織を選択するフィールドです。会社、事業部、支社など、組織情報を格納するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（組織コードの配列、省略可）
2. `entities`: 選択可能な組織（配列、省略可）

## 使用例

### 基本的な組織選択フィールド
```json
{
  "type": "ORGANIZATION_SELECT",
  "code": "organization",
  "label": "組織",
  "required": true
}
```

## 注意事項
1. 選択された組織は組織コードで保存されます
2. 削除された組織は選択できません
"""

def get_subtable_documentation() -> str:
    """テーブルフィールドのドキュメント"""
    return """
# テーブルフィールド（SUBTABLE）の仕様

## 概要
複数の行データを格納するフィールドです。明細データ、履歴データ、関連データなど、1対多の関係を表現するのに適しています。

## 主要なプロパティ
1. `fields`: テーブル内のフィールド定義（配列、必須）

## 使用例

### 基本的なテーブルフィールド
```json
{
  "type": "SUBTABLE",
  "code": "items",
  "label": "商品明細",
  "fields": {
    "item_name": {
      "type": "SINGLE_LINE_TEXT",
      "code": "item_name",
      "label": "商品名",
      "required": true
    },
    "quantity": {
      "type": "NUMBER",
      "code": "quantity",
      "label": "数量",
      "required": true
    },
    "price": {
      "type": "NUMBER",
      "code": "price",
      "label": "単価",
      "required": true
    }
  }
}
```

## 注意事項
1. テーブル内のフィールドは通常のフィールドと同様に定義します
2. テーブル内では一部のフィールドタイプが制限される場合があります
3. テーブルの行数には制限があります
"""

def get_calc_field_documentation() -> str:
    """計算フィールドのドキュメント"""
    return """
# 計算フィールド（CALC）の仕様

## 概要
他のフィールドの値を使用して自動計算を行うフィールドです。合計、平均、条件分岐など、様々な計算式を設定できます。

## 主要なプロパティ
1. `expression`: 計算式（文字列、必須）
2. `digit`: 桁区切り表示（true/false、省略可）
3. `unit`: 単位記号（文字列、省略可）
4. `unitPosition`: 単位記号の位置（"BEFORE"/"AFTER"、省略可）

## 使用例

### 基本的な計算フィールド
```json
{
  "type": "CALC",
  "code": "total",
  "label": "合計",
  "expression": "quantity * price",
  "digit": true,
  "unit": "円",
  "unitPosition": "AFTER"
}
```

## 注意事項
1. 計算式にはkintoneがサポートする関数と演算子のみ使用できます
2. 参照するフィールドは事前に作成されている必要があります
3. 計算結果は自動的に更新されます
"""

def get_choice_field_documentation(field_type: str) -> str:
    """選択肢フィールドのドキュメント"""
    if field_type == 'DROP_DOWN':
        field_name = "ドロップダウン"
        description = "プルダウンメニューから1つの選択肢を選ぶフィールドです。"
    elif field_type == 'RADIO_BUTTON':
        field_name = "ラジオボタン"
        description = "ラジオボタンから1つの選択肢を選ぶフィールドです。"
    elif field_type == 'CHECK_BOX':
        field_name = "チェックボックス"
        description = "チェックボックスから複数の選択肢を選ぶフィールドです。"
    else:  # MULTI_SELECT
        field_name = "複数選択"
        description = "リストから複数の選択肢を選ぶフィールドです。"
    
    return f"""
# {field_name}フィールド（{field_type}）の仕様

## 概要
{description}カテゴリ、ステータス、タグなど、予め定義された選択肢から選択する情報を格納するのに適しています。

## 主要なプロパティ
1. `options`: 選択肢の定義（オブジェクト、必須）
2. `defaultValue`: 初期値（選択肢の値、省略可）

## 使用例

### 基本的な{field_name}フィールド
```json
{{
  "type": "{field_type}",
  "code": "status",
  "label": "ステータス",
  "required": true,
  "options": {{
    "未着手": {{
      "label": "未着手",
      "index": "0"
    }},
    "進行中": {{
      "label": "進行中",
      "index": "1"
    }},
    "完了": {{
      "label": "完了",
      "index": "2"
    }}
  }}
}}
```

## 注意事項
1. 選択肢のキーと値は同じにすることを推奨します
2. indexは選択肢の表示順序を決定します
3. 既存の選択肢を削除する場合は注意が必要です
"""

def get_link_field_documentation() -> str:
    """リンクフィールドのドキュメント"""
    return """
# リンクフィールド（LINK）の仕様

## 概要
URLリンクを格納するフィールドです。Webサイト、ドキュメント、参考資料など、外部リンクを管理するのに適しています。

## 主要なプロパティ
1. `defaultValue`: 初期値（URL文字列、省略可）
2. `maxLength`: 最大文字数（1-64000、省略可）
3. `minLength`: 最小文字数（0以上、省略可）
4. `protocol`: プロトコル（"WEB"/"CALL"/"MAIL"、省略可）

## 使用例

### 基本的なリンクフィールド
```json
{
  "type": "LINK",
  "code": "website",
  "label": "Webサイト",
  "required": false,
  "protocol": "WEB"
}
```

## 注意事項
1. protocolを指定することで、リンクの種類を制限できます
2. WEB: http/httpsリンク、CALL: 電話番号、MAIL: メールアドレス
3. 無効なURLは入力時にエラーになります
"""

def get_lookup_documentation() -> str:
    """ルックアップフィールドのドキュメント"""
    return """
# ルックアップフィールド（LOOKUP）の仕様

## 概要
他のアプリのレコードを参照するフィールドです。マスタデータとの連携、関連情報の自動取得などに使用します。

## 重要な注意事項
ルックアップフィールドは特別なフィールドタイプではなく、基本フィールドタイプ（SINGLE_LINE_TEXT、NUMBERなど）にlookup属性を追加したものです。

## 主要なプロパティ
1. `lookup`: ルックアップ設定（オブジェクト、必須）
   - `relatedApp`: 参照先アプリ情報
   - `relatedKeyField`: 参照先キーフィールド
   - `fieldMappings`: フィールドマッピング
   - `lookupPickerFields`: ピッカー表示フィールド
   - `sort`: ソート条件

## 使用例

### 基本的なルックアップフィールド
```json
{
  "type": "SINGLE_LINE_TEXT",
  "code": "customer_name",
  "label": "顧客名",
  "lookup": {
    "relatedApp": {
      "app": "123"
    },
    "relatedKeyField": "customer_code",
    "fieldMappings": [
      {
        "field": "customer_name",
        "relatedField": "name"
      }
    ]
  }
}
```

## 注意事項
1. 参照先アプリは運用環境にデプロイされている必要があります
2. ルックアップのキーフィールド自体はフィールドマッピングに含めません
3. 参照先アプリのアクセス権限が必要です
"""

def get_reference_table_documentation() -> str:
    """関連テーブルフィールドのドキュメント"""
    return """
# 関連テーブルフィールド（REFERENCE_TABLE）の仕様

## 概要
他のアプリのレコード一覧を表示するフィールドです。関連データの一覧表示、参照情報の確認などに使用します。

## 主要なプロパティ
1. `referenceTable`: 関連テーブル設定（オブジェクト、必須）
   - `relatedApp`: 参照先アプリ情報
   - `condition`: 絞り込み条件
   - `displayFields`: 表示フィールド
   - `sort`: ソート条件

## 使用例

### 基本的な関連テーブルフィールド
```json
{
  "type": "REFERENCE_TABLE",
  "code": "related_orders",
  "label": "関連注文",
  "referenceTable": {
    "relatedApp": {
      "app": "456"
    },
    "condition": {
      "field": "customer_id",
      "relatedField": "customer_id"
    },
    "displayFields": ["order_date", "amount", "status"]
  }
}
```

## 注意事項
1. 参照先アプリは運用環境にデプロイされている必要があります
2. 絞り込み条件は適切に設定してください
3. 参照先アプリのアクセス権限が必要です
"""

def get_system_field_documentation() -> str:
    """システムフィールドのドキュメント"""
    return """
# システムフィールドの仕様

## 概要
kintoneが自動的に管理するフィールドです。レコードの作成者、更新者、作成日時、更新日時、レコード番号などの情報を自動的に記録します。

## システムフィールドの種類

### RECORD_NUMBER（レコード番号）
- レコードの一意な番号
- 自動的に採番されます

### CREATOR（作成者）
- レコードを作成したユーザー
- 自動的に設定されます

### MODIFIER（更新者）
- レコードを最後に更新したユーザー
- 自動的に更新されます

### CREATED_TIME（作成日時）
- レコードが作成された日時
- 自動的に設定されます

### UPDATED_TIME（更新日時）
- レコードが最後に更新された日時
- 自動的に更新されます

## 注意事項
1. システムフィールドは事前に作成する必要がありません
2. システムフィールドの値は自動的に設定され、手動で変更できません
3. レイアウトには自由に配置できます
"""

def get_layout_field_documentation(field_type: str) -> str:
    """レイアウトフィールドのドキュメント"""
    return """
# フォームレイアウトの仕様

## 概要
kintoneのフォームレイアウトは、フィールドの配置や表示方法を定義します。行、グループ、テーブルなどの要素を組み合わせて、使いやすいフォームを作成できます。

## レイアウト要素の種類

### ROW（行）
- フィールドを横に並べる要素
- 複数のフィールドを1行に配置できます

### GROUP（グループ）
- 関連するフィールドをまとめる要素
- 折りたたみ可能なセクションを作成できます

### SUBTABLE（テーブル）
- テーブルフィールドのレイアウト
- テーブル内のフィールド配置を定義します

### LABEL（ラベル）
- 説明文やタイトルを表示する要素
- フィールド以外のテキストを配置できます

### SPACER（スペーサー）
- 空白スペースを作る要素
- レイアウトの調整に使用します

### HR（水平線）
- 区切り線を表示する要素
- セクションの区切りに使用します

## 重要な注意事項

### フィールドとレイアウトの関係
- **通常のフィールドは、レイアウトに含める前に必ず事前に作成しておく必要があります**
- 存在しないフィールドコードをレイアウトに含めると、エラーが発生します
- システムフィールド（RECORD_NUMBER, CREATOR, MODIFIER, CREATED_TIME, UPDATED_TIME）は事前作成不要です
- レイアウト要素（LABEL, SPACER, HR）も事前作成不要です

### 推奨されるワークフロー
1. `add_fields` ツールでフィールドを作成（システムフィールドとレイアウト要素を除く）
2. `get_form_fields` ツールで作成されたフィールドを確認
3. `update_form_layout` ツールでレイアウトを更新

## 使用例

### 基本的なレイアウト
```json
{
  "layout": [
    {
      "type": "ROW",
      "fields": [
        {
          "type": "SINGLE_LINE_TEXT",
          "code": "title",
          "size": {"width": "200"}
        }
      ]
    },
    {
      "type": "GROUP",
      "code": "details",
      "label": "詳細情報",
      "layout": [
        {
          "type": "ROW",
          "fields": [
            {
              "type": "MULTI_LINE_TEXT",
              "code": "description",
              "size": {"width": "400", "innerHeight": "100"}
            }
          ]
        }
      ]
    }
  ]
}
```

## 注意事項
1. レイアウトの更新前に、必要なフィールドが作成されていることを確認してください
2. フィールドのサイズは適切に設定してください
3. グループやテーブルの入れ子構造に注意してください
"""

async def handle_documentation_tools(name: str, args: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
    """
    ドキュメント関連のツールを処理する関数
    
    Args:
        name: ツール名
        args: 引数
        
    Returns:
        Union[str, Dict[str, Any]]: ツールの実行結果
    """
    try:
        if name == 'get_field_type_documentation':
            if 'field_type' not in args:
                raise ValueError('field_type は必須パラメータです。')
            
            logger.info(f"Getting documentation for field type: {args['field_type']}")
            return get_field_type_documentation(args['field_type'])
            
        elif name == 'get_available_field_types':
            return get_available_field_types()
            
        elif name == 'get_documentation_tool_description':
            return get_documentation_tool_description()
            
        elif name == 'get_field_creation_tool_description':
            return get_field_creation_tool_description()
            
        else:
            raise ValueError(f"Unknown documentation tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in documentation tool {name}: {str(e)}")
        raise 