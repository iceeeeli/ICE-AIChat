from flask import jsonify, Response, request
import json
import time
from datetime import datetime
import requests
from pathlib import Path
import os

# SDK 数据目录
SDK_DATA_DIR = Path(__file__).parent.parent.parent.parent / 'data' / 'sdk'
SDK_DATA_DIR.mkdir(exist_ok=True, parents=True)

# Ollama API 配置
OLLAMA_URL = "http://localhost:11434/api/generate"

def save_sdk_conversation(conversation_id: str, conversation: dict):
    """保存 SDK 对话记录"""
    file_path = SDK_DATA_DIR / f"{conversation_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)

def load_sdk_conversation(conversation_id: str) -> dict:
    """加载 SDK 对话记录"""
    file_path = SDK_DATA_DIR / f"{conversation_id}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def handle_sdk_chat(message: str, conversation_id: str, current_model: str):
    """处理 SDK 聊天请求"""
    conversation = load_sdk_conversation(conversation_id) if conversation_id else None
    
    # 如果对话存在且处于人工模式，返回特殊响应
    if conversation and conversation.get('isManualMode'):
        return jsonify({
            'error': 'conversation_in_manual_mode',
            'message': '当前对话正在人工介入中'
        }), 400
        
    # 获取或创建对话
    if not conversation_id:
        conversation_id = f"sdk_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        conversation = {
            'id': conversation_id,
            'messages': [],
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
    else:
        conversation = load_sdk_conversation(conversation_id)
        if not conversation:
            conversation = {
                'id': conversation_id,
                'messages': [],
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }

    def generate():
        # 添加用户消息
        user_message = {
            'id': int(time.time() * 1000),
            'type': 'user',
            'content': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        bot_message = {
            'id': int(time.time() * 1000) + 1,
            'type': 'bot',
            'content': '',
            'model': current_model,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }

        # 添加消息到对话
        conversation['messages'].append(user_message)
        conversation['messages'].append(bot_message)
        
        # 保存对话
        save_sdk_conversation(conversation_id, conversation)
        
        # 发送初始消息，包含会话 ID
        yield f"data: {json.dumps({'conversationId': conversation_id, 'userMessage': user_message})}\n\n"
        
        # 使用 Ollama API
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": current_model,
                "prompt": f"请用中文回答：{message}",
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_ctx": 2048,
                    "stop": ["Human:", "Assistant:"]
                }
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        chunk = data['response']
                        bot_message['content'] += chunk
                        # 更新对话中的最后一条消息
                        conversation['messages'][-1]['content'] = bot_message['content']
                        # 保存更新后的对话
                        save_sdk_conversation(conversation_id, conversation)
                        yield f"data: {json.dumps({'chunk': chunk, 'model': current_model})}\n\n"
                except json.JSONDecodeError:
                    continue
        
        # 更新对话时间戳
        conversation['updatedAt'] = datetime.now().isoformat()
        save_sdk_conversation(conversation_id, conversation)
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

def handle_manual_reply(message: str, conversation_id: str):
    """处理人工回复"""
    conversation = load_sdk_conversation(conversation_id)
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
        
    # 添加人工回复消息
    manual_message = {
        'id': int(time.time() * 1000),
        'type': 'bot',
        'content': message,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'isManual': True
    }
    
    conversation['messages'].append(manual_message)
    conversation['updatedAt'] = datetime.now().isoformat()
    save_sdk_conversation(conversation_id, conversation)
    
    return jsonify({
        'success': True,
        'message': manual_message
    })

def get_sdk_conversations():
    """获取所有 SDK 对话"""
    conversations = []
    for file_path in SDK_DATA_DIR.glob('*.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
            # 获取最后一条用户消息作为标题
            title = next(
                (msg['content'] for msg in reversed(conversation['messages']) 
                 if msg['type'] == 'user'),
                '新对话'
            )
            conversations.append({
                'id': conversation['id'],
                'title': title[:20] + '...' if len(title) > 20 else title,
                'updatedAt': conversation['updatedAt']
            })
    return sorted(conversations, key=lambda x: x['updatedAt'], reverse=True)

def set_conversation_mode(conversation_id: str, is_manual: bool):
    """设置对话模式"""
    conversation = load_sdk_conversation(conversation_id)
    if not conversation:
        return jsonify({'error': '对话不存在'}), 404
        
    # 添加或更新模式标记
    conversation['isManualMode'] = is_manual
    save_sdk_conversation(conversation_id, conversation)
    
    return jsonify({
        'success': True,
        'isManualMode': is_manual
    }) 