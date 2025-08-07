<template>
  <div class="certificate-list">
    <!-- 搜索和筛选 -->
    <div class="list-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索证书编号或标题"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      <div class="filter-box">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
          <el-option label="全部" value="" />
          <el-option label="有效" value="active" />
          <el-option label="过期" value="expired" />
          <el-option label="暂停" value="suspended" />
          <el-option label="撤销" value="revoked" />
        </el-select>
      </div>
    </div>

    <!-- 证书列表 -->
    <div class="list-content">
      <el-table
        :data="filteredCertificates"
        v-loading="loading"
        stripe
        class="certificate-table"
      >
        <el-table-column prop="certificate_number" label="证书编号" width="180" />
        
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <div class="certificate-title">
              <div class="title-main">{{ row.title }}</div>
              <div class="title-type">{{ row.certificate_type }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="issue_date" label="发证日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.issue_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="expiry_date" label="有效期至" width="160">
          <template #default="{ row }">
            <div class="expiry-date" :class="{ 'expired': isExpired(row.expiry_date) }">
              {{ formatDate(row.expiry_date) }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewCertificate(row)">查看</el-button>
            <el-button size="small" type="primary" @click="downloadCertificate(row)">下载</el-button>
            <el-button size="small" type="success" @click="renewCertificate(row)">续期</el-button>
            <el-button size="small" type="danger" @click="revokeCertificate(row)">撤销</el-button>
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

interface Certificate {
  id: number;
  certificate_number: string;
  title: string;
  certificate_type: string;
  status: string;
  issue_date: string;
  expiry_date: string;
}

const loading = ref(false);
const certificates = ref<Certificate[]>([]);
const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 模拟数据
const mockCertificates: Certificate[] = [
  {
    id: 1,
    certificate_number: "CERT20240101001",
    title: "4.76mm普通PVB AY7前风窗夹层延伸认证证书",
    certificate_type: "玻璃认证",
    status: "active",
    issue_date: "2024-01-15T00:00:00",
    expiry_date: "2027-01-15T00:00:00"
  },
  {
    id: 2,
    certificate_number: "CERT20240102001",
    title: "5.0mm钢化玻璃前风窗认证证书",
    certificate_type: "玻璃认证",
    status: "active",
    issue_date: "2024-01-20T00:00:00",
    expiry_date: "2027-01-20T00:00:00"
  },
  {
    id: 3,
    certificate_number: "CERT20230101001",
    title: "汽车安全玻璃认证证书",
    certificate_type: "玻璃认证",
    status: "expired",
    issue_date: "2023-01-01T00:00:00",
    expiry_date: "2024-01-01T00:00:00"
  }
];

const filteredCertificates = computed(() => {
  let filtered = certificates.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(certificate => 
      certificate.certificate_number.toLowerCase().includes(query) ||
      certificate.title.toLowerCase().includes(query)
    );
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(certificate => certificate.status === statusFilter.value);
  }
  
  return filtered;
});

function getStatusType(status: string): string {
  const statusMap: Record<string, string> = {
    'active': 'success',
    'expired': 'danger',
    'suspended': 'warning',
    'revoked': 'info'
  };
  return statusMap[status] || 'info';
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'active': '有效',
    'expired': '过期',
    'suspended': '暂停',
    'revoked': '撤销'
  };
  return statusMap[status] || status;
}

function formatDate(dateString: string): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

function isExpired(expiryDate: string): boolean {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const now = new Date();
  return expiry < now;
}

function handleSearch() {
  // 实际项目中这里会调用API
  console.log('搜索:', searchQuery.value);
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadCertificates();
}

function handleCurrentChange(page: number) {
  currentPage.value = page;
  loadCertificates();
}

function loadCertificates() {
  loading.value = true;
  // 模拟API调用
  setTimeout(() => {
    certificates.value = mockCertificates;
    total.value = mockCertificates.length;
    loading.value = false;
  }, 500);
}

function viewCertificate(certificate: Certificate) {
  ElMessage.info(`查看证书: ${certificate.certificate_number}`);
}

function downloadCertificate(certificate: Certificate) {
  ElMessage.success(`开始下载证书: ${certificate.certificate_number}`);
  // 实际项目中这里会调用下载API
}

function renewCertificate(certificate: Certificate) {
  ElMessageBox.confirm(
    `确定要续期证书 "${certificate.certificate_number}" 吗？`,
    '确认续期',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('续期申请已提交');
  }).catch(() => {
    ElMessage.info('已取消续期');
  });
}

function revokeCertificate(certificate: Certificate) {
  ElMessageBox.confirm(
    `确定要撤销证书 "${certificate.certificate_number}" 吗？此操作不可逆！`,
    '确认撤销',
    {
      confirmButtonText: '确定撤销',
      cancelButtonText: '取消',
      type: 'error',
    }
  ).then(() => {
    ElMessage.success('证书已撤销');
  }).catch(() => {
    ElMessage.info('已取消撤销');
  });
}

onMounted(() => {
  loadCertificates();
});
</script>

<style scoped>
.certificate-list {
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

.certificate-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.certificate-title {
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

.expiry-date {
  font-weight: 500;
}

.expiry-date.expired {
  color: #f56c6c;
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