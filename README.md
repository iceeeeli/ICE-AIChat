# ICE AI Chat - 智能对话系统
## 本项目仅作为学习交流使用，请勿用于商业用途

一个基于大语言模型的智能对话系统，支持多模型切换、知识库管理、SDK 集成等功能。


## 功能特点

### 1. 多模型支持
- 支持 Ollama 本地模型 (mistral, qwen2-7b)
- 支持百度文心一言模型 (ERNIE-3.5-128K)
- 实时切换不同模型

### 2. 知识库管理
- 支持上传 TXT、DOC、DOCX 文档
- 自动文档向量化
- 智能相似度搜索
- 基于知识库的问答

### 3. SDK 集成
- 一键获取集成代码
- 支持网页嵌入聊天窗口
- 实时对话流式响应
- 支持人工客服介入

### 4. 对话管理
- 多会话管理
- 实时保存对话记录
- 支持删除对话
- 流式打字机效果

## 技术栈

### 后端 (Server)
- Python 3.11+
- Flask
- Flask-CORS
- NumPy
- scikit-learn
- python-docx
- tiktoken

### 前端 (Web)
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Heroicons
- React Markdown

## 项目结构
```bash
ai-chat/
├── apps/
│ ├── server/ # 后端服务
│ │ ├── src/
│ │ │ ├── app.py # 主应用
│ │ │ ├── know.py # 知识库管理
│ │ │ └── sdk_chat.py # SDK 相关
│ │ └── requirements.txt
│ └── web/ # 前端应用
│ ├── app/ # 页面
│ ├── components/ # 组件
│ ├── lib/ # 工具函数
│ └── types/ # 类型定义
├── packages/
│ └── shared/ # 共享类型和工具
└── scripts/ # 脚本
```

## 安装部署

### 环境要求
- Node.js 18+
- Python 3.11+
- pnpm 8+
- Ollama

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/yourusername/ai-chat.git
cd ai-chat
```

2. 安装依赖
```bash
#安装前端依赖
pnpm install
#安装后端依赖
cd apps/server
python -m venv venv
source venv/bin/activate # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
```bash
#在 apps/server/.env 中配置
PORT=3000
#在 apps/web/.env.local 中配置
NEXT_PUBLIC_API_URL=http://localhost:3000


4. 启动服务
```bash
#开发模式
pnpm dev

#生产模式
pnpm build
pnpm start
```

## API 文档

### 对话接口
- `POST /chat` - 发送对话消息
- `GET /conversations` - 获取对话列表
- `GET /conversations/:id` - 获取特定对话
- `DELETE /conversations/:id` - 删除对话

### 知识库接口
- `POST /knowledge/upload` - 上传文档
- `GET /knowledge` - 获取知识库列表

### SDK 接口
- `GET /sdk/script` - 获取 SDK 代码
- `POST /sdk/chat` - SDK 对话接口
- `POST /sdk/manual-reply` - 人工回复接口

### 模型接口
- `GET /models` - 获取可用模型列表
- `PUT /models/current` - 设置当前模型

## SDK 使用

1. 获取集成代码
```js
// 在你的网页中添加以下代码
<script src="http://localhost:3000/sdk/script"></script>
// 初始化聊天窗口
<script>
initAIChat();
</script>
```

2. 自定义样式
```css
.ai-chat-widget {
/ 你的样式 /
}
```

## 开发指南

### 添加新模型
1. 在 `MODEL_TYPES` 中添加模型定义
2. 实现模型的 API 调用逻辑
3. 更新前端模型选择器

### 添加新功能
1. 在后端添加新的路由和处理逻辑
2. 在前端添加对应的 API 调用
3. 创建新的组件和页面
4. 更新类型定义

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 联系方式

- 项目维护者：[iceeeeli]
- Email：[iceeee.work@gmail.com]
- GitHub：[[iceeeeli](https://github.com/iceeeeli)]

## 许可证

MIT License

Copyright (c) 2024 iceeeeli