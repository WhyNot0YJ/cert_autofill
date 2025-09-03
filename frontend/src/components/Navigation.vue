<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <div class="logo">
          <div class="logo-graphic"></div>
          <div class="logo-text">
            <span class="logo-main">TÜV NORD</span>
            <span class="logo-sub">证书管理系统</span>
          </div>
        </div>
      </div>
      
      <div class="nav-links">
        <router-link to="/" class="nav-link" active-class="active">
          <el-button :type="$route.path === '/' ? 'primary' : 'default'" size="small">
            <el-icon><Document /></el-icon>
            文档处理
          </el-button>
        </router-link>
        

        <router-link to="/applications" class="nav-link" active-class="active">
          <el-button :type="$route.path === '/applications' ? 'primary' : 'default'" size="small">
            <el-icon><Document /></el-icon>
            申请书管理
          </el-button>
        </router-link>
        
        <router-link to="/companies" class="nav-link" active-class="active">
          <el-button :type="$route.path === '/companies' ? 'primary' : 'default'" size="small">
            <el-icon><OfficeBuilding /></el-icon>
            公司管理
          </el-button>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { Document, OfficeBuilding } from '@element-plus/icons-vue';
</script>

<style scoped>
.navigation {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-graphic {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  border-radius: 8px;
  position: relative;
}

.logo-graphic::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 4px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-main {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2A3B8F;
}

.logo-sub {
  font-size: 0.8rem;
  color: #666;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
}

.nav-link.active .el-button {
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%) !important;
  color: white !important;
}
</style> 