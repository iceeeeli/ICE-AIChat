#!/bin/bash

# 获取项目根目录的绝对路径
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# 启动后端服务
cd "$ROOT_DIR/apps/server" || exit

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 先安装基础包
python3 -m pip install --upgrade pip setuptools wheel

# 安装其他依赖（添加额外的 pip 参数）
python3 -m pip install --no-cache-dir -r requirements.txt

# 运行后端服务
python3 src/app.py &

# 启动前端服务
cd "$ROOT_DIR/apps/web" || exit
pnpm dev &

# 等待所有后台进程
wait