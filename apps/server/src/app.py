from flask import Flask, request, Response, jsonify
import json
import time
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import know
import hashlib
import hmac
import base64

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)

# 创建数据目录
DATA_DIR = Path(__file__).parent.parent.parent.parent / 'data'
SDK_DATA_DIR = DATA_DIR / 'sdk'  # 添加 SDK 数据目录
DATA_DIR.mkdir(exist_ok=True)
SDK_DATA_DIR.mkdir(exist_ok=True)  # 创建 SDK 数据目录

# Ollama API 配置
OLLAMA_URL = "http://localhost:11434/api/generate"

# 允许的文件类型
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx'}

# 添加全局变量存储当前模型
CURRENT_MODEL = "mistral"

# 添加百度模型配置
BAIDU_API_KEY = "130ICAKPnBy3RH45Xuz0a0e8"
BAIDU_SECRET_KEY = "L2aNUJKhOOA6K8aP12bW4PBeksvhQYge"
BAIDU_ACCESS_TOKEN = None
BAIDU_TOKEN_EXPIRE_TIME = 0

# 修改全局变量
CURRENT_MODEL = "mistral"  # 默认模型
MODEL_TYPES = {
    "mistral": "ollama",
    "qwen2-7b": "ollama",
    "ernie-3.5-128k": "baidu"
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_conversation(conversation_id: str, conversation: dict):
    file_path = DATA_DIR / f"{conversation_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)

def load_conversation(conversation_id: str) -> dict:
    file_path = DATA_DIR / f"{conversation_id}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_all_conversations() -> list:
    conversations = []
    for file_path in DATA_DIR.glob('*.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            conversations.append(json.load(f))
    return sorted(conversations, key=lambda x: x['updatedAt'], reverse=True)

def get_baidu_access_token():
    """获取百度 API 访问令牌"""
    global BAIDU_ACCESS_TOKEN, BAIDU_TOKEN_EXPIRE_TIME
    
    # 如果令牌还有效，直接返回
    if BAIDU_ACCESS_TOKEN and time.time() < BAIDU_TOKEN_EXPIRE_TIME:
        return BAIDU_ACCESS_TOKEN
    
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        'grant_type': 'client_credentials',
        'client_id': BAIDU_API_KEY,
        'client_secret': BAIDU_SECRET_KEY
    }
    
    response = requests.post(url, params=params)
    result = response.json()
    
    if 'access_token' in result:
        BAIDU_ACCESS_TOKEN = result['access_token']
        BAIDU_TOKEN_EXPIRE_TIME = time.time() + result.get('expires_in', 2592000) - 300
        return BAIDU_ACCESS_TOKEN
    else:
        raise Exception("获取百度访问令牌失败：" + str(result))

def delete_conversation(conversation_id: str) -> bool:
    """删除对话记录"""
    file_path = DATA_DIR / f"{conversation_id}.json"
    if file_path.exists():
        file_path.unlink()
        return True
    return False

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

@app.route('/conversations', methods=['GET'])
def get_conversations():
    try:
        conversations = load_all_conversations()
        return jsonify(conversations)
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        conversation = load_conversation(conversation_id)
        if conversation:
            return jsonify(conversation)
        return jsonify({'error': '对话不存在'}), 404
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation_route(conversation_id):
    try:
        if delete_conversation(conversation_id):
            return jsonify({'success': True})
        return jsonify({'error': '对话不存在'}), 404
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/knowledge/upload', methods=['POST'])
def upload_knowledge():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        filename = secure_filename(file.filename)
        file_path = Path('temp') / filename
        file_path.parent.mkdir(exist_ok=True)
        file.save(str(file_path))
        
        try:
            document = know.process_document(
                file_path, 
                file_path.suffix[1:].lower()
            )
            return jsonify(document)
        finally:
            file_path.unlink()  # 删除临时文件
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/knowledge', methods=['GET'])
def get_knowledge():
    try:
        documents = know.get_all_documents()
        return jsonify(documents)
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """获取所有可用的模型"""
    try:
        # 获取 Ollama 模型
        response = requests.get("http://localhost:11434/api/tags")
        ollama_models = response.json().get("models", [])
        
        # 添加百度模型
        all_models = [
            *[{"name": m["name"], "type": "ollama"} for m in ollama_models],
            {"name": "ernie-3.5-128k", "type": "baidu"}
        ]
        
        return jsonify({
            "models": all_models,
            "current": CURRENT_MODEL
        })
    except Exception as e:
        print(f"获取模型列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models/current', methods=['PUT'])
def set_current_model():
    """设置当前使用的模型"""
    try:
        global CURRENT_MODEL
        data = request.get_json()
        model = data.get('model')
        
        if not model:
            return jsonify({'error': '请提供模型名称'}), 400
            
        # 验证模型是否可用
        response = requests.get("http://localhost:11434/api/tags")
        available_models = [m['name'] for m in response.json().get("models", [])]
        
        if model not in available_models:
            return jsonify({'error': '模型不可用'}), 400
            
        CURRENT_MODEL = model
        return jsonify({
            "current": CURRENT_MODEL
        })
        
    except Exception as e:
        print(f"设置模型失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversationId')
        use_knowledge = data.get('useKnowledge', False)
        
        if not message:
            return jsonify({'error': '请提供聊天消息'}), 400
            
        # 获取或创建对话
        if not conversation_id:
            # 只在没有 conversation_id 时创建新对话
            conversation_id = datetime.now().strftime('%Y%m%d%H%M%S')
            conversation = {
                'id': conversation_id,
                'title': message[:20] + '...' if len(message) > 20 else message,
                'messages': [],
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
        else:
            # 如果有 conversation_id，加载现有对话
            conversation = load_conversation(conversation_id)
            if not conversation:
                # 如果找不到对话，创建新对话
                conversation = {
                    'id': conversation_id,
                    'title': message[:20] + '...' if len(message) > 20 else message,
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
                'model': CURRENT_MODEL,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }

            # 添加消息到对话
            conversation['messages'].append(user_message)
            conversation['messages'].append(bot_message)
            
            # 保存对话（确保消息被记录）
            save_conversation(conversation_id, conversation)
            
            # 如果启用知识库，先搜索相关内容
            context = ""
            if use_knowledge:
                # 发送正在查询的消息
                yield f"data: {json.dumps({'chunk': '正在查询知识库...\n\n', 'conversationId': conversation_id})}\n\n"
                
                results = know.search_knowledge(message)
                if not results:
                    yield f"data: {json.dumps({'chunk': '未找到相关知识，将使用通用回答。\n\n', 'conversationId': conversation_id})}\n\n"
                else:
                    yield f"data: {json.dumps({'chunk': '已找到相关知识：\n\n', 'conversationId': conversation_id})}\n\n"
                    context = "根据以下信息回答：\n" + "\n".join(
                        [r['content'] for r in results]
                    ) + "\n问题：" + message
            
            # 根据模型类型选择不同的 API
            if MODEL_TYPES.get(CURRENT_MODEL) == "baidu":
                # 使用百度 API
                access_token = get_baidu_access_token()
                baidu_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
                
                response = requests.post(
                    baidu_url,
                    json={
                        "messages": [
                            {
                                "role": "user",
                                "content": context or f"请用中文回答：{message}"
                            }
                        ],
                        "stream": True
                    },
                    stream=True
                )
                
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'result' in data:
                                chunk = data['result']
                                bot_message['content'] += chunk
                                yield f"data: {json.dumps({'chunk': chunk, 'conversationId': conversation_id})}\n\n"
                        except json.JSONDecodeError:
                            continue
                
            else:
                # 使用 Ollama API
                response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": CURRENT_MODEL,
                        "prompt": context or f"请用中文回答：{message}",
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
                                save_conversation(conversation_id, conversation)
                                yield f"data: {json.dumps({'chunk': chunk, 'conversationId': conversation_id})}\n\n"
                        except json.JSONDecodeError:
                            continue
            
            # 更新对话时间戳
            conversation['updatedAt'] = datetime.now().isoformat()
            save_conversation(conversation_id, conversation)
            yield f"data: {json.dumps({'done': True, 'conversationId': conversation_id})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    try:
        # 检查 Ollama 服务是否运行
        response = requests.get("http://localhost:11434/api/tags")
        models = [model.get('name') for model in response.json().get("models", [])]
        return jsonify({
            "status": "running",
            "ollama_status": "connected",
            "available_models": models,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            "status": "running",
            "ollama_status": "disconnected",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route('/sdk/config', methods=['GET'])
def get_sdk_config():
    """获取 SDK 配置"""
    host = request.headers.get('Host', 'localhost:3000')
    scheme = request.scheme
    base_url = f"{scheme}://{host}"
    
    config = {
        'apiUrl': base_url,
        'sdkVersion': '1.0.0',
        'defaultModel': CURRENT_MODEL,
    }
    
    return jsonify(config)

@app.route('/sdk/script', methods=['GET'])
def get_sdk_script():
    """获取 SDK 脚本"""
    host = request.headers.get('Host', 'localhost:3000')
    scheme = request.scheme
    base_url = f"{scheme}://{host}"
    
    script = f"""
// AI Chat SDK v1.0.0
(function() {{
    const API_URL = '{base_url}';
    const CHAT_STYLES = `
        .ai-chat-widget {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: #343541;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            font-family: system-ui, -apple-system, sans-serif;
            z-index: 9999;
        }}
        .ai-chat-header {{
            padding: 10px 15px;
            background: #202123;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .ai-chat-header-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }}
        .ai-chat-header-model {{
            font-size: 12px;
            padding: 2px 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            color: #9ca3af;
        }}
        .ai-chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }}
        .ai-chat-message {{
            margin-bottom: 12px;
            display: flex;
            flex-direction: column;
            max-width: 80%;
            clear: both;
        }}
        .ai-chat-message.user {{
            float: right;
            align-items: flex-end;
            margin-left: auto;
        }}
        .ai-chat-message.bot {{
            float: left;
            align-items: flex-start;
        }}
        .ai-chat-message-bubble {{
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }}
        .ai-chat-message.user .ai-chat-message-bubble {{
            background: #2563eb;
            color: white;
        }}
        .ai-chat-message.bot .ai-chat-message-bubble {{
            background: #444654;
            color: white;
        }}
        .ai-chat-message-model {{
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 4px;
        }}
        .ai-chat-message-time {{
            font-size: 11px;
            color: #9ca3af;
            margin-top: 4px;
        }}
        .ai-chat-divider {{
            text-align: center;
            margin: 12px 0;
            color: #9ca3af;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            clear: both;
        }}
        .ai-chat-divider::before,
        .ai-chat-divider::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(156,163,175,0.2);
        }}
        .ai-chat-input {{
            padding: 10px;
            background: #40414f;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .ai-chat-input form {{
            position: relative;
        }}
        .ai-chat-input input {{
            width: 100%;
            padding: 8px 40px 8px 12px;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            background: transparent;
            color: white;
            font-size: 14px;
        }}
        .ai-chat-input input:focus {{
            outline: none;
            border-color: rgba(255,255,255,0.2);
        }}
        .ai-chat-input button {{
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: #9ca3af;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
        }}
        .ai-chat-input button:hover {{
            color: white;
            background: rgba(255,255,255,0.1);
        }}
        .ai-chat-input button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
    `;

    class AIChatWidget {{
        constructor() {{
            this.createWidget();
            this.isLoading = false;
            this.currentModel = null;
            this.conversationId = null;
            this.lastManualReplyId = null;
            this.startManualReplyCheck();
            this.initModel();
        }}

        async initModel() {{
            try {{
                const response = await fetch(`${{API_URL}}/models`);
                const data = await response.json();
                this.currentModel = data.current;
                const modelSpan = document.querySelector('.ai-chat-header-model');
                if (modelSpan) {{
                    modelSpan.textContent = this.currentModel;
                }}
            }} catch (error) {{
                console.error('Failed to fetch model:', error);
                this.currentModel = 'mistral';
            }}
        }}

        startManualReplyCheck() {{
            setInterval(async () => {{
                if (this.conversationId) {{
                    try {{
                        const response = await fetch(`${{API_URL}}/sdk/conversations/${{this.conversationId}}`);
                        const data = await response.json();
                        
                        const lastMessage = data.messages[data.messages.length - 1];
                        if (lastMessage && lastMessage.isManual && 
                            (!this.lastManualReplyId || this.lastManualReplyId !== lastMessage.id)) {{
                            this.lastManualReplyId = lastMessage.id;
                            this.addDivider();
                            this.addMessage(lastMessage.content, 'bot', true);
                        }}
                    }} catch (error) {{
                        console.error('Failed to check manual replies:', error);
                    }}
                }}
            }}, 5000);
        }}

        createWidget() {{
            const style = document.createElement('style');
            style.textContent = CHAT_STYLES;
            document.head.appendChild(style);

            const widget = document.createElement('div');
            widget.className = 'ai-chat-widget';
            widget.innerHTML = `
                <div class="ai-chat-header">
                    <div class="ai-chat-header-title">
                        <span>AI 助手</span>
                        <span class="ai-chat-header-model">加载中...</span>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
                <div class="ai-chat-messages"></div>
                <div class="ai-chat-input">
                    <form>
                        <input type="text" placeholder="输入消息...">
                        <button type="submit">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M22 2L11 13" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </form>
                </div>
            `;

            document.body.appendChild(widget);

            const form = widget.querySelector('form');
            const input = widget.querySelector('input');
            const button = widget.querySelector('button');
            const messages = widget.querySelector('.ai-chat-messages');

            const sendMessage = async () => {{
                if (this.isLoading || !input.value.trim()) return;

                const message = input.value;
                input.value = '';
                
                this.addMessage(message, 'user');
                
                this.isLoading = true;
                button.disabled = true;

                try {{
                    const response = await fetch(`${{API_URL}}/sdk/chat`, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ 
                            message,
                            conversationId: this.conversationId
                        }})
                    }});

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let botMessage = '';

                    while (true) {{
                        const {{done, value}} = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {{
                            if (line.startsWith('data: ')) {{
                                try {{
                                    const data = JSON.parse(line.slice(5));
                                    if (data.conversationId) {{
                                        this.conversationId = data.conversationId;
                                    }}
                                    if (data.divider) {{
                                        this.addDivider();
                                    }}
                                    if (data.chunk) {{
                                        botMessage += data.chunk;
                                        this.updateBotMessage(botMessage, data.model);
                                    }}
                                }} catch (e) {{}}
                            }}
                        }}
                    }}
                }} catch (error) {{
                    this.addMessage('抱歉，出现了一些错误。', 'bot');
                }} finally {{
                    this.isLoading = false;
                    button.disabled = false;
                }}
            }};

            form.onsubmit = (e) => {{
                e.preventDefault();
                sendMessage();
            }};
        }}

        addMessage(content, type) {{
            const messages = document.querySelector('.ai-chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `ai-chat-message ${{type}}`;
            
            let html = '';
            if (type === 'bot') {{
                html += `<div class="ai-chat-message-model">${{this.currentModel}}</div>`;
            }}
            
            html += `
                <div class="ai-chat-message-bubble">${{content}}</div>
                <div class="ai-chat-message-time">${{new Date().toLocaleTimeString()}}</div>
            `;
            
            messageDiv.innerHTML = html;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }}

        addDivider() {{
            const messages = document.querySelector('.ai-chat-messages');
            const divider = document.createElement('div');
            divider.className = 'ai-chat-divider';
            divider.textContent = '当前为人工介入';
            messages.appendChild(divider);
            messages.scrollTop = messages.scrollHeight;
        }}

        updateBotMessage(content, model) {{
            const messages = document.querySelector('.ai-chat-messages');
            let lastMessage = messages.querySelector('.ai-chat-message.bot:last-child');
            
            if (!lastMessage) {{
                lastMessage = document.createElement('div');
                lastMessage.className = 'ai-chat-message bot';
                lastMessage.innerHTML = `
                    <div class="ai-chat-message-model">${{model || this.currentModel}}</div>
                    <div class="ai-chat-message-bubble"></div>
                    <div class="ai-chat-message-time">${{new Date().toLocaleTimeString()}}</div>
                `;
                messages.appendChild(lastMessage);
            }}
            
            const bubble = lastMessage.querySelector('.ai-chat-message-bubble');
            if (bubble) {{
                bubble.textContent = content;
                messages.scrollTop = messages.scrollHeight;
            }}
        }}
    }}

    window.initAIChat = function() {{
        new AIChatWidget();
    }};
}})();
    """
    
    return Response(script, mimetype='application/javascript')

@app.route('/sdk/chat', methods=['POST'])
def sdk_chat():
    """SDK 专用的聊天接口"""
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversationId')
        
        if not message:
            return jsonify({'error': '请提供聊天消息'}), 400
            
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
                'model': CURRENT_MODEL,
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
                    "model": CURRENT_MODEL,
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
                            yield f"data: {json.dumps({'chunk': chunk, 'model': CURRENT_MODEL})}\n\n"
                    except json.JSONDecodeError:
                        continue
            
            # 更新对话时间戳
            conversation['updatedAt'] = datetime.now().isoformat()
            save_sdk_conversation(conversation_id, conversation)
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 添加人工回复接口
@app.route('/sdk/manual-reply', methods=['POST'])
def sdk_manual_reply():
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversationId')
        
        if not message or not conversation_id:
            return jsonify({'error': '缺少必要参数'}), 400
            
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
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取 SDK 对话列表
@app.route('/sdk/conversations', methods=['GET'])
def get_sdk_conversations():
    try:
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
        return jsonify(sorted(conversations, key=lambda x: x['updatedAt'], reverse=True))
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取特定 SDK 对话
@app.route('/sdk/conversations/<conversation_id>', methods=['GET'])
def get_sdk_conversation(conversation_id):
    try:
        conversation = load_sdk_conversation(conversation_id)
        if conversation:
            return jsonify(conversation)
        return jsonify({'error': '对话不存在'}), 404
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 在现有代码中添加新的路由

@app.route('/sdk/conversations/<conversation_id>/mode', methods=['PUT'])
def set_conversation_mode(conversation_id):
    try:
        data = request.get_json()
        is_manual = data.get('isManual', False)
        
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
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True) 