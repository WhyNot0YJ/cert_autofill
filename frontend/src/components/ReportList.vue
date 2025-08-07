<template>
  <div class="report-list">
    <!-- 搜索和筛选 -->
    <div class="list-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索报告编号或标题"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      <div class="filter-box">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
          <el-option label="全部" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="已完成" value="completed" />
          <el-option label="已批准" value="approved" />
        </el-select>
      </div>
    </div>

    <!-- 报告列表 -->
    <div class="list-content">
      <el-table
        :data="filteredReports"
        v-loading="loading"
        stripe
        class="report-table"
      >
        <el-table-column prop="report_number" label="报告编号" width="180" />
        
        <el-table-column prop="title" label="标题" min-width="250">
          <template #default="{ row }">
            <div class="report-title">
              <div class="title-main">{{ row.title }}</div>
              <div class="title-type">{{ row.report_type }}</div>
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
        
        <el-table-column prop="test_date" label="测试日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.test_date) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="completed_at" label="完成时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.completed_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row)">查看</el-button>
            <el-button size="small" type="primary" @click="downloadReport(row)">下载</el-button>
            <el-button size="small" type="success" @click="approveReport(row)">批准</el-button>
            <el-button size="small" type="danger" @click="deleteReport(row)">删除</el-button>
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

interface Report {
  id: number;
  report_number: string;
  title: string;
  report_type: string;
  status: string;
  test_date: string;
  completed_at: string;
}

const loading = ref(false);
const reports = ref<Report[]>([]);
const searchQuery = ref('');
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 模拟数据
const mockReports: Report[] = [
  {
    id: 1,
    report_number: "REP20240101001",
    title: "4.76mm普通PVB AY7前风窗夹层测试报告",
    report_type: "测试报告",
    status: "completed",
    test_date: "2024-01-10T00:00:00",
    completed_at: "2024-01-12T00:00:00"
  },
  {
    id: 2,
    report_number: "REP20240102001",
    title: "5.0mm钢化玻璃前风窗测试报告",
    report_type: "测试报告",
    status: "approved",
    test_date: "2024-01-15T00:00:00",
    completed_at: "2024-01-18T00:00:00"
  },
  {
    id: 3,
    report_number: "REP20240103001",
    title: "汽车安全玻璃审核报告",
    report_type: "审核报告",
    status: "draft",
    test_date: "2024-01-20T00:00:00",
    completed_at: ""
  }
];

const filteredReports = computed(() => {
  let filtered = reports.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(report => 
      report.report_number.toLowerCase().includes(query) ||
      report.title.toLowerCase().includes(query)
    );
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(report => report.status === statusFilter.value);
  }
  
  return filtered;
});

function getStatusType(status: string): string {
  const statusMap: Record<string, string> = {
    'draft': 'info',
    'completed': 'primary',
    'approved': 'success'
  };
  return statusMap[status] || 'info';
}

function getStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'draft': '草稿',
    'completed': '已完成',
    'approved': '已批准'
  };
  return statusMap[status] || status;
}

function formatDate(dateString: string): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}

function handleSearch() {
  // 实际项目中这里会调用API
  console.log('搜索:', searchQuery.value);
}

function handleSizeChange(size: number) {
  pageSize.value = size;
  loadReports();
}

function handleCurrentChange(page: number) {
  currentPage.value = page;
  loadReports();
}

function loadReports() {
  loading.value = true;
  // 模拟API调用
  setTimeout(() => {
    reports.value = mockReports;
    total.value = mockReports.length;
    loading.value = false;
  }, 500);
}

function viewReport(report: Report) {
  ElMessage.info(`查看报告: ${report.report_number}`);
}

function downloadReport(report: Report) {
  ElMessage.success(`开始下载报告: ${report.report_number}`);
  // 实际项目中这里会调用下载API
}

function approveReport(report: Report) {
  ElMessageBox.confirm(
    `确定要批准报告 "${report.report_number}" 吗？`,
    '确认批准',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('报告已批准');
  }).catch(() => {
    ElMessage.info('已取消批准');
  });
}

function deleteReport(report: Report) {
  ElMessageBox.confirm(
    `确定要删除报告 "${report.report_number}" 吗？`,
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
  loadReports();
});
</script>

<style scoped>
.report-list {
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

.report-table {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
}

.report-title {
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