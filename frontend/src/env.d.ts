/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_PORT: string
  readonly VITE_FRONTEND_PORT: string
  // 更多环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 声明全局变量
declare global {
  const __BACKEND_PORT__: string
  const __FRONTEND_PORT__: string
}

export {}
