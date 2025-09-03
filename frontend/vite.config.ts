import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  // 获取端口配置
  const frontendPort = mode === 'production' 
    ? parseInt(env.FRONTEND_PORT_PROD || '81')
    : parseInt(env.FRONTEND_PORT_DEV || '80')
  
  const backendPort = mode === 'production'
    ? parseInt(env.BACKEND_PORT_PROD || '5001')
    : parseInt(env.BACKEND_PORT_DEV || '5000')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      port: frontendPort,
      proxy: {
        // 代理uploads请求到后端
        '/uploads': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
          secure: false
        },
        // 代理API请求到后端
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
          secure: false
        }
      }
    },
    define: {
      // 将后端端口和服务器URL注入到前端代码中
      __BACKEND_PORT__: JSON.stringify(backendPort),
      __SERVER_URL__: JSON.stringify(env.SERVER_URL || 'http://localhost')
    }
  }
})
