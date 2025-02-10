@echo off
chcp 65001
echo 正在更新Hakubooru项目...
git pull
REM ------------------------------------------------------------------
REM 批处理脚本：更新项目
REM ------------------------------------------------------------------

set EMBEDDED_PYTHON_PATH=.\python-3.10.6-embed-amd64
set GUI_SCRIPT_PATH=update.py
set HF_ENDPOINT=https://hf-mirror.com

REM 检查嵌入式 Python 是否存在
if not exist "%EMBEDDED_PYTHON_PATH%\python.exe" (
    echo 错误：找不到嵌入式 Python 路径 "%EMBEDDED_PYTHON_PATH%"
    pause
    exit /b 1
)

REM 检查更新脚本是否存在
if not exist "%GUI_SCRIPT_PATH%" (
    echo 错误：找不到更新脚本 "%GUI_SCRIPT_PATH%"
    pause
    exit /b 1
)

REM 临时添加 Python 环境到 PATH
set PATH=%EMBEDDED_PYTHON_PATH%;%EMBEDDED_PYTHON_PATH%\Scripts;%PATH%

REM 获取用户输入的 HuggingFace Token
set /p HUGGINGFACE_TOKEN=请输入 Hugging Face Token: 

REM 登录 Hugging Face
huggingface-cli login --token %HUGGINGFACE_TOKEN%

REM 启动更新脚本
echo 正在尝试更新数据库及数据集...
"%EMBEDDED_PYTHON_PATH%\python.exe" "%GUI_SCRIPT_PATH%"

REM 保持窗口打开
pause