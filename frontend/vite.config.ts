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
  
  // 优先使用前端 .env 中的 VITE_ 变量作为后端地址与端口
  // 建议在 frontend 目录配置：
  // .env.development / .env.production
  //   VITE_SERVER_URL=http://127.0.0.1
  //   VITE_BACKEND_PORT=5000
  const viteServerUrl = env.VITE_SERVER_URL || ''
  const viteBackendPort = env.VITE_BACKEND_PORT ? parseInt(env.VITE_BACKEND_PORT) : undefined

  // 计算代理目标（优先 VITE_SERVER_URL；若未显式端口则补 VITE_BACKEND_PORT 或默认后端端口；
  // 否则回退到 127.0.0.1，避免 localhost 解析到 ::1）
  const computeBackendBase = (): string => {
    if (viteServerUrl) {
      try {
        const url = new URL(viteServerUrl)
        if (!url.port) {
          url.port = String(viteBackendPort ?? backendPort)
        }
        return `${url.protocol}//${url.hostname}:${url.port}`
      } catch {
        const host = viteServerUrl.replace(/\/$/, '')
        const port = viteBackendPort ?? backendPort
        return host.includes(':') ? host : `${host}:${port}`
      }
    }
    return `http://127.0.0.1:${viteBackendPort ?? backendPort}`
  }
  const backendBase = computeBackendBase()
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      port: frontendPort,
      // 在部分 Windows/Node 环境，localhost 可能解析为 ::1（IPv6），
      // 而后端监听在 IPv4，导致连接被拒绝。强制 IPv4 优先。
      dnsResultOrder: 'ipv4first',
      proxy: {
        // 代理uploads请求到后端
        '/uploads': {
          target: backendBase,
          changeOrigin: true,
          secure: false
        },
        // 代理API请求到后端
        '/api': {
          target: backendBase,
          changeOrigin: true,
          secure: false
        }
      }
    },
    define: {
      // 仅注入端口；服务器URL改为使用 VITE_ 变量或运行时回退
      __BACKEND_PORT__: JSON.stringify(backendPort)
    }
  }
})
