"""
Layout utilities for kintone MCP server.

レイアウト関連のユーティリティ関数を提供します。
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from ..repositories.validators.constants import (
    LOOKUP_FIELD_MIN_WIDTH,
    SYSTEM_FIELD_TYPES
)

logger = logging.getLogger(__name__)


def auto_correct_field_width(field: Dict[str, Any], field_def: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    フィールドの幅を自動補正する関数
    
    Args:
        field: レイアウト内のフィールド要素
        field_def: フィールド定義
        
    Returns:
        補正されたフィールド要素とガイダンスメッセージを含む辞書
    """
    # フィールド要素のディープコピーを作成
    corrected_field = json.loads(json.dumps(field))
    # ガイダンスメッセージを格納する変数
    guidance = None
    
    # デバッグ情報の出力
    logger.debug(f'auto_correct_field_width: フィールド "{field.get("code")}" の幅を確認中...')
    logger.debug(f'フィールドタイプ: {field.get("type")}')
    logger.debug(f'現在の幅: {field.get("size", {}).get("width", "未指定")}')
    
    if field_def:
        field_info = {
            "type": field_def.get("type"),
            "hasLookup": "lookup" in field_def,
            "lookupInfo": {
                "relatedApp": field_def.get("lookup", {}).get("relatedApp", {}).get("app"),
                "relatedKeyField": field_def.get("lookup", {}).get("relatedKeyField")
            } if "lookup" in field_def else None
        }
        logger.debug(f'フィールド定義: {json.dumps(field_info)}')
    else:
        logger.debug('フィールド定義が見つかりません')
    
    # ルックアップフィールドの場合（lookup プロパティの有無で判断）
    if field_def and "lookup" in field_def:
        logger.debug(f'"{field.get("code")}" はルックアップフィールドです')
        
        # sizeプロパティがない場合は作成
        if "size" not in corrected_field:
            corrected_field["size"] = {}
            logger.debug(f'"{field.get("code")}" のsizeプロパティが存在しないため作成しました')
        
        # 幅が指定されていない、または最小幅より小さい場合は補正
        current_width = corrected_field["size"].get("width")
        if not current_width or int(current_width) < int(LOOKUP_FIELD_MIN_WIDTH):
            old_width = current_width or "未指定"
            corrected_field["size"]["width"] = LOOKUP_FIELD_MIN_WIDTH
            logger.debug(f'ルックアップフィールド "{field.get("code")}" の幅を {old_width} から {LOOKUP_FIELD_MIN_WIDTH} に自動補正しました。')
            
            # ガイダンスメッセージを設定
            guidance = f'ルックアップフィールド "{field.get("code")}" をフォームレイアウトに配置する際には必ず幅を指定する必要があり、その幅は {LOOKUP_FIELD_MIN_WIDTH} 以上の値を明示的に指定してください。'
            logger.debug(f'ガイダンス: {guidance}')
        else:
            logger.debug(f'ルックアップフィールド "{field.get("code")}" の幅は {current_width} で、最小幅 {LOOKUP_FIELD_MIN_WIDTH} 以上のため補正不要です。')
    else:
        logger.debug(f'"{field.get("code")}" はルックアップフィールドではありません')
    
    # 推奨幅の情報がある場合
    if field_def and "_recommendedMinWidth" in field_def:
        # sizeプロパティがない場合は作成
        if "size" not in corrected_field:
            corrected_field["size"] = {}
        
        # 幅が指定されていない、または推奨幅より小さい場合は補正
        current_width = corrected_field["size"].get("width")
        recommended_width = field_def["_recommendedMinWidth"]
        if not current_width or int(current_width) < int(recommended_width):
            old_width = current_width or "未指定"
            corrected_field["size"]["width"] = recommended_width
            logger.debug(f'フィールド "{field.get("code")}" の幅を {old_width} から {recommended_width} に自動補正しました。')
    
    return {
        "field": corrected_field,
        "guidance": guidance
    }


def auto_correct_layout_widths(layout: List[Dict[str, Any]], form_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    レイアウト全体のフィールド幅を自動補正する関数
    
    Args:
        layout: レイアウト配列
        form_fields: フォームのフィールド定義
        
    Returns:
        補正されたレイアウト配列とガイダンスメッセージの配列を含む辞書
    """
    if not layout or not isinstance(layout, list):
        return {"layout": layout, "guidances": []}
    
    # ガイダンスメッセージを収集する配列
    guidances = []
    
    def process_layout(layout_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """再帰的にレイアウトを処理する関数"""
        if not layout_items or not isinstance(layout_items, list):
            return layout_items
        
        processed_items = []
        for item in layout_items:
            # ROWの場合、内部のフィールドを処理
            if item.get("type") == "ROW" and "fields" in item:
                processed_fields = []
                for field in item["fields"]:
                    # フィールドコードからフィールド定義を取得
                    field_def = None
                    if field.get("code") and form_fields:
                        field_def = form_fields.get(field["code"])
                    
                    # フィールド幅の自動補正
                    result = auto_correct_field_width(field, field_def)
                    
                    # ガイダンスメッセージがあれば収集
                    if result["guidance"]:
                        guidances.append(result["guidance"])
                    
                    processed_fields.append(result["field"])
                
                processed_items.append({
                    **item,
                    "fields": processed_fields
                })
            
            # GROUPの場合、内部のレイアウトを再帰的に処理
            elif item.get("type") == "GROUP" and "layout" in item:
                processed_items.append({
                    **item,
                    "layout": process_layout(item["layout"])
                })
            
            else:
                processed_items.append(item)
        
        return processed_items
    
    # レイアウトを処理
    corrected_layout = process_layout(layout)
    
    return {
        "layout": corrected_layout,
        "guidances": guidances
    }


def extract_fields_from_layout(layout: List[Dict[str, Any]]) -> List[str]:
    """
    レイアウトからフィールドコードを抽出する関数
    
    Args:
        layout: レイアウト配列
        
    Returns:
        レイアウトに含まれるフィールドコードの配列
    """
    if not layout or not isinstance(layout, list):
        return []
    
    # フィールドコードを収集する配列
    field_codes = []
    
    def process_layout(layout_items: List[Dict[str, Any]]) -> None:
        """再帰的にレイアウトを処理する関数"""
        if not layout_items or not isinstance(layout_items, list):
            return
        
        for item in layout_items:
            # ROWの場合、内部のフィールドを処理
            if item.get("type") == "ROW" and "fields" in item:
                for field in item["fields"]:
                    # フィールドコードがあれば収集
                    if field.get("code"):
                        field_codes.append(field["code"])
            
            # GROUPの場合、内部のレイアウトを再帰的に処理
            elif item.get("type") == "GROUP" and "layout" in item:
                process_layout(item["layout"])
            
            # SUBTABLEの場合、テーブル自体のコードを収集
            elif item.get("type") == "SUBTABLE" and item.get("code"):
                field_codes.append(item["code"])
    
    # レイアウトを処理
    process_layout(layout)
    
    return field_codes


def validate_fields_in_layout(layout: List[Dict[str, Any]], all_fields: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    レイアウトに含まれるフィールドを検証する関数
    
    Args:
        layout: レイアウト配列
        all_fields: フォームのフィールド定義
        
    Returns:
        レイアウトに含まれていないカスタムフィールドの配列
    """
    if not all_fields:
        return []
    
    # システムフィールドを除外したカスタムフィールドのリスト
    custom_fields = [
        field_code for field_code, field in all_fields.items()
        if field.get("type") not in SYSTEM_FIELD_TYPES
    ]
    
    # レイアウトに含まれるフィールドのリストを抽出
    fields_in_layout = extract_fields_from_layout(layout)
    
    # レイアウトに含まれていないカスタムフィールドを特定
    missing_fields = [
        field_code for field_code in custom_fields
        if field_code not in fields_in_layout
    ]
    
    return missing_fields


def add_missing_fields_to_layout(
    layout: List[Dict[str, Any]], 
    all_fields: Optional[Dict[str, Any]] = None, 
    auto_fix: bool = False
) -> Dict[str, Any]:
    """
    レイアウトに含まれていないフィールドを追加する関数
    
    Args:
        layout: レイアウト配列
        all_fields: フォームのフィールド定義
        auto_fix: 自動修正を行うかどうか
        
    Returns:
        修正されたレイアウト配列と警告メッセージを含む辞書
    """
    if not all_fields:
        return {"layout": layout, "warnings": []}
    
    # レイアウトに含まれていないカスタムフィールドを特定
    missing_fields = validate_fields_in_layout(layout, all_fields)
    
    # 警告メッセージを格納する配列
    warnings = []
    
    # 不足しているフィールドがない場合はそのまま返す
    if not missing_fields:
        return {"layout": layout, "warnings": warnings}
    
    # 警告メッセージを作成
    warnings.append(f"以下のフィールドがレイアウトに含まれていません: {', '.join(missing_fields)}")
    
    # 自動修正を行わない場合はそのまま返す
    if not auto_fix:
        warnings.append("自動修正を行うには auto_fix オプションを True に設定してください。")
        return {"layout": layout, "warnings": warnings}
    
    # 不足しているフィールドを最下部に追加
    new_layout = json.loads(json.dumps(layout))
    
    # 不足しているフィールドごとに行要素を作成して追加
    for field_code in missing_fields:
        field = all_fields.get(field_code)
        if not field:
            continue
        
        # フィールドタイプに応じた処理
        if field.get("type") == "SUBTABLE":
            # テーブルの場合は直接追加
            new_layout.append({
                "type": "SUBTABLE",
                "code": field_code
            })
            warnings.append(f'テーブルフィールド "{field_code}" をレイアウトに自動追加しました。')
        else:
            # 通常のフィールドの場合は行要素として追加
            new_layout.append({
                "type": "ROW",
                "fields": [{
                    "type": field.get("type"),
                    "code": field_code
                }]
            })
            warnings.append(f'フィールド "{field_code}" をレイアウトに自動追加しました。')
    
    return {"layout": new_layout, "warnings": warnings} 