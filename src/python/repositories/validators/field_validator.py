"""
Field validation utilities for kintone MCP server.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from .constants import (
    FIELD_TYPES_REQUIRING_OPTIONS,
    CALC_FIELD_TYPE,
    LINK_FIELD_TYPE,
    VALID_LINK_PROTOCOLS,
    REFERENCE_TABLE_FIELD_TYPE,
    SINGLE_LINE_TEXT_FIELD_TYPE,
    MULTI_LINE_TEXT_FIELD_TYPE,
    NUMBER_FIELD_TYPE,
    VALID_UNIT_POSITIONS,
    DATE_FIELD_TYPE,
    TIME_FIELD_TYPE,
    DATETIME_FIELD_TYPE,
    RICH_TEXT_FIELD_TYPE,
    ATTACHMENT_FIELD_TYPE,
    USER_SELECT_FIELD_TYPE,
    GROUP_SELECT_FIELD_TYPE,
    ORGANIZATION_SELECT_FIELD_TYPE,
    SUBTABLE_FIELD_TYPE,
    STATUS_FIELD_TYPE,
    RELATED_RECORDS_FIELD_TYPE,
    RECORD_NUMBER_FIELD_TYPE,
    CREATOR_FIELD_TYPE,
    MODIFIER_FIELD_TYPE,
    CREATED_TIME_FIELD_TYPE,
    UPDATED_TIME_FIELD_TYPE,
    UNIT_POSITION_PATTERNS,
    SYSTEM_FIELD_CODES,
    CALC_FIELD_FORMATS,
    LOOKUP_FIELD_MIN_WIDTH
)

logger = logging.getLogger(__name__)


class FieldValidator:
    """
    kintoneフィールドのバリデーションを行うクラス
    """
    
    # システムフィールドの代替フィールドの例
    SYSTEM_FIELD_ALTERNATIVES = {
        'RECORD_NUMBER': '「管理番号」などの名前でSINGLE_LINE_TEXTフィールドを追加できます',
        'CREATOR': '「申請者」などの名前でUSER_SELECTフィールドを追加できます',
        'MODIFIER': '「承認者」などの名前でUSER_SELECTフィールドを追加できます',
        'CREATED_TIME': '「申請日時」などの名前でDATETIMEフィールドを追加できます',
        'UPDATED_TIME': '「承認日時」などの名前でDATETIMEフィールドを追加できます'
    }
    
    # kintoneでサポートされていない関数のリスト
    UNSUPPORTED_FUNCTIONS = {
        "DAYS_BETWEEN": "日付の差分は「DATE_FORMAT(日付1, \"YYYY/MM/DD\") - DATE_FORMAT(日付2, \"YYYY/MM/DD\")」で計算できます",
        "AVERAGE": "平均値は「SUM(フィールド) / COUNT(フィールド)」で計算できます",
        "CONCATENATE": "文字列の連結は「&」演算子を使用します。例: 文字列1 & \" \" & 文字列2",
        "VLOOKUP": "参照テーブルの値を取得するには、ルックアップフィールドを使用してください",
        "COUNTIF": "条件付きカウントは「SUM(IF(条件, 1, 0))」で計算できます",
        "SUMIF": "条件付き合計は「SUM(IF(条件, 値, 0))」で計算できます",
        "TODAY": "現在の日付を取得するには、日付フィールドで「defaultNowValue: true」を設定してください",
        "NOW": "現在の日時を取得するには、日時フィールドで「defaultNowValue: true」を設定してください",
        "MONTH": "月を取得するには「DATE_FORMAT(日付, \"MM\")」を使用してください",
        "YEAR": "年を取得するには「DATE_FORMAT(日付, \"YYYY\")」を使用してください",
        "DAY": "日を取得するには「DATE_FORMAT(日付, \"DD\")」を使用してください"
    }

    @classmethod
    def validate_field(cls, field: Dict[str, Any]) -> Dict[str, Any]:
        """
        フィールドを検証し、必要に応じて自動修正を適用する関数
        
        Args:
            field: フィールドオブジェクト
            
        Returns:
            検証・修正済みのフィールドオブジェクト
        """
        # 単位位置の自動修正を適用
        corrected_field = cls._auto_correct_unit_position(field.copy())
        
        # フィールドコードの検証
        if corrected_field.get('code'):
            cls.validate_field_code(corrected_field['code'])
        
        # フィールドタイプ固有の検証
        field_type = corrected_field.get('type')
        if field_type:
            # 選択肢フィールドの検証
            if field_type in FIELD_TYPES_REQUIRING_OPTIONS:
                cls.validate_options(field_type, corrected_field.get('options'))
            
            # 計算フィールドの検証
            if field_type == CALC_FIELD_TYPE:
                cls.validate_calc_field(field_type, corrected_field.get('expression'), corrected_field)
            
            # リンクフィールドの検証
            if field_type == LINK_FIELD_TYPE:
                cls.validate_link_field(field_type, corrected_field.get('protocol'))
            
            # 関連テーブルフィールドの検証
            if field_type == REFERENCE_TABLE_FIELD_TYPE:
                cls.validate_reference_table_field(field_type, corrected_field.get('referenceTable'))
            
            # 数値フィールドの検証
            if field_type == NUMBER_FIELD_TYPE:
                cls.validate_number_field(field_type, corrected_field)
            
            # 文字列フィールドの検証
            if field_type in [SINGLE_LINE_TEXT_FIELD_TYPE, MULTI_LINE_TEXT_FIELD_TYPE]:
                cls.validate_text_field(field_type, corrected_field)
            
            # 日時フィールドの検証
            if field_type in [DATE_FIELD_TYPE, TIME_FIELD_TYPE, DATETIME_FIELD_TYPE]:
                cls.validate_datetime_field(field_type, corrected_field)
            
            # リッチエディタフィールドの検証
            if field_type == RICH_TEXT_FIELD_TYPE:
                cls.validate_rich_text_field(field_type, corrected_field)
            
            # 添付ファイルフィールドの検証
            if field_type == ATTACHMENT_FIELD_TYPE:
                cls.validate_attachment_field(field_type, corrected_field)
            
            # ユーザー選択フィールドの検証
            if field_type in [USER_SELECT_FIELD_TYPE, GROUP_SELECT_FIELD_TYPE, ORGANIZATION_SELECT_FIELD_TYPE]:
                cls.validate_user_select_field(field_type, corrected_field)
            
            # テーブルフィールドの検証
            if field_type == SUBTABLE_FIELD_TYPE:
                cls.validate_subtable_field(field_type, corrected_field)
            
            # ステータスフィールドの検証
            if field_type == STATUS_FIELD_TYPE:
                cls.validate_status_field(field_type, corrected_field)
            
            # 関連レコードリストフィールドの検証
            if field_type == RELATED_RECORDS_FIELD_TYPE:
                cls.validate_related_records_field(field_type, corrected_field)
            
            # レコード番号フィールドの検証
            if field_type == RECORD_NUMBER_FIELD_TYPE:
                cls.validate_record_number_field(field_type, corrected_field)
            
            # システムフィールドの検証
            if field_type in [CREATOR_FIELD_TYPE, MODIFIER_FIELD_TYPE, CREATED_TIME_FIELD_TYPE, UPDATED_TIME_FIELD_TYPE]:
                cls.validate_system_field(field_type, corrected_field)
            
            # LOOKUPフィールドの検証（lookupプロパティの有無で判断）
            if corrected_field.get('lookup'):
                result = cls.validate_lookup_field(field_type, corrected_field['lookup'])
                if result and result.get('_recommendedMinWidth'):
                    # 推奨最小幅の情報を追加
                    corrected_field['_recommendedMinWidth'] = result['_recommendedMinWidth']
        
        return corrected_field

    @classmethod
    def _determine_unit_position(cls, unit: str) -> str:
        """
        単位記号に基づいて適切な unitPosition を判定する関数
        
        Args:
            unit: 単位記号
            
        Returns:
            適切な unitPosition ("BEFORE" または "AFTER")
        """
        # 単位が指定されていない場合
        if not unit:
            logger.error("単位位置判定: 単位が指定されていないため、デフォルト値 \"AFTER\" を設定")
            return "AFTER"
        
        # 単位の長さが4文字以上の場合
        if len(unit) >= 4:
            logger.error(f"単位位置判定: 単位の長さが4文字以上 ({len(unit)}文字) のため、\"AFTER\" を設定")
            return "AFTER"
        
        # 複合単位の判定（スペースや特殊記号を含む）
        if re.search(r'[\s\/\-\+]', unit) or (len(unit) > 1 and re.search(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', unit)):
            logger.error(f"単位位置判定: 複合単位 \"{unit}\" と判断されるため、\"AFTER\" を設定")
            return "AFTER"
        
        # 完全一致による判定
        is_before_exact = unit in UNIT_POSITION_PATTERNS['BEFORE']
        is_after_exact = unit in UNIT_POSITION_PATTERNS['AFTER']
        
        # 両方のパターンに一致する場合
        if is_before_exact and is_after_exact:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が BEFORE と AFTER の両方のパターンに一致するため、\"AFTER\" を優先設定")
            return "AFTER"
        
        # BEFOREパターンに完全一致
        if is_before_exact:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が BEFORE パターンに完全一致するため、\"BEFORE\" を設定")
            return "BEFORE"
        
        # AFTERパターンに完全一致
        if is_after_exact:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が AFTER パターンに完全一致するため、\"AFTER\" を設定")
            return "AFTER"
        
        # 部分一致による判定（完全一致しない場合のフォールバック）
        before_matches = [pattern for pattern in UNIT_POSITION_PATTERNS['BEFORE'] if pattern in unit]
        after_matches = [pattern for pattern in UNIT_POSITION_PATTERNS['AFTER'] if pattern in unit]
        
        # 両方のパターンに部分一致する場合
        if before_matches and after_matches:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が BEFORE パターン [{', '.join(before_matches)}] と AFTER パターン [{', '.join(after_matches)}] の両方に部分一致するため、\"AFTER\" を優先設定")
            return "AFTER"
        
        # BEFOREパターンに部分一致
        if before_matches:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が BEFORE パターン [{', '.join(before_matches)}] に部分一致するため、\"BEFORE\" を設定")
            return "BEFORE"
        
        # AFTERパターンに部分一致
        if after_matches:
            logger.error(f"単位位置判定: 単位 \"{unit}\" が AFTER パターン [{', '.join(after_matches)}] に部分一致するため、\"AFTER\" を設定")
            return "AFTER"
        
        # どのパターンにも一致しない場合
        logger.error(f"単位位置判定: 単位 \"{unit}\" がどのパターンにも一致しないため、デフォルト値 \"AFTER\" を設定")
        return "AFTER"

    @classmethod
    def _auto_correct_unit_position(cls, field: Dict[str, Any]) -> Dict[str, Any]:
        """
        単位位置の自動修正を適用する関数
        
        Args:
            field: フィールドオブジェクト
            
        Returns:
            修正済みのフィールドオブジェクト
        """
        # 数値フィールドまたは計算フィールドの場合のみ処理
        if field.get('type') not in [NUMBER_FIELD_TYPE, CALC_FIELD_TYPE]:
            return field
        
        unit = field.get('unit')
        if not unit:
            return field
        
        # 現在の unitPosition を取得
        current_position = field.get('unitPosition')
        
        # 推奨される unitPosition を判定
        recommended_position = cls._determine_unit_position(unit)
        
        # unitPosition が指定されていない場合は推奨値を設定
        if not current_position:
            field['unitPosition'] = recommended_position
            logger.error(f"単位記号「{unit}」に対して unitPosition=\"{recommended_position}\" を自動設定しました")
        elif current_position != recommended_position:
            # 警告を出力するが、ユーザーの設定を尊重
            examples = {
                "BEFORE": "$100, ¥100",
                "AFTER": "100円, 100%, 100kg"
            }
            logger.warning(f"警告: 単位記号「{unit}」には unitPosition=\"{recommended_position}\" が推奨されます。"
                         f"現在の設定: \"{current_position}\"。"
                         f"例: {examples[recommended_position]}")
        
        return field

    @classmethod
    def validate_field_code(cls, field_code: str) -> bool:
        """
        フィールドコードのバリデーション
        
        Args:
            field_code: フィールドコード
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        # システムフィールドのコードと一致するかチェック
        if field_code in SYSTEM_FIELD_CODES:
            alternative = cls.SYSTEM_FIELD_ALTERNATIVES.get(field_code, '別のフィールドコードを使用してください')
            
            raise ValueError(
                f'フィールドコード "{field_code}" はkintoneのシステムフィールドとして予約されています。\n\n'
                'kintoneアプリを作成すると、以下のシステムフィールドが自動的に作成されます：\n'
                '- RECORD_NUMBER（レコード番号）\n'
                '- CREATOR（作成者）\n'
                '- MODIFIER（更新者）\n'
                '- CREATED_TIME（作成日時）\n'
                '- UPDATED_TIME（更新日時）\n\n'
                f'【代替方法】\n{alternative}'
            )
        
        valid_pattern = re.compile(r'^[a-zA-Z0-9０-９ぁ-んァ-ヶー一-龠々＿_･・＄￥]+$')
        if not valid_pattern.match(field_code):
            raise ValueError(
                f'フィールドコード "{field_code}" に使用できない文字が含まれています。\n\n'
                '使用可能な文字は以下の通りです：\n'
                '- ひらがな\n'
                '- カタカナ（半角／全角）\n'
                '- 漢字\n'
                '- 英数字（半角／全角）\n'
                '- 記号：\n'
                '  - 半角の「_」（アンダースコア）\n'
                '  - 全角の「＿」（アンダースコア）\n'
                '  - 半角の「･」（中黒）\n'
                '  - 全角の「・」（中黒）\n'
                '  - 全角の通貨記号（＄や￥など）'
            )
        return True

    @classmethod
    def validate_options(cls, field_type: str, options: Optional[Dict[str, Any]]) -> bool:
        """
        選択肢フィールドのoptionsバリデーション
        
        Args:
            field_type: フィールドタイプ
            options: 選択肢オプション
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        # 選択肢フィールドの場合のみチェック
        if field_type not in FIELD_TYPES_REQUIRING_OPTIONS:
            return True

        # optionsの必須チェック
        if not options:
            raise ValueError(
                f'フィールドタイプ "{field_type}" には options の指定が必須です。\n'
                f'以下の形式で指定してください：\n'
                f'options: {{\n'
                f'  "選択肢キー1": {{ "label": "選択肢キー1", "index": "0" }},\n'
                f'  "選択肢キー2": {{ "label": "選択肢キー2", "index": "1" }}\n'
                f'}}'
            )

        # optionsの形式チェック
        if not isinstance(options, dict):
            raise ValueError(
                'options はオブジェクト形式で指定する必要があります。\n'
                f'以下の形式で指定してください：\n'
                f'options: {{\n'
                f'  "選択肢キー1": {{ "label": "選択肢キー1", "index": "0" }},\n'
                f'  "選択肢キー2": {{ "label": "選択肢キー2", "index": "1" }}\n'
                f'}}'
            )

        # 各選択肢のバリデーション
        for key, value in options.items():
            # labelの存在チェック
            if not value.get('label'):
                raise ValueError(
                    f'選択肢 "{key}" の label が指定されていません。\n'
                    f'kintone APIの仕様により、label の指定が必要です。\n'
                    f'例: "{key}": {{ "label": "表示名", "index": "0" }}'
                )

            # labelと選択肢キーの一致チェック（警告レベル）
            if value['label'] != key:
                logger.warning(
                    f'選択肢 "{key}" のキーとlabel "{value["label"]}" が異なります。\n'
                    f'kintone APIでは通常問題ありませんが、混乱を避けるため一致させることを推奨します。'
                )

            # indexの存在チェック
            if 'index' not in value:
                raise ValueError(
                    f'選択肢 "{key}" の index が指定されていません。\n'
                    f'0以上の数値を文字列型で指定してください。\n'
                    f'例: "{key}": {{ "label": "{value.get("label", key)}", "index": "0" }}'
                )

            # indexが文字列型であることのチェック
            if not isinstance(value['index'], str):
                raise ValueError(
                    f'選択肢 "{key}" の index は文字列型の数値を指定してください。\n'
                    f'例: "{key}": {{ "label": "{value.get("label", key)}", "index": "0" }},\n'
                    f'現在の値: {type(value["index"]).__name__} 型の {value["index"]}'
                )

            # indexが数値文字列であることのチェック
            if not re.match(r'^\d+$', value['index']):
                raise ValueError(
                    f'選択肢 "{key}" の index は 0以上の整数値を文字列型で指定してください。\n'
                    f'例: "{key}": {{ "label": "{value.get("label", key)}", "index": "0" }},\n'
                    f'現在の値: "{value["index"]}"'
                )

            # indexが0以上の数値であることのチェック
            try:
                index_num = int(value['index'])
                if index_num < 0:
                    raise ValueError(
                        f'選択肢 "{key}" の index は 0以上の整数値を文字列型で指定してください。\n'
                        f'例: "{key}": {{ "label": "{value.get("label", key)}", "index": "0" }}'
                    )
            except ValueError:
                raise ValueError(
                    f'選択肢 "{key}" の index は 0以上の整数値を文字列型で指定してください。\n'
                    f'例: "{key}": {{ "label": "{value.get("label", key)}", "index": "0" }}'
                )

        return True

    @classmethod
    def _validate_expression_format(cls, expression: str) -> Dict[str, Any]:
        """
        計算式内のテーブル名.フィールド名パターンを検出して修正する関数
        
        Args:
            expression: 計算式
            
        Returns:
            検証結果 {'is_valid': bool, 'message': str, 'suggestion': str}
        """
        # 未サポート関数の検出
        for func, alternative in cls.UNSUPPORTED_FUNCTIONS.items():
            func_pattern = re.compile(f'{func}\\s*\\(', re.IGNORECASE)
            if func_pattern.search(expression):
                # DAYS_BETWEEN関数の特別処理（代替案の自動生成）
                if func == "DAYS_BETWEEN":
                    days_pattern = re.compile(r'DAYS_BETWEEN\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)', re.IGNORECASE)
                    match = days_pattern.search(expression)
                    if match:
                        date1, date2 = match.groups()
                        suggestion = days_pattern.sub(
                            f'ROUNDDOWN(DATE_FORMAT({date1}, "YYYY/MM/DD") - DATE_FORMAT({date2}, "YYYY/MM/DD"), 0)',
                            expression
                        )
                        
                        return {
                            'is_valid': False,
                            'message': f'計算式で使用されている "{func}" 関数はkintoneではサポートされていません。\n\n【代替方法】\n{alternative}\n\n【修正案】\n{suggestion}\n\nkintoneの計算フィールドでサポートされている関数の詳細は get_field_type_documentation ツールで確認できます。',
                            'suggestion': suggestion
                        }
                
                return {
                    'is_valid': False,
                    'message': f'計算式で使用されている "{func}" 関数はkintoneではサポートされていません。\n\n【代替方法】\n{alternative}\n\nkintoneの計算フィールドでサポートされている関数の詳細は get_field_type_documentation ツールで確認できます。',
                    'suggestion': None
                }

        # 数値リテラルを検出する正規表現
        number_pattern = re.compile(r'\b\d+\.\d+\b')

        # 数値リテラルを一時的に置換して保護
        number_placeholders = {}
        placeholder_count = 0
        
        def replace_number(match):
            nonlocal placeholder_count
            placeholder = f'__NUMBER_PLACEHOLDER_{placeholder_count}__'
            number_placeholders[placeholder] = match.group()
            placeholder_count += 1
            return placeholder
        
        protected_expression = number_pattern.sub(replace_number, expression)

        # テーブル名.フィールド名パターンを検出
        table_field_pattern = re.compile(r'([a-zA-Z0-9ぁ-んァ-ヶー一-龠々＿_･・＄￥]+)\.([a-zA-Z0-9ぁ-んァ-ヶー一-龠々＿_･・＄￥]+)')

        if table_field_pattern.search(protected_expression):
            # 修正案を作成
            suggestion = table_field_pattern.sub(r'\2', protected_expression)

            # プレースホルダーを元の数値に戻す
            def restore_number(match):
                placeholder = match.group()
                return number_placeholders.get(placeholder, placeholder)
            
            final_suggestion = re.sub(r'__NUMBER_PLACEHOLDER_\d+__', restore_number, suggestion)

            return {
                'is_valid': False,
                'message': f'計算式内でサブテーブル内のフィールドを参照する際は、テーブル名を指定せず、フィールドコードのみを使用してください。\n\n【誤った参照方法】\n{expression}\n\n【正しい参照方法】\n{final_suggestion}\n\nkintoneでは、フィールドコードはアプリ内で一意であるため、サブテーブル名を指定する必要はありません。',
                'suggestion': final_suggestion
            }

        # 空の計算式チェック
        if not expression or expression.strip() == '':
            return {
                'is_valid': False,
                'message': '計算式が空です。有効な計算式を指定してください。\n\n【計算式の例】\n- 数値計算: price * quantity\n- 合計計算: SUM(金額)\n- 条件分岐: IF(quantity > 10, price * 0.9, price)',
                'suggestion': None
            }
        
        return {'is_valid': True}

    @classmethod
    def validate_calc_field(cls, field_type: str, expression: Optional[str], config: Dict[str, Any]) -> bool:
        """
        計算フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            expression: 計算式
            config: フィールド設定
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type == CALC_FIELD_TYPE:
            # formulaからexpressionへの自動変換
            if config.get('formula') is not None and config.get('expression') is None:
                config['expression'] = config['formula']
                del config['formula']
                logger.error('警告: 計算フィールドの計算式は formula ではなく expression に指定してください。今回は自動的に変換しました。')
                expression = config['expression']
            
            # digit=trueの場合はformatをNUMBER_DIGITに自動設定
            if config.get('digit') is True and (not config.get('format') or config.get('format') == 'NUMBER'):
                config['format'] = 'NUMBER_DIGIT'
                logger.error('桁区切り表示が有効なため、format を "NUMBER_DIGIT" に自動設定しました。')
            
            # 計算式のチェック
            if expression is None:
                raise ValueError('計算フィールドには expression の指定が必須です。formula ではなく expression を使用してください。')
            if not isinstance(expression, str) or expression.strip() == '':
                raise ValueError('expression は空でない文字列で kintoneで使用できる計算式を指定する必要があります。')
            
            # 表示形式のチェック
            if config.get('format') is not None:
                if config['format'] not in CALC_FIELD_FORMATS:
                    raise ValueError(f'format の値が不正です: "{config["format"]}"\n指定可能な値: {", ".join(CALC_FIELD_FORMATS)}')
                
                # 数値形式の場合の追加チェック
                if config['format'] in ['NUMBER', 'NUMBER_DIGIT']:
                    # 桁区切りのチェック
                    digit = config.get('digit')
                    if digit is not None and not isinstance(digit, bool) and digit not in ['true', 'false']:
                        raise ValueError('digitはtrueまたはfalseで指定してください。')
                    
                    # 小数点以下桁数のチェック
                    display_scale = config.get('displayScale')
                    if display_scale is not None:
                        try:
                            scale = int(display_scale)
                            if scale < 0 or scale > 10:
                                raise ValueError('displayScaleは0から10までの整数で指定してください。')
                        except (ValueError, TypeError):
                            raise ValueError('displayScaleは0から10までの整数で指定してください。')
                    
                    # 単位位置のチェック
                    unit_position = config.get('unitPosition')
                    if unit_position and unit_position not in VALID_UNIT_POSITIONS:
                        raise ValueError(f'単位位置の値が不正です: "{unit_position}"\n指定可能な値: {", ".join(VALID_UNIT_POSITIONS)}')
                    
                    # 単位記号と unitPosition の組み合わせが不自然な場合は警告
                    unit = config.get('unit')
                    if unit and unit_position:
                        recommended_position = cls._determine_unit_position(unit)
                        if unit_position != recommended_position:
                            examples = {
                                "BEFORE": "$100, ¥100",
                                "AFTER": "100円, 100%, 100kg"
                            }
                            
                            logger.warning(f'警告: 単位記号「{unit}」には unitPosition="{recommended_position}" が推奨されます。'
                                         f'現在の設定: "{unit_position}"。'
                                         f'例: {examples[recommended_position]}')
            else:
                # formatが指定されていない場合はデフォルトでNUMBER_DIGITを設定
                config['format'] = 'NUMBER_DIGIT'
                logger.error('formatが指定されていないため、デフォルト値 "NUMBER_DIGIT" を設定しました。')
        
        return True

    @classmethod
    def validate_link_field(cls, field_type: str, protocol: Optional[str]) -> bool:
        """
        リンクフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            protocol: プロトコル
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type == LINK_FIELD_TYPE:
            msg = f'指定可能な値: {", ".join(VALID_LINK_PROTOCOLS)}'
            if not protocol:
                raise ValueError(f'リンクフィールドには protocol の指定が必須です。\n{msg}')
            if protocol not in VALID_LINK_PROTOCOLS:
                raise ValueError(f'protocol の値が不正です: "{protocol}"\n{msg}')
        return True

    @classmethod
    def validate_reference_table_field(cls, field_type: str, reference_table: Optional[Dict[str, Any]]) -> bool:
        """
        関連テーブルフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            reference_table: 関連テーブル設定
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type == REFERENCE_TABLE_FIELD_TYPE:
            # 必須項目のチェック
            if not reference_table:
                raise ValueError('関連テーブルフィールドには referenceTable の指定が必須です。')
            
            # relatedApp のチェック
            if not reference_table.get('relatedApp'):
                raise ValueError('関連テーブルフィールドには relatedApp の指定が必須です。')
            
            # app または code のいずれかが必要
            related_app = reference_table['relatedApp']
            if not related_app.get('app') and not related_app.get('code'):
                raise ValueError('関連テーブルフィールドには参照先アプリのIDまたはコード（relatedApp.app または relatedApp.code）の指定が必須です。')
            
            # condition のチェック
            if not reference_table.get('condition'):
                raise ValueError('関連テーブルフィールドには condition の指定が必須です。')
            
            condition = reference_table['condition']
            if not condition.get('field'):
                raise ValueError('関連テーブルフィールドには自アプリのフィールド（condition.field）の指定が必須です。')
            
            if not condition.get('relatedField'):
                raise ValueError('関連テーブルフィールドには参照先アプリのフィールド（condition.relatedField）の指定が必須です。')
            
            # size の値チェック（指定されている場合）
            size = reference_table.get('size')
            if size is not None:
                valid_sizes = ['1', '3', '5', '10', '20', '30', '40', '50', 1, 3, 5, 10, 20, 30, 40, 50]
                if size not in valid_sizes:
                    raise ValueError('関連テーブルフィールドの表示件数（size）には 1, 3, 5, 10, 20, 30, 40, 50 のいずれかを指定してください。')
        
        return True

    @classmethod
    def validate_number_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        数値フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type == NUMBER_FIELD_TYPE:
            # 桁区切りのチェック
            digit = config.get('digit')
            if digit is not None and not isinstance(digit, bool) and digit not in ['true', 'false']:
                raise ValueError('digitはtrueまたはfalseで指定してください。')
            
            # 小数点以下桁数のチェック
            display_scale = config.get('displayScale')
            if display_scale is not None:
                try:
                    scale = int(display_scale)
                    if scale < 0 or scale > 10:
                        raise ValueError('displayScaleは0から10までの整数で指定してください。')
                except (ValueError, TypeError):
                    raise ValueError('displayScaleは0から10までの整数で指定してください。')
            
            # 単位位置のチェック
            unit_position = config.get('unitPosition')
            if unit_position and unit_position not in VALID_UNIT_POSITIONS:
                raise ValueError(f'単位位置の値が不正です: "{unit_position}"\n指定可能な値: {", ".join(VALID_UNIT_POSITIONS)}')
        
        return True

    @classmethod
    def validate_text_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        文字列フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type in [SINGLE_LINE_TEXT_FIELD_TYPE, MULTI_LINE_TEXT_FIELD_TYPE]:
            # 最大文字数のチェック
            max_length = config.get('maxLength')
            if max_length is not None:
                try:
                    length = int(max_length)
                    if length < 1 or length > 64000:
                        raise ValueError('maxLengthは1から64000までの整数で指定してください。')
                except (ValueError, TypeError):
                    raise ValueError('maxLengthは1から64000までの整数で指定してください。')
        
        return True

    @classmethod
    def validate_datetime_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        日時フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
            
        Raises:
            ValueError: バリデーションエラー
        """
        if field_type in [DATE_FIELD_TYPE, TIME_FIELD_TYPE, DATETIME_FIELD_TYPE]:
            # 現在時刻の自動設定のチェック
            default_now_value = config.get('defaultNowValue')
            if default_now_value is not None and not isinstance(default_now_value, bool):
                raise ValueError('defaultNowValueはtrueまたはfalseで指定してください。')
        
        return True

    @classmethod
    def validate_rich_text_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        リッチエディタフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_attachment_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        添付ファイルフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_user_select_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        ユーザー選択フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_subtable_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        テーブルフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_status_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        ステータスフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_related_records_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        関連レコードリストフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_record_number_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        レコード番号フィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_system_field(cls, field_type: str, config: Dict[str, Any]) -> bool:
        """
        システムフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            config: フィールド設定
            
        Returns:
            バリデーション結果
        """
        # 現在は特別なバリデーションなし
        return True

    @classmethod
    def validate_lookup_field(cls, field_type: str, lookup: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        LOOKUPフィールドのバリデーション
        
        Args:
            field_type: フィールドタイプ
            lookup: ルックアップ設定
            
        Returns:
            バリデーション結果（推奨最小幅情報を含む場合がある）
        """
        if lookup:
            # 推奨最小幅の情報を返す
            return {'_recommendedMinWidth': LOOKUP_FIELD_MIN_WIDTH}
        
        return None 