<template>
  <div id="app">
    <Navigation />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import Navigation from './components/Navigation.vue'
// 路由组件会自动加载
</script>

<style>
/* 全局样式重置 */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}

/* Element Plus 组件样式覆盖 */
.el-button--primary {
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%) !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}

.el-button--primary:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(42, 59, 143, 0.4) !important;
}

.el-button--primary:active {
  transform: translateY(0) !important;
}

.el-input__wrapper {
  background: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  transition: all 0.3s ease !important;
}

.el-input__wrapper:hover {
  border-color: #2A3B8F !important;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1) !important;
}

.el-input__wrapper.is-focus {
  border-color: #2A3B8F !important;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1) !important;
}

.el-textarea__inner {
  background: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
  transition: all 0.3s ease !important;
}

.el-textarea__inner:hover {
  border-color: #2A3B8F !important;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1) !important;
}

.el-textarea__inner:focus {
  border-color: #2A3B8F !important;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1) !important;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(42, 59, 143, 0.3);
  border-radius: 4px;
  transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(42, 59, 143, 0.5);
}

/* 选择文本样式 */
::selection {
  background: rgba(42, 59, 143, 0.2);
  color: #1a1a1a;
}

/* 焦点样式 */
*:focus {
  outline: none;
}

*:focus-visible {
  outline: 2px solid #2A3B8F;
  outline-offset: 2px;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    transform: translateX(-20px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fade-in {
  animation: fadeIn 0.6s ease-out;
}

.slide-in {
  animation: slideIn 0.4s ease-out;
}

/* 响应式字体大小 */
@media (max-width: 768px) {
  html {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  html {
    font-size: 13px;
  }
}
</style> 