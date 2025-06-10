"""
App Tools Implementation

アプリ関連のツール実装
"""

import logging
from typing import Dict, Any, List, Optional

from .....repositories.kintone_app_repository import KintoneAppRepository
from .....utils.exceptions import KintoneAPIError

logger = logging.getLogger(__name__)


async def handle_app_tools(name: str, args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """
    アプリ関連ツールのハンドラ
    
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
        if name == "get_process_management":
            return await _get_process_management(args, repository)
        elif name == "get_apps_info":
            return await _get_apps_info(args, repository)
        elif name == "create_app":
            return await _create_app(args, repository)
        elif name == "deploy_app":
            return await _deploy_app(args, repository)
        elif name == "get_deploy_status":
            return await _get_deploy_status(args, repository)
        elif name == "update_app_settings":
            return await _update_app_settings(args, repository)
        elif name == "move_app_to_space":
            return await _move_app_to_space(args, repository)
        elif name == "move_app_from_space":
            return await _move_app_from_space(args, repository)
        elif name == "get_preview_app_settings":
            return await _get_preview_app_settings(args, repository)
        elif name == "get_preview_form_fields":
            return await _get_preview_form_fields(args, repository)
        elif name == "get_preview_form_layout":
            return await _get_preview_form_layout(args, repository)
        elif name == "get_app_actions":
            return await _get_app_actions(args, repository)
        elif name == "get_preview_apps":
            return await _get_preview_apps(args, repository)
        elif name == "get_preview_form":
            return await _get_preview_form(args, repository)
        elif name == "get_preview_process_management":
            return await _get_preview_process_management(args, repository)
        elif name == "get_preview_app_customization":
            return await _get_preview_app_customization(args, repository)
        elif name == "get_preview_app_views":
            return await _get_preview_app_views(args, repository)
        elif name == "get_preview_app_permissions":
            return await _get_preview_app_permissions(args, repository)
        elif name == "get_app_plugins":
            return await _get_app_plugins(args, repository)
        else:
            raise ValueError(f"未知のアプリツール: {name}")
            
    except Exception as error:
        logger.error(f"App tool error [{name}]: {error}")
        raise


async def _get_process_management(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プロセス管理設定を取得"""
    app_id = args["app_id"]
    preview = args.get("preview", False)
    
    result = await repository.get_process_management(app_id, preview)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプロセス管理設定:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_apps_info(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリ情報を取得"""
    app_name = args.get("app_name")
    
    result = await repository.get_apps_info(app_name)
    
    apps = result.get("apps", [])
    if not apps:
        if app_name:
            message = f"'{app_name}' に該当するアプリが見つかりませんでした。"
        else:
            message = "アプリが見つかりませんでした。"
        return {
            "content": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
    
    # アプリ情報を整理して表示
    app_list = []
    for app in apps:
        app_info = {
            "appId": app.get("appId"),
            "code": app.get("code"),
            "name": app.get("name"),
            "description": app.get("description", ""),
            "spaceId": app.get("spaceId"),
            "threadId": app.get("threadId"),
            "createdAt": app.get("createdAt"),
            "modifiedAt": app.get("modifiedAt")
        }
        app_list.append(app_info)
    
    if app_name:
        message = f"'{app_name}' に該当するアプリ ({len(apps)}件):\n\n{_format_json(app_list)}"
    else:
        message = f"全アプリ ({len(apps)}件):\n\n{_format_json(app_list)}"
    
    return {
        "content": [
            {
                "type": "text",
                "text": message
            }
        ]
    }


async def _create_app(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """新しいアプリを作成"""
    name = args["name"]
    space = args.get("space")
    thread = args.get("thread")
    
    result = await repository.create_app(name, space, thread)
    
    app_id = result.get("app")
    revision = result.get("revision")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ '{name}' を作成しました。\n\n"
                       f"アプリID: {app_id}\n"
                       f"リビジョン: {revision}\n\n"
                       f"注意: 作成されたアプリはプレビュー環境にあります。"
                       f"運用環境で使用するには deploy_app ツールでデプロイしてください。"
            }
        ]
    }


async def _deploy_app(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリをデプロイ"""
    apps = args["apps"]
    
    result = await repository.deploy_app(apps)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリのデプロイを開始しました。\n\n"
                       f"対象アプリ: {apps}\n\n"
                       f"デプロイ状況は get_deploy_status ツールで確認できます。"
            }
        ]
    }


async def _get_deploy_status(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """デプロイ状況を確認"""
    apps = args["apps"]
    
    result = await repository.get_deploy_status(apps)
    
    statuses = result.get("apps", [])
    
    status_text = []
    for status in statuses:
        app_id = status.get("app")
        deploy_status = status.get("status")
        status_text.append(f"アプリ {app_id}: {deploy_status}")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"デプロイ状況:\n\n" + "\n".join(status_text)
            }
        ]
    }


async def _update_app_settings(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリ設定を更新"""
    app_id = args["app_id"]
    
    # app_idを除いた設定項目を抽出
    settings = {k: v for k, v in args.items() if k != "app_id"}
    
    if not settings:
        raise ValueError("更新する設定項目を指定してください")
    
    result = await repository.update_app_settings(app_id, settings)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} の設定を更新しました。\n\n"
                       f"更新された設定:\n{_format_json(settings)}\n\n"
                       f"注意: 設定変更はプレビュー環境に反映されました。"
                       f"運用環境に反映するには deploy_app ツールでデプロイしてください。"
            }
        ]
    }


async def _move_app_to_space(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリをスペースに移動"""
    app_id = args["app_id"]
    space_id = args["space_id"]
    
    # space_idを整数に変換
    if isinstance(space_id, str):
        try:
            space_id = int(space_id)
        except ValueError:
            raise ValueError("space_idは数値で指定してください")
    
    await repository.move_app_to_space(app_id, space_id)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} をスペース {space_id} に移動しました。"
            }
        ]
    }


async def _move_app_from_space(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリをスペースから移動"""
    app_id = args["app_id"]
    
    await repository.move_app_from_space(app_id)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} をスペースに所属させないようにしました。"
            }
        ]
    }


async def _get_preview_app_settings(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のアプリ設定を取得"""
    app_id = args["app_id"]
    lang = args.get("lang")
    
    result = await repository.get_preview_app_settings(app_id, lang)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境設定:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_preview_form_fields(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のフォームフィールド情報を取得"""
    app_id = args["app_id"]
    lang = args.get("lang")
    
    result = await repository.get_form_fields(app_id, preview=True, lang=lang)
    
    properties = result.get("properties", {})
    revision = result.get("revision")
    message = result.get("message", "")
    
    response_text = f"アプリ {app_id} のプレビュー環境フィールド情報:\n\n"
    
    if message:
        response_text += f"ℹ️ {message}\n\n"
    
    response_text += f"リビジョン: {revision}\n"
    response_text += f"フィールド数: {len(properties)}\n\n"
    
    # フィールド一覧を整理して表示
    field_list = []
    for code, field in properties.items():
        field_info = {
            "code": code,
            "type": field.get("type"),
            "label": field.get("label"),
            "required": field.get("required", False)
        }
        
        # ルックアップフィールドの場合は追加情報を表示
        if field.get("lookup"):
            field_info["lookup"] = True
            lookup_info = field.get("lookup", {})
            field_info["relatedApp"] = lookup_info.get("relatedApp", {}).get("app")
            field_info["relatedKeyField"] = lookup_info.get("relatedKeyField")
        
        field_list.append(field_info)
    
    response_text += f"フィールド一覧:\n{_format_json(field_list)}"
    
    return {
        "content": [
            {
                "type": "text",
                "text": response_text
            }
        ]
    }


async def _get_preview_form_layout(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のフォームレイアウト情報を取得"""
    app_id = args["app_id"]
    
    result = await repository.get_form_layout(app_id, preview=True)
    
    layout = result.get("layout", [])
    revision = result.get("revision")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境フォームレイアウト:\n\n"
                       f"リビジョン: {revision}\n\n"
                       f"レイアウト:\n{_format_json(layout)}"
            }
        ]
    }


async def _get_app_actions(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリのアクション設定を取得"""
    app_id = args["app_id"]
    lang = args.get("lang")
    
    result = await repository.get_app_actions(app_id, lang)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のアクション設定:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_app_plugins(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """アプリのプラグイン一覧を取得"""
    app_id = args["app_id"]
    
    result = await repository.get_app_plugins(app_id)
    
    plugins = result.get("plugins", [])
    
    if not plugins:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"アプリ {app_id} にはプラグインが追加されていません。"
                }
            ]
        }
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプラグイン一覧 ({len(plugins)}件):\n\n{_format_json(plugins)}"
            }
        ]
    }


async def _get_preview_apps(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビューアプリ一覧を取得（注意：直接的な取得は不可能）"""
    result = await repository.get_preview_apps()
    
    if result.get("success") is False:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"⚠️ プレビューアプリの直接一覧取得について\n\n"
                           f"エラー: {result.get('error')}\n\n"
                           f"推奨事項: {result.get('suggestion', '')}\n\n"
                           f"プレビューアプリにアクセスするには、具体的なアプリIDを指定して "
                           f"get_preview_form_fields などの専用ツールを使用してください。"
                }
            ]
        }
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"プレビューアプリ情報:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_preview_form(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のフォーム詳細情報を取得"""
    app_id = args["app_id"]
    lang = args.get("lang")
    
    result = await repository.get_preview_form(app_id, lang)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境フォーム詳細:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_preview_process_management(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のプロセス管理設定を取得"""
    app_id = args["app_id"]
    
    result = await repository.get_preview_process_management(app_id)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境プロセス管理設定:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_preview_app_customization(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のアプリカスタマイズ設定を取得"""
    app_id = args["app_id"]
    
    result = await repository.get_preview_app_customization(app_id)
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境カスタマイズ設定:\n\n{_format_json(result)}"
            }
        ]
    }


async def _get_preview_app_views(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のアプリビュー設定を取得"""
    app_id = args["app_id"]
    lang = args.get("lang")
    
    result = await repository.get_preview_app_views(app_id, lang)
    
    views = result.get("views", {})
    revision = result.get("revision")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境ビュー設定:\n\n"
                       f"リビジョン: {revision}\n"
                       f"ビュー数: {len(views)}\n\n"
                       f"ビュー一覧:\n{_format_json(views)}"
            }
        ]
    }


async def _get_preview_app_permissions(args: Dict[str, Any], repository: KintoneAppRepository) -> Dict[str, Any]:
    """プレビュー環境のアプリ権限設定を取得"""
    app_id = args["app_id"]
    
    result = await repository.get_preview_app_permissions(app_id)
    
    rights = result.get("rights", [])
    revision = result.get("revision")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"アプリ {app_id} のプレビュー環境権限設定:\n\n"
                       f"リビジョン: {revision}\n"
                       f"権限設定数: {len(rights)}\n\n"
                       f"権限設定:\n{_format_json(rights)}"
            }
        ]
    }


def _format_json(data: Any) -> str:
    """JSONデータを見やすい形式でフォーマット"""
    import json
    return json.dumps(data, ensure_ascii=False, indent=2) 