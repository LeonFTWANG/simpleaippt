## 📖 使用教程
本项目开箱即用，ppt模板请参考内置的ppt模板（\uploads\custom_templates），建议使用大纲做为ppt的内容，内容太多会造成ppt内容拥挤，也违背ppt的初衷了

### 1. 配置环境

**方法一：一键脚本⭐**

双击 `启动.bat` 文件，程序会自动：
- 检查 Python 是否安装
- 自动安装所需依赖包
- 创建配置文件
- 启动 Web 服务

**方法二：手动启动**

```bash
# 1. 进入项目目录
cd x:\paippt

# 2. 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 启动服务
python app.py
```

### 2. 访问应用

打开浏览器访问：**http://127.0.0.1:5000**

### 3. 配置 API 密钥

**网页配置（推荐）：**
1. 点击页面右上角 **"配置API"** 按钮
2. 填写 API Key、Base URL（可选）、模型（可选）
3. 点击保存并刷新页面
#### 状态指示

- ✅ **绿色** - API 已配置且连接正常
- ⚠️ **黄色** - API 未配置
- ❌ **红色** - API 配置错误或连接失败

**手动配置：**

编辑 `.env` 文件：
```env
API_KEY=sk-your-api-key-here
API_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat
```

**API Key 获取：**
- DeepSeek：https://platform.deepseek.com/api_keys
- 目前只测试了deepsek的apikey，需要使用其他的请看相关的官方文档

#### 4. 模板设置

**选项 A：使用默认模板**
- 不勾选"使用自定义模板"
- 系统使用内置简洁模板

**选项 B：使用自定义模板**
1. 勾选"使用自定义模板"
2. 选择已上传的模板，或点击"上传模板"
3. 选择你的 .pptx 文件
4. 等待上传完成
注意！！！---ppt不能使用动画，否则可能生成的ppt会提示损坏，使用ppt模板请提前设置好ppt的母版，详情请参考文件内置的ppt模板（\uploads\custom_templates）