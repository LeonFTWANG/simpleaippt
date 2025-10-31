import requests
import json
from config import Config


class AIService:
    
    def __init__(self):
        self.api_url = Config.API_URL
        self.api_key = Config.API_KEY
        self.model = Config.AI_MODEL
    
    def _call_api(self, messages, max_tokens, temperature=None, stream=False):
        """
        调用 AI API
        
        Args:
            messages: 消息列表
            max_tokens: 最大 token 数
            temperature: 温度参数
            stream: 是否使用流式输出
            
        Returns:
            dict 或 generator: API 响应
        """
        if not self.api_key:
            raise ValueError("API_KEY 未配置，请在 .env 文件中设置")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature or Config.AI_TEMPERATURE,
            'stream': stream
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return response
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"AI API 调用失败: {str(e)}")
    
    def generate_outline(self, topic, chapters=5):
        """
        生成 PPT 大纲
        
        Args:
            topic: 主题
            chapters: 章节数量
            
        Returns:
            str: Markdown 格式的大纲
        """
        system_prompt = """你是一个专业的PPT大纲设计师。请根据用户提供的主题生成结构清晰的PPT大纲。

要求：
1. 使用 Markdown 格式
2. 第一级标题 (##) 代表主要章节
3. 第二级标题 (###) 代表小标题
4. 使用列表 (-) 列出要点
5. **每个章节（##）最多只能有3个小标题（###）**
6. 每个小标题（###）的字数不超过50个字
7. 必须生成完整的大纲，不能中途停止
8. 结构要清晰，逻辑要严密

示例格式：
## 第一章 引言
### 背景介绍
- 要点1
- 要点2

### 核心概念
- 要点1
- 要点2

### 发展趋势
- 要点1
- 要点2
"""
        
        user_prompt = f"""请为以下主题生成一个包含{chapters}个章节的PPT大纲：

主题：{topic}

请严格遵守：
1. 每个章节都有明确的主题
2. **每个章节最多只能有3个小标题（不能超过3个）**
3. 每个小标题下有2-4个要点
4. 小标题字数不超过50个字
5. 必须完整生成所有{chapters}个章节"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        result = self._call_api(messages, Config.AI_MAX_TOKENS_OUTLINE)
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content.strip()
        else:
            raise Exception("AI 返回的数据格式不正确")
    
    def generate_content(self, outline):
        """
        根据大纲生成详细内容
        
        Args:
            outline: Markdown 格式的大纲
            
        Returns:
            str: Markdown 格式的详细内容
        """
        system_prompt = """你是一个专业的PPT内容撰写师。请根据提供的大纲，为每个要点生成详细的说明内容。

要求：
1. 保持原有的完整章节结构（##, ###, -）
2. 在每个要点（-）后面添加详细、充分的说明内容
3. 每个小标题（###）的字数不超过50个字
4. 每个要点的详细说明要充分展开，清晰表达核心内容
5. 必须完整生成所有章节的内容，不能中途停止
6. 内容要专业、准确、有深度

示例格式：
## 第一章 引言
### 背景介绍
- 要点1：详细说明内容，可以充分展开描述，确保信息完整、清晰
- 要点2：详细说明内容，不限制字数，重点是表达清楚核心观点和关键信息
"""
        
        user_prompt = f"""请根据以下大纲生成详细内容：

{outline}

请确保：
1. 保持所有章节和小标题不变
2. 为每个要点添加充分、详细的说明内容，充分展开描述
3. 小标题字数不超过50个字
4. 必须完整生成所有内容，不能遗漏任何章节"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        result = self._call_api(messages, Config.AI_MAX_TOKENS_CONTENT)
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content.strip()
        else:
            raise Exception("AI 返回的数据格式不正确")
    
    def generate_outline_stream(self, topic, chapters=5):
        """
        生成 PPT 大纲 - 流式输出
        
        Args:
            topic: 主题
            chapters: 章节数量
            
        Yields:
            str: 内容片段
        """
        system_prompt = """你是一个专业的PPT大纲设计师。请根据用户提供的主题生成结构清晰的PPT大纲。

要求：
1. 使用 Markdown 格式
2. 第一级标题 (##) 代表主要章节
3. 第二级标题 (###) 代表小标题
4. 使用列表 (-) 列出要点
5. **每个章节（##）最多只能有3个小标题（###）**
6. 每个小标题（###）的字数不超过50个字
7. 必须生成完整的大纲，不能中途停止
8. 结构要清晰，逻辑要严密

示例格式：
## 第一章 引言
### 背景介绍
- 要点1
- 要点2

### 核心概念
- 要点1
- 要点2

### 发展趋势
- 要点1
- 要点2
"""
        
        user_prompt = f"""请为以下主题生成一个包含{chapters}个章节的PPT大纲：

主题：{topic}

请严格遵守：
1. 每个章节都有明确的主题
2. **每个章节最多只能有3个小标题（不能超过3个）**
3. 每个小标题下有2-4个要点
4. 小标题字数不超过50个字
5. 必须完整生成所有{chapters}个章节"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        response = self._call_api(messages, Config.AI_MAX_TOKENS_OUTLINE, stream=True)
        
        # 处理 SSE 流
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                
                if data_str == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
    
    def generate_content_stream(self, outline):
        """
        根据大纲生成详细内容 - 流式输出
        
        Args:
            outline: Markdown 格式的大纲
            
        Yields:
            str: 内容片段
        """
        system_prompt = """你是一个专业的PPT内容撰写师。请根据提供的大纲，为每个要点生成详细的说明内容。

要求：
1. 保持原有的完整章节结构（##, ###, -）
2. 在每个要点（-）后面添加详细、充分的说明内容
3. 每个小标题（###）的字数不超过50个字
4. 每个要点的详细说明要充分展开，清晰表达核心内容
5. 必须完整生成所有章节的内容，不能中途停止
6. 内容要专业、准确、有深度

示例格式：
## 第一章 引言
### 背景介绍
- 要点1：详细说明内容，可以充分展开描述，确保信息完整、清晰
- 要点2：详细说明内容，不限制字数，重点是表达清楚核心观点和关键信息
"""
        
        user_prompt = f"""请根据以下大纲生成详细内容：

{outline}

请确保：
1. 保持所有章节和小标题不变
2. 为每个要点添加充分、详细的说明内容，充分展开描述
3. 小标题字数不超过50个字
4. 必须完整生成所有内容，不能遗漏任何章节"""
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        response = self._call_api(messages, Config.AI_MAX_TOKENS_CONTENT, stream=True)
        
        # 处理 SSE 流
        for line in response.iter_lines():
            if not line:
                continue
            
            line_str = line.decode('utf-8')
            
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                
                if data_str == '[DONE]':
                    break
                
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue

