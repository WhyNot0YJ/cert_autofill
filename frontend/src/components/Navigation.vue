<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h1 class="nav-title">证书管理系统</h1>
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

.nav-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2A3B8F;
  margin: 0;
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