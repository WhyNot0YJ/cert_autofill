from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    from .config import config
    app.config.from_object(config[config_name])
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'generated_files'), exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # CORS配置
    CORS(app)
    
    # 注册蓝图
    from .api.routes import api_bp
    from .api.mvp_routes import mvp_bp
    from .api.template_routes import template_bp
    from .api.application_routes import application_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(mvp_bp, url_prefix='/api/mvp')
    app.register_blueprint(template_bp, url_prefix='/api/template')
    app.register_blueprint(application_bp, url_prefix='/api/application')
    
    # 创建数据库表
    with app.app_context():
        # 只导入需要的模型
        from .models import Document, DocumentUpload, FormData
        
        # 只创建FormData表和其他必要的表
        db.create_all()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)