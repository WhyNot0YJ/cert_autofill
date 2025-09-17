<template>
  <div class="application-manager">
    <header class="application-header">
      <div class="header-content">
        <h1 class="page-title">申请书管理</h1>
      </div>
    </header>

    <main class="application-main">
      <div class="content-wrapper">
        <!-- 搜索和过滤 -->
        <div class="search-section">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-input
                v-model="searchQuery"
                placeholder="搜索申请书编号、标题、公司名称..."
                clearable
                @keyup.enter="handleSearch"
              >
                <template #append>
                  <el-button @click="handleSearch">
                    <el-icon><Search /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
                <el-option label="草稿" value="draft" />
                <el-option label="已提交" value="submitted" />
                <el-option label="处理中" value="processing" />
                <el-option label="已批准" value="approved" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </el-col>
            <el-col :span="4">
              <el-button @click="resetSearch">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 申请书列表 -->
        <div class="application-list">
          <el-table 
            :data="applications" 
            v-loading="loading" 
            style="width: 100%"
            @row-click="handleRowClick"
          >
            <el-table-column prop="application_number" label="申请书编号" width="200">
              <template #default="{ row }">
                <el-link type="primary" @click.stop="viewApplication(row.id)">
                  {{ row.application_number }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column prop="approval_no" label="批准号" width="260">
              <template #default="{ row }">
                <span>{{ row.approval_no || '未填写' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="company_name" label="公司名称" width="220">
              <template #default="{ row }">
                <span>{{ row.company_name || '未填写' }}</span>
              </template>
            </el-table-column>
            
            
            
            
            
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                <span>{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="updated_at" label="更新时间" width="180">
              <template #default="{ row }">
                <span>{{ formatDate(row.updated_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click.stop="viewApplication(row.id)">
                  <el-icon><View /></el-icon>
                  查看
                </el-button>
                <el-button size="small" type="primary" @click.stop="openEditor(row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button size="small" type="danger" @click.stop="deleteApplication(row.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
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

        <!-- 申请书详情对话框 -->
        <el-dialog 
          v-model="showDetailDialog" 
          title="申请书详情" 
          width="80%"
          :close-on-click-modal="false"
        >
          <div v-if="selectedApplication" class="application-detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="申请书编号">
                {{ selectedApplication.application_number }}
              </el-descriptions-item>
              
              
              <el-descriptions-item label="批准号">
                {{ selectedApplication.approval_no || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="信息文件夹号">
                {{ selectedApplication.information_folder_no || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="公司名称">
                {{ selectedApplication.company_name || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="公司地址">
                {{ selectedApplication.company_address || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">技术参数</el-divider>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="风窗厚度">
                {{ selectedApplication.windscreen_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="夹层厚度">
                {{ selectedApplication.interlayer_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="玻璃层数">
                {{ selectedApplication.glass_layers || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="夹层数">
                {{ selectedApplication.interlayer_layers || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="夹层类型">
                {{ selectedApplication.interlayer_type || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="玻璃处理">
                {{ selectedApplication.glass_treatment || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="涂层类型">
                {{ selectedApplication.coating_type || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="涂层厚度">
                {{ selectedApplication.coating_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="涂层颜色">
                {{ selectedApplication.coating_color || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="材料性质">
                {{ selectedApplication.material_nature || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="安全等级">
                {{ selectedApplication.safety_class || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="玻璃板描述">
                {{ selectedApplication.pane_desc || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">车辆信息</el-divider>
            <div v-if="selectedApplication.vehicles && selectedApplication.vehicles.length > 0">
              <div v-for="(vehicle, index) in selectedApplication.vehicles" :key="index" class="vehicle-info">
                <h4>车辆 {{ index + 1 }}</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="车辆制造商">
                    {{ vehicle.veh_mfr || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="车辆类型">
                    {{ vehicle.veh_type || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="车辆类别">
                    {{ vehicle.veh_cat || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="开发区域">
                    {{ vehicle.dev_area || '未填写' }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
            <div v-else>
              <el-empty description="暂无车辆信息" />
            </div>
            
            <el-divider content-position="left">备注</el-divider>
            <p>{{ selectedApplication.remarks || '暂无备注' }}</p>
            
            <el-divider content-position="left">时间信息</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="创建时间">
                {{ formatDate(selectedApplication.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatDate(selectedApplication.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="提交时间">
                {{ formatDate(selectedApplication.submitted_at) || '未提交' }}
              </el-descriptions-item>
              <el-descriptions-item label="批准时间">
                {{ formatDate(selectedApplication.approved_at) || '未批准' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showDetailDialog = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 编辑对话框（复用 ApplicationEditor） -->
        <el-dialog 
          v-model="showEditor" 
          title="编辑申请书" 
          width="820px"
          :close-on-click-modal="false"
        >
          <ApplicationEditor 
            :session-id="selectedApplication?.application_number || undefined"
            :value="selectedApplication || undefined"
            @saved="onEditorSaved"
            @cancel="showEditor=false"
          />
        </el-dialog>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Delete, Edit, Refresh, Search, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ApplicationEditor from '../components/ApplicationEditor.vue'
import { onMounted, ref } from 'vue'
import { applicationAPI } from '../api/application'

const loading = ref(false)
const applications = ref<any[]>([])
const selectedApplication = ref<any>(null)
const showDetailDialog = ref(false)

// 搜索和过滤
const searchQuery = ref('')
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadApplications = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchQuery.value || undefined
    }
    
    const response = await applicationAPI.getApplications(params)
    if (response.success) {
      applications.value = response.data.applications
      total.value = response.data.pagination?.total || 0
    } else {
      applications.value = []
      total.value = 0
    }
  } catch (error) {
    ElMessage.error('获取申请书列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadApplications()
}

const resetSearch = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  loadApplications()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadApplications()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadApplications()
}

const viewApplication = async (id: number) => {
  try {
    const response = await applicationAPI.getApplication(id)
    if (response.success) {
      selectedApplication.value = response.data
      showDetailDialog.value = true
    } else {
      ElMessage.error('获取申请书详情失败')
    }
  } catch (error) {
    ElMessage.error('获取申请书详情失败')
  }
}

const openEditor = async (row: any) => {
  try {
    const res = await applicationAPI.getApplication(row.id)
    if (res.success) {
      selectedApplication.value = res.data
      showEditor.value = true
    } else {
      ElMessage.error(res.message || '获取申请书详情失败')
    }
  } catch (e) {
    ElMessage.error('获取申请书详情失败')
  }
}

const deleteApplication = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个申请书吗？此操作不可恢复。', '确认删除', {
      type: 'warning'
    })
    const response = await applicationAPI.deleteApplication(id)
    if (response.success) {
      ElMessage.success('申请书删除成功')
      loadApplications()
    } else {
      ElMessage.error(response.message || '删除申请书失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除申请书失败')
    }
  }
}

const handleRowClick = (row: any) => {
  viewApplication(row.id)
}

const getStatusType = (status: string) => {
  const statusMap: { [key: string]: string } = {
    draft: 'info',
    submitted: 'warning',
    processing: 'primary',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: { [key: string]: string } = {
    draft: '草稿',
    submitted: '已提交',
    processing: '处理中',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadApplications()
})

const onEditorSaved = (payload: { session_id: string }) => {
  showEditor.value = false
  ElMessage.success('保存成功')
  loadApplications()
}

// 编辑对话框
const showEditor = ref(false)
</script>

<style scoped>
.application-manager {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.application-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2A3B8F;
}

.application-main {
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.search-section {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.application-list {
  padding: 1.5rem;
}

.application-title {
  font-weight: 500;
  color: #2A3B8F;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.application-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.vehicle-info {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.vehicle-info h4 {
  margin: 0 0 1rem 0;
  color: #2A3B8F;
}
</style> 