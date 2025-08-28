from app.main import create_app
import os

# 获取环境配置
env = os.environ.get('ENV', 'development')

# 直接获取端口配置
if env == 'production':
    backend_port = int(os.environ.get('BACKEND_PORT_PROD', 5001))
    debug_mode = False
else:
    backend_port = int(os.environ.get('BACKEND_PORT_DEV', 5000))
    debug_mode = True

app = create_app(env)

if __name__ == "__main__":
    print(f"启动后端服务 - 环境: {env}, 端口: {backend_port}, 调试模式: {debug_mode}")
    app.run(
        debug=debug_mode, 
        host='0.0.0.0', 
        port=backend_port
    ) 