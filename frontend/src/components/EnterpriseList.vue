<template>
  <div class="enterprise-list">
    <!-- 搜索和筛选 -->
    <div class="list-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索企业名称、英文名或注册号"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      <div class="filter-box">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
          <el-option label="全部" value="" />
          <el-option label="活跃" value="active" />
          <el-option label="非活跃" value="inactive" />
        </el-select>
      </div>
    </div>

    <!-- 企业列表 -->
    <div class="list-content">
      <el-table
        :data="filteredEnterprises"
        v-loading="loading"
        stripe
        class="enterprise-table"
      >
        <el-table-column prop="name" label="企业名称" min-width="200">
          <template #default="{ row }">
            <div class="enterprise-name">
              <div class="name-main">{{ row.name }}</div>
              <div class="name-english">{{ row.english_name }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="registration_number" label="注册号" width="180" />
        
        <el-table-column prop="contact_person" label="联系人" width="120" />
        
        <el-table-column prop="contact_phone" label="联系电话" width="140" />
        
        <el-table-column prop="industry_type" label="行业类型" width="120" />
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewEnterprise(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editEnterprise(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteEnterprise(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search } from '@element-plus/icons-vue';

interface Enterprise {
  id: number;
  name: string;
  english_name: string;
  registration_number: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  industry_type: string;
  created_at: string;
}

const loading = ref(false);
const enterprises = ref<Enterprise[]>([]);
const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 模拟数据
const mockEnterprises: Enterprise[] = [
  {
    id: 1,
    name: "广州福耀玻璃有限公司",
    english_name: "Guangzhou Fuyao Glass Co., Ltd.",
    registration_number: "91440101MA9CQ8YX3R",
    contact_person: "张三",
    contact_phone: "020-12345678",
    contact_email: "contact@fuyao.com",
    industry_type: "制造业",
    created_at: "2024-01-01T00:00:00"
  },
  {
    id: 2,
    name: "上海汽车玻璃有限公司",
    english_name: "Shanghai Automotive Glass Co., Ltd.",
    registration_number: "91310000MA1FL4YX3R",
    contact_person: "李四",
    contact_phone: "021-87654321",
    contact_email: "info@saglass.com",
    industry_type: "制造业",
    created_at: "2024-01-02T00:00:00"
  },
  {
    id: 3,
    name: "北京玻璃集团",
    english_name: "Beijing Glass Group",
    registration_number: "91110000MA1FL4YX3R",
    contact_person: "王五",
    contact_phone: "010-87654321",
    contact_email: "info@bjglass.com",
    industry_type: "制造业",
    created_at: "2024-01-03T00:00:00"
  }
];

const filteredEnterprises = computed(() => {
  let filtered = enterprises.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(enterprise => 
      enterprise.name.toLowerCase().includes(query) ||
      enterprise.english_name.toLowerCase().includes(query) ||
      enterprise.registration_number.toLowerCase().includes(query)
    );
  }
  
  return filtered;
});

function formatDate(dateString: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

function handleSearch() {
  // 实际项目中这里会调用API
  console.log('搜索:', searchQuery.value);
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadEnterprises();
}

function handleCurrentChange(page: number) {
  currentPage.value = page;
  loadEnterprises();
}

function loadEnterprises() {
  loading.value = true;
  // 模拟API调用
  setTimeout(() => {
    enterprises.value = mockEnterprises;
    total.value = mockEnterprises.length;
    loading.value = false;
  }, 500);
}

function viewEnterprise(enterprise: Enterprise) {
  ElMessage.info(`查看企业: ${enterprise.name}`);
}

function editEnterprise(enterprise: Enterprise) {
  ElMessage.info(`编辑企业: ${enterprise.name}`);
}

function deleteEnterprise(enterprise: Enterprise) {
  ElMessageBox.confirm(
    `确定要删除企业 "${enterprise.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('删除成功');
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
}

onMounted(() => {
  loadEnterprises();
});
</script>

<style scoped>
.enterprise-list {
  width: 100%;
}

.list-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.filter-box {
  flex-shrink: 0;
}

.list-content {
  margin-bottom: 1.5rem;
}

.enterprise-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.enterprise-name {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.name-main {
  font-weight: 500;
  color: #1a1a1a;
}

.name-english {
  font-size: 0.875rem;
  color: #6b7280;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .list-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
}
</style> 