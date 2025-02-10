@REM @echo off
@REM chcp 65001
@REM echo 正在更新Hakubooru项目...
@REM git pull
@REM REM ------------------------------------------------------------------
@REM REM 批处理脚本：更新项目
@REM REM ------------------------------------------------------------------

@REM set EMBEDDED_PYTHON_PATH=.\python-3.10.6-embed-amd64
@REM set GUI_SCRIPT_PATH=update.py
@REM set HF_ENDPOINT=https://hf-mirror.com

@REM REM 检查嵌入式 Python 是否存在
@REM if not exist "%EMBEDDED_PYTHON_PATH%\python.exe" (
@REM     echo 错误：找不到嵌入式 Python 路径 "%EMBEDDED_PYTHON_PATH%"
@REM     pause
@REM     exit /b 1
@REM )

@REM REM 检查更新脚本是否存在
@REM if not exist "%GUI_SCRIPT_PATH%" (
@REM     echo 错误：找不到更新脚本 "%GUI_SCRIPT_PATH%"
@REM     pause
@REM     exit /b 1
@REM )

@REM REM 临时添加 Python 环境到 PATH
@REM set PATH=%EMBEDDED_PYTHON_PATH%;%EMBEDDED_PYTHON_PATH%\Scripts;%PATH%

@REM REM 获取用户输入的 HuggingFace Token
@REM set /p HUGGINGFACE_TOKEN=请输入 Hugging Face Token: 

@REM REM 登录 Hugging Face
@REM huggingface-cli login --token %HUGGINGFACE_TOKEN%

@REM REM 启动更新脚本
@REM echo 正在尝试更新数据库及数据集...
@REM "%EMBEDDED_PYTHON_PATH%\python.exe" "%GUI_SCRIPT_PATH%"

@REM REM 保持窗口打开
@REM pause