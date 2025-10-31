import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    

    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    

    API_URL = os.getenv('API_URL', 'https://api.deepseek.com/v1/chat/completions')
    API_KEY = os.getenv('API_KEY', '')
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
    CUSTOM_TEMPLATES_FOLDER = os.path.join(UPLOAD_FOLDER, 'custom_templates')
    

    MAX_TEMPLATE_SIZE = int(os.getenv('MAX_TEMPLATE_SIZE', '50')) * 1024 * 1024  # MB to bytes
    ALLOWED_TEMPLATE_EXTENSIONS = {'pptx'}
    

    DEFAULT_SLIDE_WIDTH = int(os.getenv('DEFAULT_SLIDE_WIDTH', '9144000'))
    DEFAULT_SLIDE_HEIGHT = int(os.getenv('DEFAULT_SLIDE_HEIGHT', '6858000'))
    

    AI_MODEL = 'deepseek-chat'
    AI_TEMPERATURE = 0.7
    AI_MAX_TOKENS_OUTLINE = 4096
    AI_MAX_TOKENS_CONTENT = 8192
    

    @staticmethod
    def init_app():
        for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.CUSTOM_TEMPLATES_FOLDER]:
            os.makedirs(folder, exist_ok=True)

