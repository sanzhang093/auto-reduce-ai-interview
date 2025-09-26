@echo off
chcp 65001 >nul

echo 🚀 自动减负AI应用架构 - 部署脚本
echo ==================================

REM 检查Python环境
echo 📋 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python 已安装
python --version

REM 检查依赖文件
echo 📋 检查依赖文件...
if not exist "requirements_deploy.txt" (
    echo ❌ requirements_deploy.txt 文件不存在
    pause
    exit /b 1
)

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements_deploy.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装成功

REM 检查必要文件
echo 📋 检查必要文件...
set required_files=deploy_simple.py ai_chat_interface.html web_interface_fixed.html industry_standard_database_extended.json

for %%f in (%required_files%) do (
    if not exist "%%f" (
        echo ❌ 必要文件 %%f 不存在
        pause
        exit /b 1
    )
)

echo ✅ 所有必要文件存在

REM 启动服务
echo 🚀 启动服务...
echo 📍 服务地址: http://localhost:8000
echo 📍 健康检查: http://localhost:8000/health
echo 📍 API文档: http://localhost:8000/docs
echo ==================================

python deploy_simple.py

pause
