"""
Layout Tools Implementation

レイアウト関連のツール実装
"""

import logging
import uuid
from typing import Dict, Any, List, Optional

from .....repositories.kintone_app_repository import KintoneAppRepository
from .....utils.exceptions import KintoneAPIError

logger = logging.getLogger(__name__)


async def handle_layout_tools(name: str, args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """
    レイアウト関連ツールのハンドラ
    
    Args:
        name: ツール名
        args: ツール引数
        repository: KintoneAppRepository インスタンス
        
    Returns:
        Dict[str, Any]: ツール実行結果
        
    Raises:
        Exception: ツール実行エラー
    """
    try:
        if name == "get_form_layout":
            return await _get_form_layout(args, repository)
        elif name == "update_form_layout":
            return await _update_form_layout(args, repository)
        elif name == "create_layout_element":
            return await _create_layout_element(args, repository)
        elif name == "add_fields_to_layout":
            return await _add_fields_to_layout(args, repository)
        elif name == "remove_fields_from_layout":
            return await _remove_fields_from_layout(args, repository)
        elif name == "organize_layout":
            return await _organize_layout(args, repository)
        elif name == "create_field_group":
            return await _create_field_group(args, repository)
        elif name == "create_form_layout":
            return await _create_form_layout(args, repository)
        elif name == "add_layout_element":
            return await _add_layout_element(args, repository)
        elif name == "create_group_layout":
            return await _create_group_layout(args, repository)
        elif name == "create_table_layout":
            return await _create_table_layout(args, repository)
        else:
            raise ValueError(f"未知のレイアウトツール: {name}")
            
    except Exception as error:
        logger.error(f"Layout tool error [{name}]: {error}")
        raise


async def _get_form_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """フォームレイアウト情報を取得"""
    app_id = args["app_id"]
    preview = args.get("preview", False)
    
    result = await repository.get_form_layout(app_id, preview=preview)
    
    layout = result.get("layout", [])
    revision = result.get("revision")
    is_preview = result.get("preview", False)
    message = result.get("message", "")
    
    response_text = f"アプリ {app_id} のフォームレイアウト情報:\n\n"
    
    if is_preview:
        response_text += f"⚠️ {message}\n\n"
    
    response_text += f"リビジョン: {revision}\n"
    response_text += f"レイアウト要素数: {len(layout)}\n\n"
    
    # レイアウト構造を分析
    layout_summary = _analyze_layout_structure(layout)
    response_text += f"レイアウト構造:\n{_format_json(layout_summary)}\n\n"
    
    response_text += f"詳細なレイアウト定義:\n{_format_json(layout)}"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _update_form_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """フォームレイアウトを更新"""
    app_id = args["app_id"]
    layout = args["layout"]
    revision = args.get("revision", -1)
    
    # レイアウトを検証
    validation_errors = _validate_layout(layout)
    if validation_errors:
        raise ValueError(f"レイアウト検証エラー: {', '.join(validation_errors)}")
    
    # レイアウトを更新
    result = await repository.update_form_layout(app_id, layout, revision)
    
    response_text = f"アプリ {app_id} のフォームレイアウトを更新しました。\n\n"
    response_text += f"新しいリビジョン: {result.get('revision')}\n\n"
    response_text += "注意: レイアウト更新はプレビュー環境に反映されました。"
    response_text += "運用環境に反映するには deploy_app ツールでデプロイしてください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _create_layout_element(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """レイアウト要素を生成"""
    element_type = args["element_type"]
    config = args.get("config", {})
    
    element = _build_layout_element(element_type, config)
    
    usage_example = f"""
update_form_layout ツールでの使用例:
{{
  "app_id": 123,
  "layout": [
    {_format_json(element)},
    // ... 他のレイアウト要素
  ]
}}
"""
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"レイアウト要素を生成しました:\n\n{_format_json(element)}"
            },
            {
                "type": "text",
                "text": "注意: このツールは要素を生成するだけです。実際にレイアウトを更新するには、この結果を update_form_layout ツールに渡してください。"
            },
            {
                "type": "text",
                "text": usage_example
            }
        ]
    }


async def _add_fields_to_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """レイアウトにフィールドを追加"""
    app_id = args["app_id"]
    field_codes = args["field_codes"]
    group_fields = args.get("group_fields", False)
    revision = args.get("revision", -1)
    
    # 現在のレイアウトを取得
    layout_result = await repository.get_form_layout(app_id, preview=True)
    current_layout = layout_result.get("layout", [])
    
    # フィールドを追加
    updated_layout = current_layout.copy()
    
    if group_fields:
        # 1つの行にまとめて追加
        row_fields = []
        for field_code in field_codes:
            row_fields.append({
                "type": "FIELD",
                "code": field_code,
                "size": {"width": "200px"}
            })
        
        updated_layout.append({
            "type": "ROW",
            "fields": row_fields
        })
    else:
        # 個別の行として追加
        for field_code in field_codes:
            updated_layout.append({
                "type": "ROW",
                "fields": [{
                    "type": "FIELD",
                    "code": field_code,
                    "size": {"width": "200px"}
                }]
            })
    
    # レイアウトを更新
    result = await repository.update_form_layout(app_id, updated_layout, revision)
    
    response_text = f"アプリ {app_id} のレイアウトにフィールドを追加しました。\n\n"
    response_text += f"追加されたフィールド: {', '.join(field_codes)}\n"
    response_text += f"新しいリビジョン: {result.get('revision')}\n\n"
    response_text += "注意: レイアウト更新はプレビュー環境に反映されました。"
    response_text += "運用環境に反映するには deploy_app ツールでデプロイしてください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _remove_fields_from_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """レイアウトからフィールドを削除"""
    app_id = args["app_id"]
    field_codes = args["field_codes"]
    revision = args.get("revision", -1)
    
    # 現在のレイアウトを取得
    layout_result = await repository.get_form_layout(app_id, preview=True)
    current_layout = layout_result.get("layout", [])
    
    # フィールドを削除
    updated_layout = _remove_fields_from_layout_structure(current_layout, field_codes)
    
    # レイアウトを更新
    result = await repository.update_form_layout(app_id, updated_layout, revision)
    
    response_text = f"アプリ {app_id} のレイアウトからフィールドを削除しました。\n\n"
    response_text += f"削除されたフィールド: {', '.join(field_codes)}\n"
    response_text += f"新しいリビジョン: {result.get('revision')}\n\n"
    response_text += "注意: レイアウト更新はプレビュー環境に反映されました。"
    response_text += "運用環境に反映するには deploy_app ツールでデプロイしてください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _organize_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """レイアウトを自動整理"""
    app_id = args["app_id"]
    fields_per_row = args.get("fields_per_row", 2)
    revision = args.get("revision", -1)
    
    # フィールド情報とレイアウト情報を取得
    fields_result = await repository.get_form_fields(app_id, preview=True)
    layout_result = await repository.get_form_layout(app_id, preview=True)
    
    all_fields = fields_result.get("properties", {})
    current_layout = layout_result.get("layout", [])
    
    # レイアウトを自動整理
    organized_layout = _auto_organize_layout(all_fields, current_layout, fields_per_row)
    
    # レイアウトを更新
    result = await repository.update_form_layout(app_id, organized_layout, revision)
    
    response_text = f"アプリ {app_id} のレイアウトを自動整理しました。\n\n"
    response_text += f"1行あたりのフィールド数: {fields_per_row}\n"
    response_text += f"新しいリビジョン: {result.get('revision')}\n\n"
    response_text += "整理内容:\n"
    response_text += "• 未配置のフィールドを追加\n"
    response_text += "• 削除されたフィールドを除去\n"
    response_text += "• フィールドを指定された行数で整列\n\n"
    response_text += "注意: レイアウト更新はプレビュー環境に反映されました。"
    response_text += "運用環境に反映するには deploy_app ツールでデプロイしてください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _create_field_group(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """フィールドをグループ化"""
    app_id = args["app_id"]
    group_label = args["group_label"]
    field_codes = args["field_codes"]
    fields_per_row = args.get("fields_per_row", 2)
    revision = args.get("revision", -1)
    
    # 現在のレイアウトを取得
    layout_result = await repository.get_form_layout(app_id, preview=True)
    current_layout = layout_result.get("layout", [])
    
    # 指定されたフィールドをレイアウトから削除
    updated_layout = _remove_fields_from_layout_structure(current_layout, field_codes)
    
    # グループレイアウトを作成
    group_layout = []
    current_row = []
    
    for field_code in field_codes:
        current_row.append({
            "type": "FIELD",
            "code": field_code,
            "size": {"width": "200px"}
        })
        
        if len(current_row) >= fields_per_row:
            group_layout.append({
                "type": "ROW",
                "fields": current_row
            })
            current_row = []
    
    # 残りのフィールドがあれば追加
    if current_row:
        group_layout.append({
            "type": "ROW",
            "fields": current_row
        })
    
    # グループ要素を作成
    group_element = {
        "type": "GROUP",
        "code": f"group_{uuid.uuid4().hex[:8]}",
        "label": group_label,
        "layout": group_layout
    }
    
    # グループをレイアウトに追加
    updated_layout.append(group_element)
    
    # レイアウトを更新
    result = await repository.update_form_layout(app_id, updated_layout, revision)
    
    response_text = f"アプリ {app_id} でフィールドをグループ化しました。\n\n"
    response_text += f"グループ名: {group_label}\n"
    response_text += f"グループ化されたフィールド: {', '.join(field_codes)}\n"
    response_text += f"新しいリビジョン: {result.get('revision')}\n\n"
    response_text += "注意: レイアウト更新はプレビュー環境に反映されました。"
    response_text += "運用環境に反映するには deploy_app ツールでデプロイしてください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


def _analyze_layout_structure(layout: List[Dict[str, Any]]) -> Dict[str, Any]:
    """レイアウト構造を分析"""
    summary = {
        "total_elements": len(layout),
        "element_types": {},
        "field_count": 0,
        "groups": [],
        "subtables": []
    }
    
    for element in layout:
        element_type = element.get("type")
        summary["element_types"][element_type] = summary["element_types"].get(element_type, 0) + 1
        
        if element_type == "ROW":
            fields = element.get("fields", [])
            for field in fields:
                if field.get("type") == "FIELD":
                    summary["field_count"] += 1
        elif element_type == "GROUP":
            summary["groups"].append({
                "code": element.get("code"),
                "label": element.get("label"),
                "field_count": _count_fields_in_layout(element.get("layout", []))
            })
        elif element_type == "SUBTABLE":
            summary["subtables"].append({
                "code": element.get("code")
            })
    
    return summary


def _count_fields_in_layout(layout: List[Dict[str, Any]]) -> int:
    """レイアウト内のフィールド数をカウント"""
    count = 0
    for element in layout:
        if element.get("type") == "ROW":
            fields = element.get("fields", [])
            for field in fields:
                if field.get("type") == "FIELD":
                    count += 1
        elif element.get("type") == "GROUP":
            count += _count_fields_in_layout(element.get("layout", []))
    return count


def _validate_layout(layout: List[Dict[str, Any]]) -> List[str]:
    """レイアウトを検証"""
    errors = []
    
    for i, element in enumerate(layout):
        element_type = element.get("type")
        
        if not element_type:
            errors.append(f"要素 {i}: typeが指定されていません")
            continue
        
        if element_type == "ROW":
            fields = element.get("fields", [])
            if not fields:
                errors.append(f"ROW要素 {i}: fieldsが空です")
        elif element_type in ["SUBTABLE", "REFERENCE_TABLE"]:
            if not element.get("code"):
                errors.append(f"{element_type}要素 {i}: codeが指定されていません")
        elif element_type == "GROUP":
            if not element.get("label"):
                errors.append(f"GROUP要素 {i}: labelが指定されていません")
            layout_content = element.get("layout", [])
            if not layout_content:
                errors.append(f"GROUP要素 {i}: layoutが空です")
        elif element_type == "LABEL":
            if not element.get("label"):
                errors.append(f"LABEL要素 {i}: labelが指定されていません")
    
    return errors


def _build_layout_element(element_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """レイアウト要素を構築"""
    element = {"type": element_type}
    
    if element_type == "ROW":
        fields = config.get("fields", [])
        row_fields = []
        
        for field_config in fields:
            field_element = {
                "type": "FIELD",
                "code": field_config["code"],
                "size": {}
            }
            
            if field_config.get("width"):
                field_element["size"]["width"] = field_config["width"]
            if field_config.get("height"):
                field_element["size"]["height"] = field_config["height"]
            
            row_fields.append(field_element)
        
        element["fields"] = row_fields
        
    elif element_type in ["SUBTABLE", "REFERENCE_TABLE"]:
        element["code"] = config.get("code", "")
        
    elif element_type == "GROUP":
        element["code"] = config.get("code", f"group_{uuid.uuid4().hex[:8]}")
        element["label"] = config.get("label", "")
        element["layout"] = config.get("layout", [])
        
    elif element_type == "LABEL":
        element["label"] = config.get("label", "")
        
    elif element_type == "SPACER":
        element["elementId"] = f"spacer_{uuid.uuid4().hex[:8]}"
        if config.get("spacer_width"):
            element["size"] = {"width": config["spacer_width"]}
            
    elif element_type == "HR":
        element["elementId"] = f"hr_{uuid.uuid4().hex[:8]}"
    
    return element


def _remove_fields_from_layout_structure(layout: List[Dict[str, Any]], field_codes: List[str]) -> List[Dict[str, Any]]:
    """レイアウト構造からフィールドを削除"""
    updated_layout = []
    
    for element in layout:
        element_type = element.get("type")
        
        if element_type == "ROW":
            fields = element.get("fields", [])
            updated_fields = []
            
            for field in fields:
                if field.get("type") == "FIELD" and field.get("code") in field_codes:
                    continue  # このフィールドをスキップ
                updated_fields.append(field)
            
            # 行にフィールドが残っている場合のみ追加
            if updated_fields:
                updated_element = element.copy()
                updated_element["fields"] = updated_fields
                updated_layout.append(updated_element)
                
        elif element_type == "GROUP":
            # グループ内のレイアウトを再帰的に処理
            group_layout = element.get("layout", [])
            updated_group_layout = _remove_fields_from_layout_structure(group_layout, field_codes)
            
            # グループにレイアウトが残っている場合のみ追加
            if updated_group_layout:
                updated_element = element.copy()
                updated_element["layout"] = updated_group_layout
                updated_layout.append(updated_element)
                
        else:
            # その他の要素はそのまま追加
            updated_layout.append(element)
    
    return updated_layout


def _auto_organize_layout(all_fields: Dict[str, Any], current_layout: List[Dict[str, Any]], fields_per_row: int) -> List[Dict[str, Any]]:
    """レイアウトを自動整理"""
    # 現在レイアウトに配置されているフィールドを収集
    placed_fields = set()
    _collect_placed_fields(current_layout, placed_fields)
    
    # システムフィールドを除外
    system_fields = {
        "$id", "$revision", "作成者", "作成日時", "更新者", "更新日時",
        "CREATED_TIME", "CREATOR", "MODIFIED_TIME", "MODIFIER"
    }
    
    # 未配置のフィールドを特定
    unplaced_fields = []
    for field_code, field_info in all_fields.items():
        if field_code not in placed_fields and field_code not in system_fields:
            # レイアウト要素（SUBTABLE、REFERENCE_TABLE）は除外
            field_type = field_info.get("type")
            if field_type not in ["SUBTABLE", "REFERENCE_TABLE"]:
                unplaced_fields.append(field_code)
    
    # 既存のレイアウトから削除されたフィールドを除去
    cleaned_layout = _remove_deleted_fields_from_layout(current_layout, all_fields)
    
    # 未配置のフィールドを行に整理して追加
    organized_layout = cleaned_layout.copy()
    
    current_row = []
    for field_code in unplaced_fields:
        current_row.append({
            "type": "FIELD",
            "code": field_code,
            "size": {"width": "200px"}
        })
        
        if len(current_row) >= fields_per_row:
            organized_layout.append({
                "type": "ROW",
                "fields": current_row
            })
            current_row = []
    
    # 残りのフィールドがあれば追加
    if current_row:
        organized_layout.append({
            "type": "ROW",
            "fields": current_row
        })
    
    return organized_layout


def _collect_placed_fields(layout: List[Dict[str, Any]], placed_fields: set):
    """配置済みフィールドを収集"""
    for element in layout:
        element_type = element.get("type")
        
        if element_type == "ROW":
            fields = element.get("fields", [])
            for field in fields:
                if field.get("type") == "FIELD":
                    placed_fields.add(field.get("code"))
        elif element_type == "GROUP":
            group_layout = element.get("layout", [])
            _collect_placed_fields(group_layout, placed_fields)
        elif element_type in ["SUBTABLE", "REFERENCE_TABLE"]:
            placed_fields.add(element.get("code"))


def _remove_deleted_fields_from_layout(layout: List[Dict[str, Any]], all_fields: Dict[str, Any]) -> List[Dict[str, Any]]:
    """削除されたフィールドをレイアウトから除去"""
    cleaned_layout = []
    
    for element in layout:
        element_type = element.get("type")
        
        if element_type == "ROW":
            fields = element.get("fields", [])
            valid_fields = []
            
            for field in fields:
                if field.get("type") == "FIELD":
                    field_code = field.get("code")
                    if field_code in all_fields:
                        valid_fields.append(field)
                else:
                    valid_fields.append(field)  # SPACER等はそのまま保持
            
            if valid_fields:
                updated_element = element.copy()
                updated_element["fields"] = valid_fields
                cleaned_layout.append(updated_element)
                
        elif element_type == "GROUP":
            group_layout = element.get("layout", [])
            cleaned_group_layout = _remove_deleted_fields_from_layout(group_layout, all_fields)
            
            if cleaned_group_layout:
                updated_element = element.copy()
                updated_element["layout"] = cleaned_group_layout
                cleaned_layout.append(updated_element)
                
        elif element_type in ["SUBTABLE", "REFERENCE_TABLE"]:
            field_code = element.get("code")
            if field_code in all_fields:
                cleaned_layout.append(element)
                
        else:
            # LABEL、SPACER、HR等はそのまま保持
            cleaned_layout.append(element)
    
    return cleaned_layout


def _format_json(data: Any) -> str:
    """JSONデータを見やすい形式でフォーマット"""
    import json
    return json.dumps(data, ensure_ascii=False, indent=2)


async def _create_form_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """フィールド情報からフォームレイアウトを自動生成"""
    app_id = args["app_id"]
    fields = args["fields"]
    options = args.get("options", {})
    
    group_by_section = options.get("groupBySection", False)
    fields_per_row = options.get("fieldsPerRow", 2)
    
    # フォームレイアウトを構築
    layout = _build_form_layout(fields, {
        "groupBySection": group_by_section,
        "fieldsPerRow": fields_per_row
    })
    
    response_text = f"アプリ {app_id} 用のフォームレイアウトを生成しました。\n\n"
    response_text += f"生成されたレイアウト要素数: {len(layout)}\n"
    response_text += f"フィールド数: {len(fields)}\n"
    response_text += f"1行あたりのフィールド数: {fields_per_row}\n\n"
    
    if group_by_section:
        response_text += "セクションごとにグループ化されています。\n\n"
    
    response_text += f"生成されたレイアウト:\n{_format_json(layout)}\n\n"
    response_text += "注意: このツールはレイアウトを生成するだけです。実際に適用するには update_form_layout ツールを使用してください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _add_layout_element(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """既存のフォームレイアウトに要素を追加"""
    app_id = args["app_id"]
    element = args["element"]
    position = args.get("position", {})
    
    # 現在のレイアウトを取得
    layout_result = await repository.get_form_layout(app_id, preview=True)
    current_layout = layout_result.get("layout", [])
    
    # 要素を追加
    updated_layout = _add_element_to_layout(current_layout, element, position)
    
    response_text = f"アプリ {app_id} のレイアウトに要素を追加しました。\n\n"
    response_text += f"追加された要素:\n{_format_json(element)}\n\n"
    
    if position:
        response_text += f"挿入位置: {_format_json(position)}\n\n"
    
    response_text += f"更新されたレイアウト:\n{_format_json(updated_layout)}\n\n"
    response_text += "注意: この結果を update_form_layout ツールで適用してください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _create_group_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """グループ要素を作成"""
    code = args["code"]
    label = args["label"]
    fields = args["fields"]
    open_group = args.get("openGroup", True)
    options = args.get("options", {})
    
    fields_per_row = options.get("fieldsPerRow", 2)
    
    # グループレイアウトを構築
    group_layout = _build_group_layout(fields, {"fieldsPerRow": fields_per_row})
    
    group_element = {
        "type": "GROUP",
        "code": code,
        "label": label,
        "openGroup": open_group,
        "layout": group_layout
    }
    
    response_text = f"グループ要素を作成しました:\n\n"
    response_text += f"グループコード: {code}\n"
    response_text += f"グループラベル: {label}\n"
    response_text += f"フィールド数: {len(fields)}\n"
    response_text += f"1行あたりのフィールド数: {fields_per_row}\n"
    response_text += f"開いた状態で表示: {open_group}\n\n"
    response_text += f"生成されたグループ要素:\n{_format_json(group_element)}\n\n"
    response_text += "注意: この要素を update_form_layout ツールで適用してください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _create_table_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """テーブルレイアウトを作成"""
    rows = args["rows"]
    options = args.get("options", {})
    
    # テーブルレイアウトを構築
    table_layout = _build_table_layout(rows, options)
    
    response_text = f"テーブルレイアウトを作成しました:\n\n"
    response_text += f"行数: {len(rows)}\n"
    response_text += f"生成されたレイアウト要素数: {len(table_layout)}\n\n"
    response_text += f"生成されたテーブルレイアウト:\n{_format_json(table_layout)}\n\n"
    response_text += "注意: この結果を update_form_layout ツールで適用してください。"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


def _build_form_layout(fields: List[Dict[str, Any]], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """フィールド情報からフォームレイアウトを構築"""
    if options is None:
        options = {}
    
    group_by_section = options.get("groupBySection", False)
    fields_per_row = options.get("fieldsPerRow", 2)
    
    layout = []
    
    if group_by_section:
        # セクションごとにグループ化
        sections = {}
        for field in fields:
            section = field.get("section", "default")
            if section not in sections:
                sections[section] = []
            sections[section].append(field)
        
        for section_name, section_fields in sections.items():
            if section_name != "default":
                # セクション用のグループを作成
                group_layout = _build_section_layout(section_fields, {"fieldsPerRow": fields_per_row})
                layout.append({
                    "type": "GROUP",
                    "code": f"section_{section_name}",
                    "label": section_name,
                    "openGroup": True,
                    "layout": group_layout
                })
            else:
                # デフォルトセクションは直接配置
                section_layout = _build_section_layout(section_fields, {"fieldsPerRow": fields_per_row})
                layout.extend(section_layout)
    else:
        # 通常のレイアウト
        layout = _build_section_layout(fields, {"fieldsPerRow": fields_per_row})
    
    return layout


def _build_section_layout(fields: List[Dict[str, Any]], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """セクション用のレイアウトを構築"""
    if options is None:
        options = {}
    
    fields_per_row = options.get("fieldsPerRow", 2)
    layout = []
    
    # フィールドを行ごとに分割
    for i in range(0, len(fields), fields_per_row):
        row_fields = fields[i:i + fields_per_row]
        row_elements = []
        
        for field in row_fields:
            row_elements.append({
                "type": "FIELD",
                "code": field.get("code", ""),
                "size": {
                    "width": field.get("width", "200px")
                }
            })
        
        layout.append({
            "type": "ROW",
            "fields": row_elements
        })
    
    return layout


def _build_group_layout(fields: List[Dict[str, Any]], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """グループ用のレイアウトを構築"""
    return _build_section_layout(fields, options)


def _build_table_layout(rows: List[List[Dict[str, Any]]], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """テーブル用のレイアウトを構築"""
    layout = []
    
    for row_fields in rows:
        row_elements = []
        
        for field in row_fields:
            row_elements.append({
                "type": "FIELD",
                "code": field.get("code", ""),
                "size": {
                    "width": field.get("width", "200px")
                }
            })
        
        layout.append({
            "type": "ROW",
            "fields": row_elements
        })
    
    return layout


def _add_element_to_layout(layout: List[Dict[str, Any]], element: Dict[str, Any], position: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """レイアウトに要素を追加"""
    if position is None:
        position = {}
    
    updated_layout = layout.copy()
    
    # インデックス指定の場合
    if "index" in position:
        index = position["index"]
        if position.get("type") == "GROUP" and "groupCode" in position:
            # グループ内への挿入
            group_code = position["groupCode"]
            for layout_item in updated_layout:
                if layout_item.get("type") == "GROUP" and layout_item.get("code") == group_code:
                    if "layout" not in layout_item:
                        layout_item["layout"] = []
                    layout_item["layout"].insert(index, element)
                    break
        else:
            # トップレベルへの挿入
            updated_layout.insert(index, element)
    
    # 前後指定の場合
    elif "after" in position or "before" in position:
        target_code = position.get("after") or position.get("before")
        is_after = "after" in position
        
        def search_and_insert(items: List[Dict[str, Any]]) -> bool:
            for i, item in enumerate(items):
                if item.get("code") == target_code:
                    insert_index = i + 1 if is_after else i
                    items.insert(insert_index, element)
                    return True
                elif item.get("type") == "GROUP" and "layout" in item:
                    if search_and_insert(item["layout"]):
                        return True
                elif item.get("type") == "ROW" and "fields" in item:
                    for j, field in enumerate(item["fields"]):
                        if field.get("code") == target_code:
                            insert_index = j + 1 if is_after else j
                            item["fields"].insert(insert_index, element)
                            return True
            return False
        
        search_and_insert(updated_layout)
    
    else:
        # 位置指定なしの場合は最後に追加
        updated_layout.append(element)
    
    return updated_layout 