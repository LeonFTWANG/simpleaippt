let currentStep = 1;
let outlineData = '';
let contentData = '';
let uploadedTemplateId = null;

const API_BASE = '/api';


function setLoading(buttonElement, isLoading) {
    const btnText = buttonElement.querySelector('.btn-text');
    const btnLoading = buttonElement.querySelector('.btn-loading');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        buttonElement.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        buttonElement.disabled = false;
    }
}


function showError(message) {
    alert('错误: ' + message);
}


function updateStepIndicator(step) {
    document.querySelectorAll('.step').forEach((s, index) => {
        s.classList.remove('active');
        const stepNum = index + 1;
        

        if (stepNum < step) {
            s.classList.add('completed');
        } else {
            s.classList.remove('completed');
        }
    });
    document.querySelector(`.step[data-step="${step}"]`).classList.add('active');
    currentStep = step;
}


function switchToStep(stepNumber) {

    document.getElementById('step1').style.display = 'none';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('step3').style.display = 'none';
    

    document.getElementById('step' + stepNumber).style.display = 'block';
    

    updateStepIndicator(stepNumber);
    

    window.scrollTo({ top: 0, behavior: 'smooth' });
    

    if (stepNumber === 3) {
        loadTemplates();
    }
}


async function generateOutline(event) {
    const topic = document.getElementById('topic').value.trim();
    const chapters = parseInt(document.getElementById('chapters').value);
    const button = event ? event.currentTarget : document.querySelector('#step1 .btn-primary');
    
    if (!topic) {
        showError('请输入PPT主题');
        return;
    }
    
    setLoading(button, true);
    

    const resultDiv = document.getElementById('outline-result');
    const contentDiv = document.getElementById('outline-content');
    contentDiv.value = '正在生成大纲...\n\n';
    resultDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/generate-outline-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic, chapters })
        });
        
        if (!response.ok) {
            throw new Error('生成大纲失败');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        contentDiv.value = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        const json = JSON.parse(data);
                        if (json.content) {
                            contentDiv.value += json.content;

                            contentDiv.scrollTop = contentDiv.scrollHeight;
                        }
                        if (json.error) {
                            throw new Error(json.error);
                        }
                    } catch (e) {
                        if (data !== '[DONE]') {
                            console.error('解析错误:', e);
                        }
                    }
                }
            }
        }
        

        outlineData = contentDiv.value;
        

        document.getElementById('ppt-title').value = topic;
        
    } catch (error) {
        showError(error.message);
        resultDiv.style.display = 'none';
    } finally {
        setLoading(button, false);
    }
}


function handleMarkdownFileUpload(event) {
    const file = event.target.files[0];
    
    if (!file) {
        return;
    }
    

    const fileNameSpan = document.getElementById('md-file-name');
    fileNameSpan.textContent = `已选择: ${file.name}`;
    fileNameSpan.style.color = '#4CAF50';
    

    const validExtensions = ['.md', '.markdown', '.txt'];
    const fileName = file.name.toLowerCase();
    const isValidFile = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValidFile) {
        showError('请选择有效的Markdown文件（.md、.markdown 或 .txt）');
        fileNameSpan.textContent = '';
        event.target.value = '';
        return;
    }
    

    if (file.size > 5 * 1024 * 1024) {
        showError('文件大小不能超过 5MB');
        fileNameSpan.textContent = '';
        event.target.value = '';
        return;
    }
    

    const reader = new FileReader();
    
    reader.onload = function(e) {
        const content = e.target.result;
        

        if (!content || content.trim().length === 0) {
            showError('文件内容为空');
            fileNameSpan.textContent = '';
            event.target.value = '';
            return;
        }
        

        const resultDiv = document.getElementById('outline-result');
        const contentDiv = document.getElementById('outline-content');
        

        contentDiv.value = content;
        resultDiv.style.display = 'block';
        

        outlineData = content;
        

        document.querySelector('.step[data-step="1"]').classList.add('completed');
        

        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        

        fileNameSpan.textContent = `✅ ${file.name} 加载成功`;
        

        setTimeout(() => {
            event.target.value = '';
        }, 100);
    };
    
    reader.onerror = function() {
        showError('文件读取失败，请重试');
        fileNameSpan.textContent = '';
        event.target.value = '';
    };
    

    reader.readAsText(file, 'UTF-8');
}


function goToStep2() {
    switchToStep(2);
}


async function generateContent(event) {
    const button = event ? event.currentTarget : document.querySelector('#step2 .btn-primary');
    
    if (!outlineData) {
        showError('请先生成大纲');
        return;
    }
    
    setLoading(button, true);
    

    const resultDiv = document.getElementById('content-result');
    const contentDiv = document.getElementById('content-content');
    contentDiv.value = '正在生成详细内容...\n\n';
    resultDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/generate-content-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ outline: outlineData })
        });
        
        if (!response.ok) {
            throw new Error('生成内容失败');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        contentDiv.value = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        const json = JSON.parse(data);
                        if (json.content) {
                            contentDiv.value += json.content;

                            contentDiv.scrollTop = contentDiv.scrollHeight;
                        }
                        if (json.error) {
                            throw new Error(json.error);
                        }
                    } catch (e) {
                        if (data !== '[DONE]') {
                            console.error('解析错误:', e);
                        }
                    }
                }
            }
        }
        

        contentData = contentDiv.value;
        
    } catch (error) {
        showError(error.message);
        resultDiv.style.display = 'none';
    } finally {
        setLoading(button, false);
    }
}


function skipToStep3() {

    document.querySelector('input[name="content-source"][value="outline"]').checked = true;
    
    switchToStep(3);
}


function goToStep3() {
    switchToStep(3);
}


function toggleTemplateSection() {
    const useTemplate = document.getElementById('use-template').checked;
    document.getElementById('template-section').style.display = useTemplate ? 'block' : 'none';
}


async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/list-templates`);
        const data = await response.json();
        
        if (data.success && data.templates.length > 0) {
            const select = document.getElementById('template-select');
            

            while (select.options.length > 1) {
                select.remove(1);
            }
            

            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                const sizeMB = (template.size / 1024 / 1024).toFixed(2);
                option.textContent = `${template.name} (${sizeMB}MB)`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载模板列表失败:', error);
    }
}


function handleTemplateSelect() {
    const fileInput = document.getElementById('template-file');
    const file = fileInput.files[0];
    
    if (!file) return;
    

    if (!file.name.endsWith('.pptx')) {
        showError('只支持 .pptx 格式的文件');
        fileInput.value = '';
        return;
    }
    

    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('文件大小超过限制（最大 50MB）');
        fileInput.value = '';
        return;
    }
}


async function uploadTemplate(event) {
    const fileInput = document.getElementById('template-file');
    const button = event ? event.currentTarget : document.querySelector('#upload-section .btn-secondary');
    
    if (!fileInput.files || !fileInput.files[0]) {
        showError('请选择模板文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('template', fileInput.files[0]);
    
    setLoading(button, true);
    
    try {
        const response = await fetch(`${API_BASE}/upload-template`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || '上传模板失败');
        }
        

        uploadedTemplateId = data.templateId;
        
        alert(`模板上传成功！\n文件名：${data.fileName}\n大小：${(data.fileSize / 1024 / 1024).toFixed(2)}MB`);
        

        fileInput.value = '';
        

        await loadTemplates();
        

        document.getElementById('template-select').value = uploadedTemplateId;
        
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(button, false);
    }
}


async function generatePPT(event) {
    const button = event ? event.currentTarget : document.querySelector('#step3 .btn-primary');
    const title = document.getElementById('ppt-title').value.trim() || '未命名PPT';
    const subtitle = document.getElementById('ppt-subtitle').value.trim();
    const useTemplate = document.getElementById('use-template').checked;
    const contentSource = document.querySelector('input[name="content-source"]:checked').value;
    

    let content;
    if (contentSource === 'outline') {

        const outlineTextarea = document.getElementById('outline-content');
        content = outlineTextarea ? outlineTextarea.value : outlineData;
        if (!content) {
            showError('请先生成大纲');
            return;
        }
    } else {

        const contentTextarea = document.getElementById('content-content');
        content = contentTextarea ? contentTextarea.value : contentData;
        if (!content) {
            showError('请先生成详细内容');
            return;
        }
    }
    

    let templateId = null;
    if (useTemplate) {
        const selectValue = document.getElementById('template-select').value;
        if (selectValue) {
            templateId = selectValue;
        } else if (uploadedTemplateId) {
            templateId = uploadedTemplateId;
        }
    }
    
    setLoading(button, true);
    
    try {
        const response = await fetch(`${API_BASE}/generate-ppt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content,
                title,
                subtitle,
                templateId
            })
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || '生成PPT失败');
        }
        

        const sizeMB = (data.fileSize / 1024 / 1024).toFixed(2);
        document.getElementById('ppt-info').textContent = `文件大小：${sizeMB}MB`;
        

        const downloadLink = document.getElementById('download-link');
        downloadLink.href = data.downloadUrl;
        downloadLink.download = data.fileId;
        

        document.getElementById('ppt-result').style.display = 'block';
        

        document.getElementById('ppt-result').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(button, false);
    }
}


function copyOutline() {
    const content = document.getElementById('outline-content').value || document.getElementById('outline-content').textContent;
    copyToClipboard(content, '大纲已复制到剪贴板！');
}


function copyContent() {
    const content = document.getElementById('content-content').value || document.getElementById('content-content').textContent;
    copyToClipboard(content, '内容已复制到剪贴板！');
}


function copyToClipboard(text, successMessage) {
    if (!text) {
        showError('没有可复制的内容');
        return;
    }
    

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
            .then(() => {
                alert(successMessage || '已复制到剪贴板！');
            })
            .catch(err => {

                fallbackCopyToClipboard(text, successMessage);
            });
    } else {

        fallbackCopyToClipboard(text, successMessage);
    }
}


function fallbackCopyToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            alert(successMessage || '已复制到剪贴板！');
        } else {
            showError('复制失败，请手动复制');
        }
    } catch (err) {
        showError('复制失败：' + err.message);
    }
    
    document.body.removeChild(textArea);
}


function toggleApiConfig() {
    const modal = document.getElementById('api-modal');
    if (modal.style.display === 'none') {
        modal.style.display = 'flex';

        loadCurrentApiConfig();
    } else {
        modal.style.display = 'none';
    }
}


async function loadCurrentApiConfig() {
    try {
        const response = await fetch(`${API_BASE}/get-api-config`);
        const data = await response.json();
        
        if (data.success) {

            if (data.config.api_key) {
                const key = data.config.api_key;
                const maskedKey = key.substring(0, 8) + '...' + key.substring(key.length - 4);
                document.getElementById('api-key-input').placeholder = `当前: ${maskedKey}`;
            }
            if (data.config.api_base) {
                document.getElementById('api-base-input').value = data.config.api_base;
            }
            if (data.config.model) {
                document.getElementById('api-model-input').value = data.config.model;
            }
        }
    } catch (error) {
        console.error('加载配置失败:', error);
    }
}


async function saveApiConfig() {
    const apiKey = document.getElementById('api-key-input').value.trim();
    const apiBase = document.getElementById('api-base-input').value.trim();
    const model = document.getElementById('api-model-input').value.trim();
    
    if (!apiKey && !document.getElementById('api-key-input').placeholder.includes('当前:')) {
        alert('⚠️ 请输入 API Key');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/save-api-config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                api_key: apiKey || undefined,
                api_base: apiBase || undefined,
                model: model || undefined
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ API 配置保存成功！\n\n⚠️ 请刷新页面使配置生效。');
            toggleApiConfig();
            // 重新检查API状态
            checkApiStatus();
        } else {
            alert('❌ 保存失败: ' + (data.error || '未知错误'));
        }
    } catch (error) {
        alert('❌ 保存失败: ' + error.message);
    }
}


function togglePasswordVisibility() {
    const input = document.getElementById('api-key-input');
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}


async function checkApiStatus() {
    const statusIcon = document.getElementById('status-icon');
    const statusText = document.getElementById('api-status-text');
    const statusDiv = document.getElementById('api-status');
    
    try {
        const response = await fetch(`${API_BASE}/test`);
        const data = await response.json();
        
        if (data.success && data.config.api_configured) {
            statusIcon.textContent = '✅';
            statusText.textContent = 'API 已配置';
            statusDiv.className = 'api-status status-ok';
        } else {
            statusIcon.textContent = '⚠️';
            statusText.textContent = 'API 未配置';
            statusDiv.className = 'api-status status-warning';
        }
    } catch (error) {
        statusIcon.textContent = '❌';
        statusText.textContent = 'API 连接失败';
        statusDiv.className = 'api-status status-error';
    }
}


document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI PPT 生成器已加载');
    

    checkApiStatus();
    

    fetch(`${API_BASE}/test`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('✅ API连接正常');
                console.log('API配置:', data.config);
            }
        })
        .catch(err => {
            console.error('❌ API连接失败:', err);
        });
});
