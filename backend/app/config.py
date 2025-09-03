import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cert_autofill.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 服务器配置
    SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost')  # 可通过环境变量配置
    
    # 端口配置
    ENV = os.environ.get('ENV', 'development')
    BACKEND_PORT_DEV = int(os.environ.get('BACKEND_PORT_DEV', 5000))
    BACKEND_PORT_PROD = int(os.environ.get('BACKEND_PORT_PROD', 5000))
    
    @property
    def BACKEND_PORT(self):
        """根据环境返回对应的端口"""
        if self.ENV == 'production':
            return self.BACKEND_PORT_PROD
        return self.BACKEND_PORT_DEV
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
