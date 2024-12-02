import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """保存 JSON 数据到文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path: Path) -> Dict[str, Any]:
    """从文件加载 JSON 数据"""
    if not file_path.exists():
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime('%H:%M:%S')

def get_iso_time() -> str:
    """获取 ISO 格式时间"""
    return datetime.now().isoformat()

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_message(content: str, msg_type: str, **kwargs) -> Dict[str, Any]:
    """创建消息对象"""
    return {
        'id': int(datetime.now().timestamp() * 1000),
        'type': msg_type,
        'content': content,
        'timestamp': get_timestamp(),
        **kwargs
    }

def create_conversation(conversation_id: str, title: str) -> Dict[str, Any]:
    """创建对话对象"""
    return {
        'id': conversation_id,
        'title': title[:20] + '...' if len(title) > 20 else title,
        'messages': [],
        'createdAt': get_iso_time(),
        'updatedAt': get_iso_time()
    } 