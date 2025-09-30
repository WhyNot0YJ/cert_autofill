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
    from .api.mvp_routes import mvp_bp
    from .api.application_routes import application_bp
    from .api.company_routes import company_bp
    app.register_blueprint(mvp_bp, url_prefix='/api/mvp')
    app.register_blueprint(application_bp, url_prefix='/api')
    app.register_blueprint(company_bp, url_prefix='/api')
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        """健康检查接口"""
        try:
            # 检查数据库连接
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return {"status": "healthy", "database": "connected"}, 200
        except Exception as e:
            return {"status": "unhealthy", "database": str(e)}, 500
    
    # 添加静态文件服务路由（直接在根级别，不带/api前缀）
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        """直接服务uploads文件夹的静态文件"""
        from flask import send_from_directory
        import os
        
        uploads_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(uploads_folder, filename)
        
        if not os.path.exists(file_path):
            from flask import jsonify
            return jsonify({"error": f"文件不存在: {filename}"}), 404
        
        return send_from_directory(uploads_folder, filename)
    
    # 创建数据库表
    with app.app_context():
        # 只导入需要的模型
        from .models import FormData, Company
        
        # 只创建FormData表和其他必要的表
        db.create_all()
    
    return app

# 创建应用实例供Gunicorn使用
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)