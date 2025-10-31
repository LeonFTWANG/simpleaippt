@echo off
chcp 65001 >nul
echo ========================================
echo    AI PPT 生成器 - 启动程序
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Python！
    echo.
    echo 请先安装 Python 3.8 或更高版本：
    echo.
    echo 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python 已安装
python --version
echo.

REM 更新 pip
echo 更新 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
echo.

REM 检查是否已安装依赖
echo 检查依赖包...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo.
    echo 检测到依赖未安装，正在安装...
    echo.
    echo 使用国内镜像加速安装（清华源）...
    echo 这可能需要几分钟时间，请耐心等待...
    echo.
    
    REM 分步安装，避免编译问题
    echo [1/6] 安装 Flask...
    pip install Flask==3.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo [2/6] 安装 Flask-CORS...
    pip install Flask-CORS==4.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo [3/6] 安装 requests...
    pip install requests==2.31.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo [4/6] 安装 python-dotenv...
    pip install python-dotenv==1.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo [5/6] 安装 Pillow...
    pip install Pillow==10.1.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo [6/6] 安装 python-pptx...
    pip install python-pptx==0.6.23 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if errorlevel 1 (
        echo.
        echo 依赖安装失败！
        echo.
        echo 可能的解决方案：
        echo 1. 检查网络连接
        echo 2. 尝试使用官方源：pip install -r requirements.txt
        echo 3. 使用虚拟环境安装（详见使用说明.md）
        echo.
        pause
        exit /b 1
    )
    echo.
    echo 依赖安装完成
) else (
    echo 依赖已安装
)

echo.
echo ========================================
echo    检查配置文件
echo ========================================

REM 检查 .env 文件
if not exist .env (
    echo.
    echo 未找到 .env 配置文件，正在创建...
    echo # AI API 配置>>.env
    echo API_KEY=请在这里填写你的API密钥>>.env
    echo API_BASE_URL=https://api.deepseek.com>>.env
    echo AI_MODEL=deepseek-chat>>.env
    echo.>>.env
    echo # Flask 配置>>.env
    echo FLASK_SECRET_KEY=your-secret-key-change-this>>.env
    echo FLASK_DEBUG=True>>.env
    echo.>>.env
    echo # 上传配置>>.env
    echo MAX_TEMPLATE_SIZE=50>>.env
    echo.
    echo .env 文件已创建
    echo.
    echo ========================================
    echo    重要提示：配置 API 密钥
    echo ========================================
    echo.
    echo 1. 请在弹出的记事本中填写你的 API_KEY
    echo 2. 获取 API Key 的方式：
    echo    - DeepSeek: https://platform.deepseek.com/api_keys
    echo    - OpenAI: https://platform.openai.com/api-keys
    echo 3. 保存并关闭记事本
    echo 4. 重新运行本程序启动服务
    echo.
    echo 按任意键打开配置文件...
    pause >nul
    notepad .env
    echo.
    echo 配置完成后，请重新运行本程序！
    echo.
    pause
    exit /b 0
)

echo 配置文件已存在
echo.

REM 检查是否已配置API密钥
findstr /C:"请在这里填写你的API密钥" .env >nul
if not errorlevel 1 (
    echo.
    echo ========================================
    echo    警告：API 密钥未配置
    echo ========================================
    echo.
    echo 检测到 .env 文件中的 API_KEY 尚未配置！
    echo.
    echo 您可以：
    echo 1. 现在配置（按 Y 键打开配置文件）
    echo 2. 稍后在网页界面配置（按 N 键继续启动）
    echo.
    choice /C YN /M "是否现在配置 API 密钥？"
    if errorlevel 2 (
        echo.
        echo 提示：启动后可以在网页右上角点击"配置API"按钮进行配置
        echo.
    ) else (
        notepad .env
        echo.
        echo 配置完成后，请重新运行本程序！
        echo.
        pause
        exit /b 0
    )
)

echo.
echo ========================================
echo    启动服务
echo ========================================
echo.
echo 正在启动 Flask 服务...
echo.
echo 访问地址: http://127.0.0.1:5000
echo.
echo ========================================
echo.

python app.py

echo.
echo 服务已停止
echo.
pause

