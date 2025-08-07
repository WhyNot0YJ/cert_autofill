<template>
  <div class="application-list">
    <!-- 搜索和筛选 -->
    <div class="list-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索申请书编号、标题、批准号或公司名称"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      <div class="filter-box">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="已提交" value="submitted" />
          <el-option label="处理中" value="processing" />
          <el-option label="已批准" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>
      </div>
    </div>

    <!-- 申请书列表 -->
    <div class="list-content">
      <el-table
        :data="filteredApplications"
        v-loading="loading"
        stripe
        class="application-table"
      >
        <el-table-column prop="application_number" label="申请书编号" width="180" />
        
        <el-table-column prop="approval_no" label="批准号" width="150" />
        
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <div class="application-title">
              <div class="title-main">{{ row.title }}</div>
              <div class="title-type">{{ row.application_type }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="company_name" label="公司名称" width="200" />
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="information_folder_no" label="信息文件夹号" width="150" />
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewApplication(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editApplication(row)">编辑</el-button>
            <el-button size="small" type="success" @click="uploadFile(row)">上传文件</el-button>
            <el-button size="small" type="danger" @click="deleteApplication(row)">删除</el-button>
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
import { ElMessage, ElMessageBox } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { applicationAPI } from '../api/application';

interface Application {
  id: number;
  application_number: string;
  approval_no: string;
  title: string;
  application_type: string;
  status: string;
  information_folder_no: string;
  safety_class: string;
  company_name: string;
  created_at: string;
  updated_at: string;
}

const loading = ref(false);
const applications = ref<Application[]>([]);
const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const filteredApplications = computed(() => {
  let filtered = applications.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(application => 
      application.application_number.toLowerCase().includes(query) ||
      application.title.toLowerCase().includes(query) ||
      application.approval_no.toLowerCase().includes(query) ||
      (application.company_name && application.company_name.toLowerCase().includes(query))
    );
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(application => application.status === statusFilter.value);
  }
  
  return filtered;
});

function getStatusType(status: string): string {
  const statusMap: Record<string, string> = {
    'draft': 'info',
    'submitted': 'warning',
    'processing': 'primary',
    'approved': 'success',
    'rejected': 'danger'
  };
  return statusMap[status] || 'info';
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'processing': '处理中',
    'approved': '已批准',
    'rejected': '已拒绝'
  };
  return statusMap[status] || status;
}

function formatDate(dateString: string): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

async function handleSearch() {
  await loadApplications();
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadApplications();
}

function handleCurrentChange(page: number) {
  currentPage.value = page;
  loadApplications();
}

async function loadApplications() {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      per_page: pageSize.value
    };
    
    if (searchQuery.value) {
      params.search = searchQuery.value;
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value;
    }
    
    const response = await applicationAPI.getApplications(params);
    
    // 添加调试信息
    console.log('API Response:', response);
    console.log('Response data:', response.data);
    console.log('Success flag:', response.data.success);
    
    if (response.data.success) {
      applications.value = response.data.data.applications;
      total.value = response.data.data.total;
      console.log('Applications loaded:', applications.value);
    } else {
      console.error('API returned success: false');
      ElMessage.error('获取申请书列表失败');
    }
  } catch (error) {
    console.error('加载申请书失败:', error);
    ElMessage.error('加载申请书失败');
  } finally {
    loading.value = false;
  }
}

function viewApplication(application: Application) {
  ElMessage.info(`查看申请书: ${application.application_number}`);
}

function editApplication(application: Application) {
  ElMessage.info(`编辑申请书: ${application.application_number}`);
}

function uploadFile(application: Application) {
  ElMessage.info(`上传文件到申请书: ${application.application_number}`);
}

function deleteApplication(application: Application) {
  ElMessageBox.confirm(
    `确定要删除申请书 "${application.application_number}" 吗？`,
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
  loadApplications();
});
</script>

<style scoped>
.application-list {
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

.application-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.application-title {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.title-main {
  font-weight: 500;
  color: #1a1a1a;
}

.title-type {
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