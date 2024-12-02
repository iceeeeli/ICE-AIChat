from pathlib import Path

# 基础路径配置
ROOT_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = ROOT_DIR / 'data'
SDK_DATA_DIR = DATA_DIR / 'sdk'
KNOWLEDGE_DIR = DATA_DIR / 'knowledge'

# API 配置
OLLAMA_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_URL}/api/generate"
OLLAMA_EMBEDDINGS_URL = f"{OLLAMA_URL}/api/embeddings"

# 百度 API 配置
BAIDU_API_KEY = "130ICAKPnBy3RH45Xuz0a0e8"
BAIDU_SECRET_KEY = "L2aNUJKhOOA6K8aP12bW4PBeksvhQYge"
BAIDU_API_URL = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"

# 模型配置
DEFAULT_MODEL = "mistral"
MODEL_TYPES = {
    "mistral": "ollama",
    "qwen2-7b": "ollama",
    "ernie-3.5-128k": "baidu"
}

# 文件配置
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx'}

# 向量搜索配置
VECTOR_SIMILARITY_THRESHOLD = 0.3
TOP_K_RESULTS = 3
CHUNK_SIZE = 500

# AI 参数配置
AI_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "num_ctx": 2048,
    "stop": ["Human:", "Assistant:"]
} 