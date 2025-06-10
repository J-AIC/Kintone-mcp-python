"""
Field Tools Implementation

フィールド関連のツール実装
"""

import logging
import re
import time
from typing import Dict, Any, List, Optional, Union

from ....repositories.kintone_app_repository import KintoneAppRepository
from ....repositories.validators.field_validator import FieldValidator
from ....repositories.validators.constants import UNIT_POSITION_PATTERNS, LOOKUP_FIELD_MIN_WIDTH

logger = logging.getLogger(__name__)


def determine_unit_position(unit: str) -> str:
    """
    単位記号に基づいて適切な unitPosition を判定する関数
    
    Args:
        unit: 単位記号
        
    Returns:
        適切な unitPosition ("BEFORE" または "AFTER")
    """
    # 判定理由を記録する変数
    reason = ""
    
    # 単位が指定されていない場合
    if not unit:
        reason = "単位が指定されていないため"
        logger.warning(f"単位位置判定: {reason}、デフォルト値 'AFTER' を設定")
        return "AFTER"
    
    # 単位の長さが4文字以上の場合
    if len(unit) >= 4:
        reason = f"単位の長さが4文字以上 ({len(unit)}文字) のため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を設定")
        return "AFTER"
    
    # 複合単位の判定（スペースや特殊記号を含む）
    if re.search(r'[\s\/\-\+]', unit) or (len(unit) > 1 and re.search(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', unit)):
        reason = f"複合単位 \"{unit}\" と判断されるため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を設定")
        return "AFTER"
    
    # 完全一致による判定
    is_before_exact = unit in UNIT_POSITION_PATTERNS["BEFORE"]
    is_after_exact = unit in UNIT_POSITION_PATTERNS["AFTER"]
    
    # 両方のパターンに一致する場合
    if is_before_exact and is_after_exact:
        reason = f"単位 \"{unit}\" が BEFORE と AFTER の両方のパターンに一致するため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を優先設定")
        return "AFTER"
    
    # BEFOREパターンに完全一致
    if is_before_exact:
        reason = f"単位 \"{unit}\" が BEFORE パターンに完全一致するため"
        logger.warning(f"単位位置判定: {reason}、'BEFORE' を設定")
        return "BEFORE"
    
    # AFTERパターンに完全一致
    if is_after_exact:
        reason = f"単位 \"{unit}\" が AFTER パターンに完全一致するため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を設定")
        return "AFTER"
    
    # 部分一致による判定（完全一致しない場合のフォールバック）
    before_matches = [pattern for pattern in UNIT_POSITION_PATTERNS["BEFORE"] if pattern in unit]
    after_matches = [pattern for pattern in UNIT_POSITION_PATTERNS["AFTER"] if pattern in unit]
    
    # 両方のパターンに部分一致する場合
    if before_matches and after_matches:
        reason = f"単位 \"{unit}\" が BEFORE パターン [{', '.join(before_matches)}] と AFTER パターン [{', '.join(after_matches)}] の両方に部分一致するため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を優先設定")
        return "AFTER"
    
    # BEFOREパターンに部分一致
    if before_matches:
        reason = f"単位 \"{unit}\" が BEFORE パターン [{', '.join(before_matches)}] に部分一致するため"
        logger.warning(f"単位位置判定: {reason}、'BEFORE' を設定")
        return "BEFORE"
    
    # AFTERパターンに部分一致
    if after_matches:
        reason = f"単位 \"{unit}\" が AFTER パターン [{', '.join(after_matches)}] に部分一致するため"
        logger.warning(f"単位位置判定: {reason}、'AFTER' を設定")
        return "AFTER"
    
    # どのパターンにも一致しない場合
    reason = f"単位 \"{unit}\" がどのパターンにも一致しないため"
    logger.warning(f"単位位置判定: {reason}、デフォルト値 'AFTER' を設定")
    return "AFTER"


def auto_correct_unit_position(field: Dict[str, Any]) -> Dict[str, Any]:
    """
    フィールドの単位位置を自動修正する関数
    
    Args:
        field: フィールドオブジェクト
        
    Returns:
        修正されたフィールドオブジェクト
    """
    import copy
    
    # フィールドオブジェクトのディープコピーを作成
    corrected_field = copy.deepcopy(field)
    
    # NUMBER フィールドの場合
    if field.get("type") == "NUMBER" and field.get("unit") and not field.get("unitPosition"):
        # 単位記号に基づいて適切な unitPosition を判定
        corrected_field["unitPosition"] = determine_unit_position(field["unit"])
        logger.warning(f"NUMBER フィールド \"{field.get('code', '')}\" の unitPosition を \"{corrected_field['unitPosition']}\" に自動設定しました。")
    
    # CALC フィールドの場合
    if (field.get("type") == "CALC" and field.get("format") == "NUMBER" and 
        field.get("unit") and not field.get("unitPosition")):
        # 単位記号に基づいて適切な unitPosition を判定
        corrected_field["unitPosition"] = determine_unit_position(field["unit"])
        logger.warning(f"CALC フィールド \"{field.get('code', '')}\" の unitPosition を \"{corrected_field['unitPosition']}\" に自動設定しました。")
    
    # サブテーブルフィールドの場合、内部のフィールドも再帰的に処理
    if field.get("type") == "SUBTABLE" and field.get("fields"):
        # 各サブフィールドに対して自動修正を適用
        for field_key, field_def in field["fields"].items():
            corrected_field["fields"][field_key] = auto_correct_unit_position(field_def)
        logger.warning(f"SUBTABLE フィールド \"{field.get('code', '')}\" 内のフィールドの単位位置を自動修正しました。")
    
    return corrected_field


def check_unit_position_warning(unit: str, unit_position: str) -> Optional[str]:
    """
    単位記号と unitPosition の組み合わせが適切かチェックし、警告メッセージを返す関数
    
    Args:
        unit: 単位記号
        unit_position: 単位位置
        
    Returns:
        警告メッセージ（問題がなければ None）
    """
    if not unit or not unit_position:
        return None
    
    recommended_position = determine_unit_position(unit)
    
    if unit_position != recommended_position:
        examples = {
            "BEFORE": "$100, ¥100",
            "AFTER": "100円, 100%, 100kg"
        }
        
        return (f"単位記号「{unit}」には unitPosition=\"{recommended_position}\" が推奨されます。"
                f"現在の設定: \"{unit_position}\"。"
                f"例: {examples[recommended_position]}")
    
    return None


def generate_field_code_from_label(label: str) -> str:
    """
    ラベルからフィールドコードを生成する関数
    
    Args:
        label: フィールドラベル
        
    Returns:
        生成されたフィールドコード
    """
    # 英数字以外を削除し、小文字に変換
    code = re.sub(r'[^a-zA-Z0-9ぁ-んァ-ヶー一-龠々＿_･・＄￥]', '_', label).lower()
    
    # 先頭が数字の場合、先頭に 'f_' を追加
    if re.match(r'^[0-9０-９]', code):
        code = 'f_' + code
    
    # 空文字列の場合はタイムスタンプベースのコードを生成
    if not code:
        code = f"field_{int(time.time())}"
    
    return code


async def handle_field_tools(name: str, args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """
    フィールド関連のツールを処理する関数
    
    Args:
        name: ツール名
        args: 引数
        repository: アプリリポジトリ
        
    Returns:
        処理結果
    """
    if name == "add_fields":
        # 引数のチェック
        if not args.get("app_id"):
            raise ValueError("app_id は必須パラメータです。")
        
        # 不正なパラメータを除外して、実際のフィールド定義のみを抽出
        app_id = args.get("app_id")
        fields = args.get("fields", [])
        revision = args.get("revision", -1)
        
        # パラメータのクリーンアップ（不要なパラメータを除去）
        clean_args = {
            "app_id": app_id,
            "fields": fields,
            "revision": revision
        }
        
        # fieldsのバリデーション
        if not fields:
            raise ValueError("fields は必須パラメータです。")
        if not isinstance(fields, list):
            raise ValueError("fields は配列形式で指定する必要があります。")
        if len(fields) == 0:
            raise ValueError("fields には少なくとも1つのフィールド定義を指定する必要があります。")
        
        # デバッグ用のログ出力
        logger.info(f"Adding fields to app: {app_id}")
        logger.debug(f"Fields count: {len(fields)}")
        for i, field in enumerate(fields):
            logger.debug(f"Field {i+1}: {field.get('type', 'UNKNOWN')} - {field.get('label', 'No label')}")
        
        # レイアウト要素（SPACER, HR, LABEL）のチェック
        layout_element_types = ["SPACER", "HR", "LABEL"]
        for field in fields:
            if field.get("type") in layout_element_types:
                raise ValueError(
                    f"レイアウト要素 \"{field['type']}\" は add_fields ツールではサポートされていません。\n\n"
                    f"スペース、罫線、ラベルなどのレイアウト要素は、フォームのレイアウト設定で追加する必要があります。\n\n"
                    f"【代替方法】\n"
                    f"1. update_form_layout ツールを使用してフォームレイアウトを更新する\n"
                    f"2. add_layout_element ツールを使用して特定の位置にレイアウト要素を追加する\n\n"
                    f"【使用例】\n"
                    f"// スペース要素を作成\n"
                    f"const spacerElement = {{\n"
                    f"  type: \"SPACER\",\n"
                    f"  elementId: \"spacer1\",\n"
                    f"  size: {{ width: 100, height: 30 }}\n"
                    f"}};\n\n"
                    f"// レイアウトに要素を追加\n"
                    f"add_layout_element({{\n"
                    f"  app_id: {app_id},\n"
                    f"  element: spacerElement\n"
                    f"}});\n\n"
                    f"または、create_spacer_element、create_hr_element、create_label_element ツールを使用して\n"
                    f"簡単にレイアウト要素を作成することもできます。"
                )
        
        # フィールドのコード設定を確認・修正
        processed_properties = {}
        for field in fields:
            # フィールドの複製を作成（元のオブジェクトを変更しないため）
            field_copy = field.copy()
            
            # フィールドコードが指定されていない場合は自動生成
            if not field_copy.get("code"):
                # ラベルがある場合はラベルからコードを生成
                if not field_copy.get("label"):
                    raise ValueError("フィールドにはcodeまたはlabelのいずれかが必須です。")
                base_code = field_copy["label"]
                code = generate_field_code_from_label(base_code)
                field_copy["code"] = code
                logger.warning(f"フィールドコードを自動生成しました: {field_copy['code']}")
            
            # フィールドタイプが指定されていない場合はエラー
            if not field_copy.get("type"):
                raise ValueError(f"フィールド \"{field_copy.get('code', 'unknown')}\" にはタイプ(type)の指定が必須です。")
            
            # 計算フィールドの場合、formulaからexpressionへの自動変換
            if field_copy.get("type") == "CALC" and "formula" in field_copy and "expression" not in field_copy:
                field_copy["expression"] = field_copy["formula"]
                del field_copy["formula"]
                logger.warning(f"警告: 計算フィールド \"{field_copy['code']}\" の計算式は formula ではなく expression に指定してください。今回は自動的に変換しました。")
            
            # 数値フィールドの場合、displayScaleが空文字列なら削除
            if field_copy.get("type") == "NUMBER" and field_copy.get("displayScale") == "":
                del field_copy["displayScale"]
                logger.warning(f"数値フィールド \"{field_copy['code']}\" の displayScale に空文字列が指定されたため、指定を削除しました。")
            
            # 選択肢フィールドの場合、配列形式のoptionsを辞書形式に変換
            choice_field_types = ["DROP_DOWN", "RADIO_BUTTON", "CHECK_BOX", "MULTI_SELECT"]
            if field_copy.get("type") in choice_field_types and "options" in field_copy:
                options = field_copy["options"]
                
                # 配列形式の場合は辞書形式に変換
                if isinstance(options, list):
                    converted_options = {}
                    for index, option in enumerate(options):
                        if isinstance(option, dict):
                            # {"label": "顧客", "value": "customer"} 形式の場合
                            if "value" in option and "label" in option:
                                value = option["value"]
                                label = option["label"]
                                converted_options[value] = {
                                    "label": label,
                                    "index": str(index)
                                }
                            # {"label": "選択肢"} 形式の場合
                            elif "label" in option:
                                label = option["label"]
                                converted_options[label] = {
                                    "label": label,
                                    "index": str(index)
                                }
                            else:
                                raise ValueError(f"選択肢オプション {option} には 'label' または 'value' と 'label' が必要です。")
                        elif isinstance(option, str):
                            # 文字列の場合はそのまま使用
                            converted_options[option] = {
                                "label": option,
                                "index": str(index)
                            }
                        else:
                            raise ValueError(f"不正な選択肢オプション形式: {option}")
                    
                    field_copy["options"] = converted_options
                    logger.info(f"フィールド \"{field_copy['code']}\" の options を配列形式から辞書形式に変換しました。")
                
                # 既に辞書形式の場合はそのまま使用（バリデーションは後で実行）
                elif isinstance(options, dict):
                    pass
                else:
                    raise ValueError(f"フィールド \"{field_copy['code']}\" の options は配列または辞書形式で指定する必要があります。")
            
            # フィールドバリデーションを適用
            validated_field = FieldValidator.validate_field(field_copy)
            processed_properties[validated_field["code"]] = validated_field
        
        response = await repository.add_form_fields(app_id, processed_properties, revision)
        
        # 警告メッセージがある場合は結果に含める
        result = {"revision": response["revision"]}
        
        if response.get("warnings"):
            result["warnings"] = response["warnings"]
        
        return result
    
    elif name == "create_choice_field":
        # 引数のチェック
        if not args.get("field_type"):
            raise ValueError("field_type は必須パラメータです。")
        if not args.get("label"):
            raise ValueError("label は必須パラメータです。")
        if not args.get("choices"):
            raise ValueError("choices は必須パラメータです。")
        if not isinstance(args["choices"], list):
            raise ValueError("choices は配列形式で指定する必要があります。")
        
        # 有効なフィールドタイプかチェック
        valid_field_types = ["RADIO_BUTTON", "CHECK_BOX", "DROP_DOWN", "MULTI_SELECT"]
        if args["field_type"] not in valid_field_types:
            raise ValueError(f"field_type は {', '.join(valid_field_types)} のいずれかである必要があります。")
        
        # フィールドコードの自動生成
        code = args.get("code")
        if not code:
            code = generate_field_code_from_label(args["label"])
            logger.warning(f"フィールドコードを自動生成しました: {code}")
        
        field_type = args["field_type"]
        label = args["label"]
        choices = args["choices"]
        required = args.get("required", False)
        align = args.get("align", "HORIZONTAL")
        
        # デバッグ用のログ出力
        logger.info(f"Creating choice field: {code}")
        logger.debug(f"Field type: {field_type}")
        logger.debug(f"Label: {label}")
        logger.debug(f"Choices: {choices}")
        
        # options オブジェクトの生成
        options = {}
        for index, choice in enumerate(choices):
            options[choice] = {
                "label": choice,
                "index": str(index)
            }
        
        # フィールド設定の基本部分
        field_config = {
            "type": field_type,
            "code": code,
            "label": label,
            "noLabel": False,
            "required": required,
            "options": options
        }
        
        # フィールドタイプ固有の設定を追加
        if field_type == "RADIO_BUTTON":
            field_config["defaultValue"] = choices[0] if choices else ""
            field_config["align"] = align
        elif field_type == "CHECK_BOX":
            field_config["defaultValue"] = []
            field_config["align"] = align
        elif field_type == "MULTI_SELECT":
            field_config["defaultValue"] = []
        elif field_type == "DROP_DOWN":
            field_config["defaultValue"] = ""
        
        return field_config
    
    elif name == "create_reference_table_field":
        # 引数のチェック
        if not args.get("label"):
            raise ValueError("label は必須パラメータです。")
        if not args.get("conditionField"):
            raise ValueError("conditionField は必須パラメータです。")
        if not args.get("relatedConditionField"):
            raise ValueError("relatedConditionField は必須パラメータです。")
        if not args.get("relatedAppId") and not args.get("relatedAppCode"):
            raise ValueError("relatedAppId または relatedAppCode のいずれかは必須パラメータです。")
        
        # フィールドコードの自動生成
        code = args.get("code")
        if not code:
            code = generate_field_code_from_label(args["label"])
            logger.warning(f"フィールドコードを自動生成しました: {code}")
        
        label = args["label"]
        related_app_id = args.get("relatedAppId")
        related_app_code = args.get("relatedAppCode")
        condition_field = args["conditionField"]
        related_condition_field = args["relatedConditionField"]
        filter_cond = args.get("filterCond")
        display_fields = args.get("displayFields")
        sort = args.get("sort")
        size = args.get("size")
        no_label = args.get("noLabel", True)
        
        # デバッグ用のログ出力
        logger.info(f"Creating reference table field: {code}")
        logger.debug(f"Label: {label}")
        logger.debug(f"Related app: {related_app_code or related_app_id}")
        logger.debug(f"Condition: {condition_field} -> {related_condition_field}")
        
        # フィールド設定の基本部分
        field_config = {
            "type": "REFERENCE_TABLE",
            "code": code,
            "label": label,
            "noLabel": no_label,
            "referenceTable": {
                "relatedApp": {},
                "condition": {
                    "field": condition_field,
                    "relatedField": related_condition_field
                }
            }
        }
        
        # relatedApp の設定（app と code の優先順位に注意）
        if related_app_code:
            field_config["referenceTable"]["relatedApp"]["code"] = related_app_code
        if related_app_id and not related_app_code:
            field_config["referenceTable"]["relatedApp"]["app"] = related_app_id
        
        # オプション項目の追加
        if filter_cond:
            field_config["referenceTable"]["filterCond"] = filter_cond
        if display_fields and isinstance(display_fields, list):
            field_config["referenceTable"]["displayFields"] = display_fields
        if sort:
            field_config["referenceTable"]["sort"] = sort
        if size:
            field_config["referenceTable"]["size"] = str(size)  # 文字列型に変換
        
        return field_config
    
    elif name == "create_lookup_field":
        # 引数のチェック
        if not args.get("label"):
            raise ValueError("label は必須パラメータです。")
        if not args.get("relatedKeyField"):
            raise ValueError("relatedKeyField は必須パラメータです。")
        if not args.get("relatedAppId") and not args.get("relatedAppCode"):
            raise ValueError("relatedAppId または relatedAppCode のいずれかは必須パラメータです。")
        
        # フィールドコードの自動生成
        code = args.get("code")
        if not code:
            code = generate_field_code_from_label(args["label"])
            logger.warning(f"フィールドコードを自動生成しました: {code}")
        
        label = args["label"]
        related_app_id = args.get("relatedAppId")
        related_app_code = args.get("relatedAppCode")
        related_key_field = args["relatedKeyField"]
        field_mappings = args.get("fieldMappings")
        lookup_picker_fields = args.get("lookupPickerFields")
        filter_cond = args.get("filterCond")
        sort = args.get("sort")
        required = args.get("required", False)
        field_type = args.get("fieldType", "SINGLE_LINE_TEXT")  # デフォルトのフィールドタイプ
        
        # デバッグ用のログ出力
        logger.info(f"Creating lookup field: {code}")
        logger.debug(f"Label: {label}")
        logger.debug(f"Field type: {field_type}")
        logger.debug(f"Related app: {related_app_code or related_app_id}")
        logger.debug(f"Related key field: {related_key_field}")
        
        # バリデーション
        if not field_mappings or not isinstance(field_mappings, list) or not field_mappings:
            raise ValueError("fieldMappingsは少なくとも1つのマッピングを含む配列である必要があります")
        
        # フィールドマッピングの各要素をチェック
        for index, mapping in enumerate(field_mappings):
            if not mapping.get("field"):
                raise ValueError(f"fieldMappings[{index}].fieldは必須です")
            if not mapping.get("relatedField"):
                raise ValueError(f"fieldMappings[{index}].relatedFieldは必須です")
            
            # ルックアップのキー自体がマッピングに含まれていないかチェック
            if mapping["relatedField"] == related_key_field:
                raise ValueError(f"ルックアップのキーフィールド \"{related_key_field}\" はフィールドマッピングに含めないでください")
        
        # lookupPickerFieldsのチェック
        if not lookup_picker_fields or not isinstance(lookup_picker_fields, list) or not lookup_picker_fields:
            logger.warning("警告: lookupPickerFieldsが指定されていません。ルックアップピッカーに表示するフィールドを指定することを推奨します。")
        
        # sortのチェック
        if not sort:
            logger.warning("警告: sortが指定されていません。ルックアップの検索結果のソート順を指定することを推奨します。")
        
        # デバッグ用のログ出力（フィールドマッピング）
        logger.debug(f"Field mappings: {field_mappings}")
        
        # フィールド設定の基本部分
        field_config = {
            "type": field_type or "SINGLE_LINE_TEXT",  # fieldTypeが指定されていない場合はデフォルト値を使用
            "code": code,
            "label": label,
            "required": required,
            "lookup": {
                "relatedApp": {},
                "relatedKeyField": related_key_field,
                "fieldMappings": field_mappings
            }
        }
        
        # 幅の設定と補正
        # 幅が指定されていない場合、または指定された幅が最小幅より小さい場合は最小幅を設定
        size = args.get("size")
        if not size:
            field_config["size"] = {"width": LOOKUP_FIELD_MIN_WIDTH}
            logger.warning(f"ルックアップフィールド \"{code}\" の幅が指定されていないため、最小幅 {LOOKUP_FIELD_MIN_WIDTH} を設定しました。")
        elif size:
            field_config["size"] = dict(size)
            if not field_config["size"].get("width") or int(field_config["size"]["width"]) < int(LOOKUP_FIELD_MIN_WIDTH):
                field_config["size"]["width"] = LOOKUP_FIELD_MIN_WIDTH
                logger.warning(f"ルックアップフィールド \"{code}\" の幅が最小幅 {LOOKUP_FIELD_MIN_WIDTH} より小さいため、最小幅を設定しました。")
        
        # relatedApp の設定（code が優先）
        if related_app_code:
            field_config["lookup"]["relatedApp"]["code"] = related_app_code
        if related_app_id and not related_app_code:
            field_config["lookup"]["relatedApp"]["app"] = related_app_id
        
        # オプション項目の追加
        if lookup_picker_fields and isinstance(lookup_picker_fields, list):
            field_config["lookup"]["lookupPickerFields"] = lookup_picker_fields
        else:
            # デフォルトのlookupPickerFieldsを設定
            # 少なくともキーフィールドは含める
            field_config["lookup"]["lookupPickerFields"] = [related_key_field]
            logger.warning(f"lookupPickerFieldsが指定されていないため、デフォルト値 [{related_key_field}] を設定しました。")
        
        if filter_cond:
            field_config["lookup"]["filterCond"] = filter_cond
        
        if sort:
            field_config["lookup"]["sort"] = sort
        else:
            # デフォルトのsortを設定
            field_config["lookup"]["sort"] = f"{related_key_field} asc"
            logger.warning(f"sortが指定されていないため、デフォルト値 \"{related_key_field} asc\" を設定しました。")
        
        # 注意書きを追加
        logger.warning("""
【注意】ルックアップフィールドについて
- ルックアップフィールドは基本的なフィールドタイプ（SINGLE_LINE_TEXT、NUMBERなど）に、lookup属性を追加したものです
- フィールドタイプとして "LOOKUP" を指定するのではなく、適切な基本タイプを指定し、その中にlookupプロパティを設定します
- 参照先アプリは運用環境にデプロイされている必要があります
- ルックアップのキーフィールド自体はフィールドマッピングに含めないでください
- lookupPickerFieldsとsortは省略可能ですが、指定することを強く推奨します
""")
        
        return field_config
    
    elif name == "update_field":
        # 引数のチェック
        if not args.get("app_id"):
            raise ValueError("app_id は必須パラメータです。")
        if not args.get("field_code"):
            raise ValueError("field_code は必須パラメータです。")
        if not args.get("field"):
            raise ValueError("field は必須パラメータです。")
        if not isinstance(args["field"], dict):
            raise ValueError("field はオブジェクト形式で指定する必要があります。")
        
        # デバッグ用のログ出力
        logger.info(f"Updating field in app: {args['app_id']}")
        logger.debug(f"Field code: {args['field_code']}")
        logger.debug(f"Field: {args['field']}")
        
        # フィールドのタイプチェック
        if not args["field"].get("type"):
            raise ValueError(f"フィールド \"{args['field_code']}\" にはタイプ(type)の指定が必須です。")
        
        # システムフィールドタイプのチェック
        system_field_types = ["RECORD_NUMBER", "CREATOR", "MODIFIER", "CREATED_TIME", "UPDATED_TIME"]
        if args["field"]["type"] in system_field_types:
            raise ValueError(
                f"フィールドタイプ \"{args['field']['type']}\" は更新できません。これはkintoneによって自動的に作成されるシステムフィールドです。\n"
                "代替方法として、以下のようなフィールドを追加できます：\n"
                "- CREATOR（作成者）の代わりに「申請者」などの名前でUSER_SELECTフィールド\n"
                "- MODIFIER（更新者）の代わりに「承認者」などの名前でUSER_SELECTフィールド\n"
                "- CREATED_TIME（作成日時）の代わりに「申請日時」などの名前でDATETIMEフィールド\n"
                "- UPDATED_TIME（更新日時）の代わりに「承認日時」などの名前でDATETIMEフィールド\n"
                "- RECORD_NUMBER（レコード番号）の代わりに「管理番号」などの名前でSINGLE_LINE_TEXTフィールド"
            )
        
        # フィールドのバリデーション
        validated_field = FieldValidator.validate_field(args["field"])
        
        # プロパティオブジェクトの作成
        properties = {
            args["field_code"]: validated_field
        }
        
        # フィールドの更新
        response = await repository.update_form_fields(
            args["app_id"],
            properties,
            args.get("revision", -1)
        )
        
        return {
            "revision": response["revision"]
        }
    
    else:
        raise ValueError(f"未知のツール名です: {name}") 