import os
import time
import json
import traceback
from flask import Flask, request, jsonify, send_file, render_template, Response, stream_with_context, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import Config
from ai_service import AIService
from ppt_generator import generate_ppt

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

Config.init_app()

ai_service = AIService()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_TEMPLATE_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico',mimetype='image/favicon.icon')

@app.route('/api/test', methods=['GET'])
def test_api():
    try:
        return jsonify({
            'success': True,
            'message': 'API 连接正常',
            'config': {
                'api_configured': bool(Config.API_KEY),
                'model': Config.AI_MODEL
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-outline', methods=['POST'])
def generate_outline():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        chapters = data.get('chapters', 5)
        
        if not topic:
            return jsonify({
                'success': False,
                'error': '请提供主题'
            }), 400
        
        outline = ai_service.generate_outline(topic, chapters)
        
        return jsonify({
            'success': True,
            'outline': outline
        })
        
    except Exception as e:
        app.logger.error(f"生成大纲失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'生成大纲失败: {str(e)}'
        }), 500


@app.route('/api/generate-outline-stream', methods=['POST'])
def generate_outline_stream():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        chapters = data.get('chapters', 5)
        
        if not topic:
            def error_stream():
                yield f"data: {json.dumps({'error': '请提供主题'})}\n\n"
            return Response(error_stream(), mimetype='text/event-stream')
        
        def generate():
            try:
                for chunk in ai_service.generate_outline_stream(topic, chapters):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield f"data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        app.logger.error(f"生成大纲失败: {str(e)}\n{traceback.format_exc()}")
        def error_stream():
            yield f"data: {json.dumps({'error': f'生成大纲失败: {str(e)}'})}\n\n"
        return Response(error_stream(), mimetype='text/event-stream')


@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        outline = data.get('outline', '')
        
        if not outline:
            return jsonify({
                'success': False,
                'error': '请提供大纲'
            }), 400
        
        content = ai_service.generate_content(outline)
        
        return jsonify({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        app.logger.error(f"生成内容失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'生成内容失败: {str(e)}'
        }), 500


@app.route('/api/generate-content-stream', methods=['POST'])
def generate_content_stream():
    try:
        data = request.get_json()
        outline = data.get('outline', '')
        
        if not outline:
            def error_stream():
                yield f"data: {json.dumps({'error': '请提供大纲'})}\n\n"
            return Response(error_stream(), mimetype='text/event-stream')
        
        def generate():
            try:
                for chunk in ai_service.generate_content_stream(outline):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield f"data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
    except Exception as e:
        app.logger.error(f"生成内容失败: {str(e)}\n{traceback.format_exc()}")
        def error_stream():
            yield f"data: {json.dumps({'error': f'生成内容失败: {str(e)}'})}\n\n"
        return Response(error_stream(), mimetype='text/event-stream')


@app.route('/api/upload-template', methods=['POST'])
def upload_template():
    try:
        if 'template' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['template']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '只支持 .pptx 格式的文件'
            }), 400
        
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > Config.MAX_TEMPLATE_SIZE:
            max_size_mb = Config.MAX_TEMPLATE_SIZE / (1024 * 1024)
            return jsonify({
                'success': False,
                'error': f'文件大小超过限制（最大 {max_size_mb:.0f}MB）'
            }), 400
        
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        unique_filename = f"template_{timestamp}_{filename}"
        filepath = os.path.join(Config.CUSTOM_TEMPLATES_FOLDER, unique_filename)
        
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'templateId': unique_filename,
            'fileName': filename,
            'fileSize': file_size
        })
        
    except Exception as e:
        app.logger.error(f"上传模板失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'上传模板失败: {str(e)}'
        }), 500


@app.route('/api/generate-ppt', methods=['POST'])
def generate_ppt_api():
    try:
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', 'AI 生成的 PPT')
        subtitle = data.get('subtitle', '')
        template_id = data.get('templateId', None)
        
        if not content:
            return jsonify({
                'success': False,
                'error': '请提供内容'
            }), 400
        
        template_path = None
        if template_id:
            template_path = os.path.join(Config.CUSTOM_TEMPLATES_FOLDER, template_id)
            if not os.path.exists(template_path):
                return jsonify({
                    'success': False,
                    'error': '模板文件不存在'
                }), 400
        
        timestamp = int(time.time())
        output_filename = f"ppt_{timestamp}.pptx"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
        
        result_path = generate_ppt(
            markdown_content=content,
            output_path=output_path,
            template_path=template_path,
            title=title,
            subtitle=subtitle
        )
        
        if not os.path.exists(result_path):
            raise Exception("PPT 文件生成失败")
        
        file_size = os.path.getsize(result_path)
        
        return jsonify({
            'success': True,
            'fileId': output_filename,
            'fileSize': file_size,
            'downloadUrl': f'/api/download-ppt/{output_filename}'
        })
        
    except Exception as e:
        app.logger.error(f"生成 PPT 失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'生成 PPT 失败: {str(e)}'
        }), 500


@app.route('/api/download-ppt/<file_id>', methods=['GET'])
def download_ppt(file_id):
    try:
        file_id = secure_filename(file_id)
        file_path = os.path.join(Config.OUTPUT_FOLDER, file_id)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在或已过期'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_id,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        app.logger.error(f"下载文件失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'下载文件失败: {str(e)}'
        }), 500


@app.route('/api/list-templates', methods=['GET'])
def list_templates():
    try:
        templates = []
        if os.path.exists(Config.CUSTOM_TEMPLATES_FOLDER):
            for filename in os.listdir(Config.CUSTOM_TEMPLATES_FOLDER):
                if filename.endswith('.pptx'):
                    filepath = os.path.join(Config.CUSTOM_TEMPLATES_FOLDER, filename)
                    file_size = os.path.getsize(filepath)
                    templates.append({
                        'id': filename,
                        'name': filename,
                        'size': file_size
                    })
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        app.logger.error(f"列出模板失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'列出模板失败: {str(e)}'
        }), 500


@app.route('/api/get-api-config', methods=['GET'])
def get_api_config():
    try:
        return jsonify({
            'success': True,
            'config': {
                'api_key': Config.API_KEY if Config.API_KEY else None,
                'api_base': Config.API_BASE_URL if Config.API_BASE_URL else None,
                'model': Config.AI_MODEL
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/save-api-config', methods=['POST'])
def save_api_config():
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        api_base = data.get('api_base')
        model = data.get('model')
        
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        env_content = {}
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        if api_key:
            env_content['API_KEY'] = api_key
        if api_base:
            env_content['API_BASE_URL'] = api_base
        if model:
            env_content['AI_MODEL'] = model
        
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        return jsonify({
            'success': True,
            'message': 'API配置已保存'
        })
        
    except Exception as e:
        app.logger.error(f"保存API配置失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'保存API配置失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("AI PPT 生成器启动中...")
    print("=" * 60)
    print(f"上传目录: {Config.UPLOAD_FOLDER}")
    print(f"输出目录: {Config.OUTPUT_FOLDER}")
    print(f"模板目录: {Config.CUSTOM_TEMPLATES_FOLDER}")
    print(f"AI 模型: {Config.AI_MODEL}")
    print(f"API Key: {'已配置' if Config.API_KEY else '未配置'}")
    print("=" * 60)
    print("服务运行在: http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )

