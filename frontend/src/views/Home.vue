<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo">
            <div class="logo-graphic"></div>
            <div class="logo-text">
              <span class="logo-main">TÜV NORD</span>
              <span class="logo-sub">Mobilität</span>
            </div>
          </div>
        </div>
        <h1 class="app-title">证书管理系统</h1>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 功能导航 -->
        <nav class="feature-nav">
          <div class="nav-item" :class="{ active: activeTab === 'enterprises' }" @click="activeTab = 'enterprises'">
            <div class="nav-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 21V19C19 17.9391 18.5786 16.9217 17.8284 16.1716C17.0783 15.4214 16.0609 15 15 15H9C7.93913 15 6.92172 15.4214 6.17157 16.1716C5.42143 16.9217 5 17.9391 5 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span>企业管理</span>
          </div>
          
          <div class="nav-item" :class="{ active: activeTab === 'applications' }" @click="activeTab = 'applications'">
            <div class="nav-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span>申请书管理</span>
          </div>
          
          <div class="nav-item" :class="{ active: activeTab === 'certificates' }" @click="activeTab = 'certificates'">
            <div class="nav-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span>证书管理</span>
          </div>
          
          <div class="nav-item" :class="{ active: activeTab === 'reports' }" @click="activeTab = 'reports'">
            <div class="nav-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 13H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 17H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span>报告管理</span>
          </div>
        </nav>

        <!-- 内容区域 -->
        <div class="content-area">
          <!-- 企业管理 -->
          <div v-if="activeTab === 'enterprises'" class="tab-content">
            <div class="content-header">
              <h2>企业管理</h2>
              <el-button type="primary" @click="showEnterpriseForm = true">
                <el-icon><Plus /></el-icon>
                添加企业
              </el-button>
            </div>
            
            <enterprise-list />
          </div>

          <!-- 申请书管理 -->
          <div v-if="activeTab === 'applications'" class="tab-content">
            <div class="content-header">
              <h2>申请书管理</h2>
              <el-button type="primary" @click="showApplicationForm = true">
                <el-icon><Plus /></el-icon>
                新建申请书
              </el-button>
            </div>
            
            <application-list />
          </div>

          <!-- 证书管理 -->
          <div v-if="activeTab === 'certificates'" class="tab-content">
            <div class="content-header">
              <h2>证书管理</h2>
              <el-button type="primary" @click="showCertificateForm = true">
                <el-icon><Plus /></el-icon>
                生成证书
              </el-button>
            </div>
            
            <certificate-list />
          </div>

          <!-- 报告管理 -->
          <div v-if="activeTab === 'reports'" class="tab-content">
            <div class="content-header">
              <h2>报告管理</h2>
              <el-button type="primary" @click="showReportForm = true">
                <el-icon><Plus /></el-icon>
                生成报告
              </el-button>
            </div>
            
            <report-list />
          </div>
        </div>
      </div>
    </main>

    <!-- 错误信息 -->
    <error-message v-if="error" :message="error" />
  </div>
</template>

<script setup lang="ts">
import { Plus } from '@element-plus/icons-vue';
import { ref } from 'vue';
import ApplicationList from '../components/ApplicationList.vue';
import CertificateList from '../components/CertificateList.vue';
import EnterpriseList from '../components/EnterpriseList.vue';
import ErrorMessage from '../components/ErrorMessage.vue';
import ReportList from '../components/ReportList.vue';

const activeTab = ref('enterprises');
const error = ref('');
const showEnterpriseForm = ref(false);
const showApplicationForm = ref(false);
const showCertificateForm = ref(false);
const showReportForm = ref(false);
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 顶部导航栏 */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo-section {
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-graphic {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.logo-graphic::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  border: 2px solid white;
  border-radius: 50% 50% 0 50%;
  transform: rotate(-45deg);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.logo-main {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2A3B8F;
  letter-spacing: 0.5px;
}

.logo-sub {
  font-size: 0.75rem;
  font-weight: 500;
  color: #2A3B8F;
  opacity: 0.8;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

/* 主要内容区域 */
.main-content {
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  gap: 2rem;
}

/* 功能导航 */
.feature-nav {
  width: 240px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: fit-content;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.nav-item:hover {
  background: rgba(42, 59, 143, 0.1);
}

.nav-item.active {
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  color: white;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.nav-item span {
  font-weight: 500;
}

/* 内容区域 */
.content-area {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.content-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.tab-content {
  min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
    padding: 0 1rem;
  }
  
  .feature-nav {
    width: 100%;
    order: 2;
  }
  
  .content-area {
    order: 1;
    padding: 1.5rem;
  }
  
  .content-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>