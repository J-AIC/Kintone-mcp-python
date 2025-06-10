"""
Constants for field validation in kintone MCP server.
"""

# 文字列フィールドの定数
SINGLE_LINE_TEXT_FIELD_TYPE = 'SINGLE_LINE_TEXT'
MULTI_LINE_TEXT_FIELD_TYPE = 'MULTI_LINE_TEXT'

# 数値フィールドの定数
NUMBER_FIELD_TYPE = 'NUMBER'
VALID_UNIT_POSITIONS = ['BEFORE', 'AFTER']

# 単位位置の自動判定用パターン
UNIT_POSITION_PATTERNS = {
    # BEFORE が適切な単位記号パターン
    'BEFORE': [
        # 通貨記号
        '$', '＄', '¥', '￥', '€', '£', '₩', '₹', '฿', '₽', '₴', '₱',
        # その他の記号
        '№', '＃', '#'
    ],
    # AFTER が適切な単位記号パターン
    'AFTER': [
        # パーセント
        '%', '％',
        # 単位
        '円', 'ドル', 'ユーロ', 'ポンド', '元', 'ウォン',
        'kg', 'g', 'mg', 'μg', 'ton', 'トン',
        'm', 'km', 'cm', 'mm', 'μm', 'nm',
        'L', 'l', 'ml', 'mL', 'cc', 'kl',
        '個', '点', '枚', '本', '冊', '台', '人', '名', '社', '件', '回',
        # 時間
        '時', '分', '秒', 'h', 'hr', 'min', 'sec',
        # その他
        '度', '°', '℃', '°C', '°F', 'K', 'A', 'V', 'W', 'Hz', 'Ω'
    ]
}

# 日時フィールドの定数
DATE_FIELD_TYPE = 'DATE'
TIME_FIELD_TYPE = 'TIME'
DATETIME_FIELD_TYPE = 'DATETIME'

# リッチエディタフィールドの定数
RICH_TEXT_FIELD_TYPE = 'RICH_TEXT'

# 添付ファイルフィールドの定数
ATTACHMENT_FIELD_TYPE = 'FILE'

# ユーザー選択フィールドの定数
USER_SELECT_FIELD_TYPE = 'USER_SELECT'
GROUP_SELECT_FIELD_TYPE = 'GROUP_SELECT'
ORGANIZATION_SELECT_FIELD_TYPE = 'ORGANIZATION_SELECT'

# 選択肢フィールドの定数
FIELD_TYPES_REQUIRING_OPTIONS = [
    'CHECK_BOX',
    'RADIO_BUTTON',
    'DROP_DOWN',
    'MULTI_SELECT'
]

# 計算フィールドの定数
CALC_FIELD_TYPE = 'CALC'
CALC_FIELD_FORMATS = [
    'NUMBER',
    'NUMBER_DIGIT',
    'DATETIME',
    'DATE',
    'TIME',
    'HOUR_MINUTE',
    'DAY_HOUR_MINUTE'
]

# リンクフィールドの定数
LINK_FIELD_TYPE = 'LINK'
VALID_LINK_PROTOCOLS = ['WEB', 'CALL', 'MAIL']

# 関連テーブルフィールドの定数
REFERENCE_TABLE_FIELD_TYPE = 'REFERENCE_TABLE'

# テーブルフィールドの定数
SUBTABLE_FIELD_TYPE = 'SUBTABLE'

# ステータスフィールドの定数
STATUS_FIELD_TYPE = 'STATUS'

# 関連レコードリストフィールドの定数
RELATED_RECORDS_FIELD_TYPE = 'RELATED_RECORDS'

# レコード番号フィールドの定数
RECORD_NUMBER_FIELD_TYPE = 'RECORD_NUMBER'

# 作成者/更新者フィールドの定数
CREATOR_FIELD_TYPE = 'CREATOR'
MODIFIER_FIELD_TYPE = 'MODIFIER'
CREATED_TIME_FIELD_TYPE = 'CREATED_TIME'
UPDATED_TIME_FIELD_TYPE = 'UPDATED_TIME'

# システムフィールドの定数（レイアウトに含める必要がないフィールド）
ID_FIELD_TYPE = '__ID__'
REVISION_FIELD_TYPE = '__REVISION__'

# システムフィールドの配列
SYSTEM_FIELD_TYPES = [
    RECORD_NUMBER_FIELD_TYPE,
    ID_FIELD_TYPE,
    REVISION_FIELD_TYPE,
    CREATOR_FIELD_TYPE,
    CREATED_TIME_FIELD_TYPE,
    MODIFIER_FIELD_TYPE,
    UPDATED_TIME_FIELD_TYPE
]

# レイアウト要素の定数（コンテナ要素と特殊フィールド要素）
LAYOUT_ELEMENT_TYPES = [
    'ROW',
    'GROUP',
    'SUBTABLE',
    'LABEL',
    'SPACER',
    'HR',
    'REFERENCE_TABLE'
    # 注意: 実際のフィールドタイプ（"NUMBER"など）も有効だが、ここには含めない
]

# フィールド要素の定数（特殊タイプのみ）
SPECIAL_FIELD_ELEMENT_TYPES = [
    'LABEL',
    'SPACER',
    'HR',
    'REFERENCE_TABLE'
]

# 全てのフィールドタイプ（実際のフィールドタイプも含む）
ALL_FIELD_TYPES = [
    'SINGLE_LINE_TEXT',
    'MULTI_LINE_TEXT',
    'NUMBER',
    'DATE',
    'TIME',
    'DATETIME',
    'RICH_TEXT',
    'FILE',
    'USER_SELECT',
    'GROUP_SELECT',
    'ORGANIZATION_SELECT',
    'CHECK_BOX',
    'RADIO_BUTTON',
    'DROP_DOWN',
    'MULTI_SELECT',
    'CALC',
    'LINK',
    'REFERENCE_TABLE',
    'SUBTABLE',
    'STATUS',
    'RELATED_RECORDS',
    'RECORD_NUMBER',
    'CREATOR',
    'MODIFIER',
    'CREATED_TIME',
    'UPDATED_TIME',
    'LABEL',
    'SPACER',
    'HR'
]

# コンテナ要素の定数
CONTAINER_ELEMENT_TYPES = [
    'ROW',
    'GROUP',
    'SUBTABLE'
]

# ルックアップフィールドの最小幅
LOOKUP_FIELD_MIN_WIDTH = "250"

# kintoneのシステムフィールドのコードリスト
SYSTEM_FIELD_CODES = [
    '$id',
    '$revision',
    'レコード番号',
    '作成者',
    '作成日時',
    '更新者',
    '更新日時'
] 