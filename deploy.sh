#!/bin/bash

# 自动减负AI应用架构 - 一键部署脚本

echo "🚀 自动减负AI应用架构 - 部署脚本"
echo "=================================="

# 检查Python环境
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查依赖
echo "📋 检查依赖..."
if [ ! -f "requirements_deploy.txt" ]; then
    echo "❌ requirements_deploy.txt 文件不存在"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements_deploy.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装成功"

# 检查必要文件
echo "📋 检查必要文件..."
required_files=("deploy_simple.py" "ai_chat_interface.html" "web_interface_fixed.html" "industry_standard_database_extended.json")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 必要文件 $file 不存在"
        exit 1
    fi
done

echo "✅ 所有必要文件存在"

# 启动服务
echo "🚀 启动服务..."
echo "📍 服务地址: http://localhost:8000"
echo "📍 健康检查: http://localhost:8000/health"
echo "📍 API文档: http://localhost:8000/docs"
echo "=================================="

python3 deploy_simple.py
