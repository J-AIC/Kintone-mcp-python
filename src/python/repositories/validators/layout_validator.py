"""
レイアウトバリデーション機能
JavaScript版のLayoutValidator.jsに相当するバリデーションロジック
"""

import logging
from typing import List, Dict, Any, Optional, Union
import re

logger = logging.getLogger(__name__)


def validate_layout_element_type(element: Dict[str, Any], allowed_types: Optional[List[str]] = None) -> bool:
    """
    レイアウト要素のタイプを検証する関数
    
    Args:
        element: 検証対象の要素
        allowed_types: 許可されているタイプのリスト
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: タイプが不正な場合
    """
    # typeプロパティが指定されていない場合は自動的に補完
    if "type" not in element or element["type"] is None:
        # デフォルトのタイプを設定
        if allowed_types and len(allowed_types) > 0:
            element["type"] = allowed_types[0]  # 許可されているタイプの最初のものを使用
            logger.warning(f'レイアウト要素に type プロパティが指定されていません。自動的に "{element["type"]}" を設定します。')
        else:
            # 許可されているタイプが指定されていない場合は "ROW" をデフォルトとして使用
            element["type"] = "ROW"
            logger.warning('レイアウト要素に type プロパティが指定されていません。自動的に "ROW" を設定します。')
    
    if allowed_types and element["type"] not in allowed_types:
        raise ValueError(
            f'レイアウト要素のタイプが不正です: "{element["type"]}"\n'
            f'指定可能な値: {", ".join(allowed_types)}'
        )
    
    return True


def validate_row_element(row: Dict[str, Any]) -> bool:
    """
    ROW要素を検証する関数
    
    Args:
        row: 検証対象のROW要素
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    validate_layout_element_type(row, ["ROW"])
    
    # fieldsプロパティが指定されていない場合は自動的に補完
    if "fields" not in row or row["fields"] is None:
        row["fields"] = []
        logger.warning('ROW要素に fields プロパティが指定されていません。空の配列を設定します。')
    
    # fieldsプロパティが配列でない場合は配列に変換
    if not isinstance(row["fields"], list):
        logger.warning('ROW要素の fields プロパティが配列ではありません。自動的に配列に変換します。')
        row["fields"] = [row["fields"]]
    
    # GROUP要素が含まれる場合は、それが唯一の要素であることを確認
    group_fields = [field for field in row["fields"] if field.get("type") == "GROUP"]
    if len(group_fields) > 0 and len(row["fields"]) > len(group_fields):
        raise ValueError(
            'GROUP要素を含む行には他のフィールドを配置できません。'
            'kintoneの仕様により、グループフィールドはトップレベルに配置する必要があります。'
        )
    
    # ROW要素内にSUBTABLE要素が含まれていないことを確認
    subtable_fields = [field for field in row["fields"] if field.get("type") == "SUBTABLE"]
    if len(subtable_fields) > 0:
        raise ValueError(
            'ROW要素内にはSUBTABLE要素を配置できません。'
            'kintoneの仕様により、テーブルはトップレベルに配置する必要があります。'
        )
    
    # 各フィールド要素を検証
    for index, field in enumerate(row["fields"]):
        # フィールド要素のタイプは実際のフィールドタイプ（"NUMBER"など）または特殊タイプ（"LABEL"など）
        # 特殊タイプのみを検証し、実際のフィールドタイプは許容する
        if field.get("type") in ["LABEL", "SPACER", "HR", "REFERENCE_TABLE"]:
            validate_layout_element_type(field, ["LABEL", "SPACER", "HR", "REFERENCE_TABLE"])
        
        # フィールドタイプに応じた検証
        if field.get("type") == "LABEL":
            if not field.get("value"):
                raise ValueError(f'ROW要素内のLABEL要素[{index}]には value プロパティが必須です。')
        elif field.get("type") == "REFERENCE_TABLE":
            if not field.get("code"):
                raise ValueError(f'ROW要素内のREFERENCE_TABLE要素[{index}]には code プロパティが必須です。')
    
    return True


def validate_group_element(group: Dict[str, Any]) -> bool:
    """
    GROUP要素を検証する関数
    
    Args:
        group: 検証対象のGROUP要素
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    validate_layout_element_type(group, ["GROUP"])
    
    if not group.get("code"):
        raise ValueError('GROUP要素には code プロパティが必須です。')
    
    # fieldsプロパティが指定されている場合は明確なエラーメッセージを表示
    if "fields" in group:
        raise ValueError(
            f'GROUP要素 "{group["code"]}" には fields プロパティではなく layout プロパティを使用してください。\n'
            'GROUP要素の正しい構造:\n'
            '{\n'
            '  "type": "GROUP",\n'
            '  "code": "グループコード",\n'
            '  "label": "グループ名",\n'
            '  "layout": [] // ここに行要素を配置\n'
            '}'
        )
    
    # フィールド追加時には label プロパティが必須だが、
    # レイアウト更新時には label プロパティを省略する必要があるため、
    # ここではチェックを行わない
    
    # openGroup プロパティが指定されていない場合は True を設定
    # kintoneの仕様では省略すると False になるが、このMCP Serverでは明示的に True を設定
    if "openGroup" not in group:
        group["openGroup"] = True
        logger.warning(f'GROUP要素 "{group["code"]}" の openGroup プロパティが指定されていません。自動的に True を設定します。')
    
    # layout プロパティが存在しない場合は空の配列を設定
    if "layout" not in group:
        group["layout"] = []
        logger.warning(f'GROUP要素 "{group["code"]}" に layout プロパティが指定されていません。空の配列を設定します。')
    
    # layout プロパティが配列でない場合は配列に変換
    if not isinstance(group["layout"], list):
        logger.warning(f'GROUP要素 "{group["code"]}" の layout プロパティが配列ではありません。自動的に配列に変換します。')
        group["layout"] = [group["layout"]]
    
    # グループ内の各レイアウト要素を検証
    for index, item in enumerate(group["layout"]):
        # 先にタイプをチェックして、適切なエラーメッセージを表示
        if item.get("type") == "SUBTABLE":
            raise ValueError(
                f'GROUP要素 "{group["code"]}" 内にはSUBTABLE要素を配置できません。'
                'kintoneの仕様により、グループフィールド内にテーブルを入れることはできません。'
            )
        
        if item.get("type") == "GROUP":
            raise ValueError(
                f'GROUP要素 "{group["code"]}" 内にはGROUP要素を配置できません。'
                'kintoneの仕様により、グループフィールド内にグループフィールドを入れることはできません。'
            )
        
        # ROW要素以外は許可しない
        if item.get("type") != "ROW":
            raise ValueError(f'GROUP要素 "{group["code"]}" 内には ROW 要素のみ配置できます。')
        
        # ROW要素の場合は詳細な検証を実行
        validate_layout_element_type(item, ["ROW"])
        validate_row_element(item)
    
    return True


def validate_subtable_element(subtable: Dict[str, Any]) -> bool:
    """
    SUBTABLE要素を検証する関数
    
    Args:
        subtable: 検証対象のSUBTABLE要素
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    validate_layout_element_type(subtable, ["SUBTABLE"])
    
    if not subtable.get("code"):
        raise ValueError('SUBTABLE要素には code プロパティが必須です。')
    
    # テーブル内のフィールドを検証（テーブルのフィールド定義を取得できる場合）
    if "fields" in subtable and subtable["fields"]:
        # GROUP要素がテーブル内に含まれていないことを確認
        has_group_field = any(
            field.get("type") == "GROUP" 
            for field in subtable["fields"].values() 
            if isinstance(field, dict)
        )
        if has_group_field:
            raise ValueError(
                'SUBTABLE要素内にはGROUP要素を配置できません。'
                'kintoneの仕様により、グループフィールドはテーブル化できません。'
            )
    
    return True


def validate_form_layout(layout: List[Dict[str, Any]]) -> bool:
    """
    フォームレイアウト全体を検証する関数
    
    Args:
        layout: 検証対象のレイアウト
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    if not isinstance(layout, list):
        raise ValueError('フォームレイアウトは配列形式で指定する必要があります。')
    
    # 各レイアウト要素を検証
    for index, item in enumerate(layout):
        validate_layout_element_type(item, ["ROW", "GROUP", "SUBTABLE"])
        
        # 要素タイプに応じた検証
        if item.get("type") == "ROW":
            validate_row_element(item)
        elif item.get("type") == "GROUP":
            validate_group_element(item)
        elif item.get("type") == "SUBTABLE":
            validate_subtable_element(item)
    
    return True


def validate_field_size(size: Optional[Dict[str, Any]]) -> bool:
    """
    フィールドサイズを検証する関数
    
    Args:
        size: 検証対象のサイズ設定
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    if not size:
        return True
    
    if not isinstance(size, dict):
        raise ValueError('size はオブジェクト形式で指定する必要があります。')
    
    # 幅の検証
    if "width" in size:
        width = size["width"]
        # 文字列形式の場合は数値に変換
        if isinstance(width, str):
            # 数値以外の文字（単位など）を除去して数値のみを抽出
            numeric_part = re.sub(r'[^0-9.]', '', width)
            try:
                num_width = float(numeric_part)
            except ValueError:
                raise ValueError('size.width は数値または数値形式の文字列で指定する必要があります。')
            
            # 元の文字列に数値以外の文字が含まれていた場合は警告
            if width != numeric_part:
                logger.warning(
                    f'size.width に単位または数値以外の文字が含まれています。'
                    f'kintoneでは単位の指定はできません。数値部分のみを使用します: "{width}" → {num_width}'
                )
            else:
                logger.warning(f'size.width が文字列形式で指定されています。自動的に数値に変換しました: "{width}" → {num_width}')
            
            # 数値に変換して置き換え
            size["width"] = num_width
        elif not isinstance(width, (int, float)):
            raise ValueError('size.width は数値または数値形式の文字列で指定する必要があります。')
        
        # 有効な範囲かチェック
        if size["width"] <= 0:
            raise ValueError('size.width は正の数値で指定する必要があります。')
    
    # 高さの検証
    if "height" in size:
        height = size["height"]
        # 文字列形式の場合は数値に変換
        if isinstance(height, str):
            # 数値以外の文字（単位など）を除去して数値のみを抽出
            numeric_part = re.sub(r'[^0-9.]', '', height)
            try:
                num_height = float(numeric_part)
            except ValueError:
                raise ValueError('size.height は数値または数値形式の文字列で指定する必要があります。')
            
            # 元の文字列に数値以外の文字が含まれていた場合は警告
            if height != numeric_part:
                logger.warning(
                    f'size.height に単位または数値以外の文字が含まれています。'
                    f'kintoneでは単位の指定はできません。数値部分のみを使用します: "{height}" → {num_height}'
                )
            else:
                logger.warning(f'size.height が文字列形式で指定されています。自動的に数値に変換しました: "{height}" → {num_height}')
            
            # 数値に変換して置き換え
            size["height"] = num_height
        elif not isinstance(height, (int, float)):
            raise ValueError('size.height は数値または数値形式の文字列で指定する必要があります。')
        
        # 有効な範囲かチェック
        if size["height"] <= 0:
            raise ValueError('size.height は正の数値で指定する必要があります。')
    
    # 内部高さの検証
    if "innerHeight" in size:
        inner_height = size["innerHeight"]
        # 文字列形式の場合は数値に変換
        if isinstance(inner_height, str):
            # 数値以外の文字（単位など）を除去して数値のみを抽出
            numeric_part = re.sub(r'[^0-9.]', '', inner_height)
            try:
                num_inner_height = float(numeric_part)
            except ValueError:
                raise ValueError('size.innerHeight は数値または数値形式の文字列で指定する必要があります。')
            
            # 元の文字列に数値以外の文字が含まれていた場合は警告
            if inner_height != numeric_part:
                logger.warning(
                    f'size.innerHeight に単位または数値以外の文字が含まれています。'
                    f'kintoneでは単位の指定はできません。数値部分のみを使用します: "{inner_height}" → {num_inner_height}'
                )
            else:
                logger.warning(f'size.innerHeight が文字列形式で指定されています。自動的に数値に変換しました: "{inner_height}" → {num_inner_height}')
            
            # 数値に変換して置き換え
            size["innerHeight"] = num_inner_height
        elif not isinstance(inner_height, (int, float)):
            raise ValueError('size.innerHeight は数値または数値形式の文字列で指定する必要があります。')
        
        # 有効な範囲かチェック
        if size["innerHeight"] <= 0:
            raise ValueError('size.innerHeight は正の数値で指定する必要があります。')
    
    return True


def validate_element_position(position: Optional[Dict[str, Any]]) -> bool:
    """
    レイアウト要素の位置指定を検証する関数
    
    Args:
        position: 検証対象の位置設定
        
    Returns:
        bool: 検証結果
        
    Raises:
        ValueError: 検証エラーの場合
    """
    if not position:
        return True
    
    if not isinstance(position, dict):
        raise ValueError('position はオブジェクト形式で指定する必要があります。')
    
    # インデックス指定の検証
    if "index" in position:
        if not isinstance(position["index"], int) or position["index"] < 0:
            raise ValueError('position.index は 0 以上の整数で指定する必要があります。')
        
        # グループ内への挿入の場合
        if position.get("type") == "GROUP":
            if not position.get("groupCode"):
                raise ValueError('グループ内への挿入には position.groupCode の指定が必須です。')
    # 前後指定の検証
    elif "after" in position or "before" in position:
        if "after" in position and "before" in position:
            raise ValueError('position.after と position.before は同時に指定できません。')
        
        target_code = position.get("after") or position.get("before")
        if not target_code or not isinstance(target_code, str):
            raise ValueError('position.after または position.before には有効なフィールドコードを指定する必要があります。')
    
    return True 