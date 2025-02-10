@echo off
chcp 65001
REM ------------------------------------------------------------------
REM 批处理脚本：使用嵌入式 Python 启动 HakuBooru-GUI
REM ------------------------------------------------------------------

set EMBEDDED_PYTHON_PATH=.\python-3.10.6-embed-amd64
set GUI_SCRIPT_PATH=.\gui\gui.py

REM 检查嵌入式 Python 是否存在
if not exist "%EMBEDDED_PYTHON_PATH%\python.exe" (
    echo 错误：找不到嵌入式 Python 路径 "%EMBEDDED_PYTHON_PATH%"
    pause
    exit /b 1
)

REM 检查 GUI 脚本是否存在
if not exist "%GUI_SCRIPT_PATH%" (
    echo 错误：找不到 GUI 脚本 "%GUI_SCRIPT_PATH%"
    pause
    exit /b 1
)

REM 临时添加 Python 环境到 PATH
set PATH=%EMBEDDED_PYTHON_PATH%;%EMBEDDED_PYTHON_PATH%\Scripts;%PATH%

REM 启动 GUI 脚本
echo 正在启动 GUI...
"%EMBEDDED_PYTHON_PATH%\python.exe" "%GUI_SCRIPT_PATH%"

REM 保持窗口打开
pause