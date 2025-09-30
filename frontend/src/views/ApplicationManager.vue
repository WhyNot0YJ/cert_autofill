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
            <el-col :span="4">
              <el-dropdown @command="handleColumnFilter" trigger="click">
                <el-button>
                  <el-icon><Setting /></el-icon>
                  列筛选
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item 
                      v-for="column in availableColumns" 
                      :key="column.key"
                      :command="column.key"
                    >
                      <el-checkbox 
                        v-model="column.visible" 
                        @change="updateColumnVisibility"
                        @click.stop
                      >
                        {{ column.label }}
                      </el-checkbox>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
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
            :border="true"
            :resizable="true"
            :show-overflow-tooltip="true"
            stripe
          >
            <el-table-column 
              v-if="getColumnVisibility('application_number')"
              prop="application_number" 
              label="申请书编号" 
              min-width="200"
            >
              <template #default="{ row }">
                <el-link type="primary" @click.stop="viewApplication(row.id)">
                  {{ row.application_number }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column 
              v-if="getColumnVisibility('approval_no')"
              prop="approval_no" 
              label="批准号" 
              min-width="260"
            >
              <template #default="{ row }">
                <span>{{ row.approval_no || '未填写' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column 
              v-if="getColumnVisibility('company_name')"
              prop="company_name" 
              label="公司名称" 
              min-width="220"
            >
              <template #default="{ row }">
                <span>{{ row.company_name || '未填写' }}</span>
              </template>
            </el-table-column>
            
            
            
            
            
            <el-table-column 
              v-if="getColumnVisibility('created_at')"
              prop="created_at" 
              label="创建时间" 
              min-width="180"
            >
              <template #default="{ row }">
                <span>{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column 
              v-if="getColumnVisibility('updated_at')"
              prop="updated_at" 
              label="更新时间" 
              min-width="180"
            >
              <template #default="{ row }">
                <span>{{ formatDate(row.updated_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="250" fixed="right">
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
              <el-descriptions-item label="Application Number">
                {{ selectedApplication.application_number }}
              </el-descriptions-item>
              
              
              <el-descriptions-item label="Approval No.">
                {{ selectedApplication.approval_no || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Information Folder No.">
                {{ selectedApplication.information_folder_no || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Company">
                {{ selectedApplication.company_name || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Company Address">
                {{ selectedApplication.company_address || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">Technical parameters</el-divider>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="Nominal thickness of the windscreen">
                {{ selectedApplication.windscreen_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Nominal thickness of interlayer(s)">
                {{ selectedApplication.interlayer_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Number of layers of glass">
                {{ selectedApplication.glass_layers || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Number of layers of interlayer">
                {{ selectedApplication.interlayer_layers || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Nature and type of interlayer(s)">
                {{ selectedApplication.interlayer_type || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Special treatment of glass">
                {{ selectedApplication.glass_treatment || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Nature and type of plastics coating(s)">
                {{ selectedApplication.coating_type || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Nominal thickness of plastic coating(s)">
                {{ selectedApplication.coating_thick || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Colouring of plastic coating(s)">
                {{ selectedApplication.coating_color || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Nature of the material">
                {{ selectedApplication.material_nature || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Class of safety-glass pane">
                {{ selectedApplication.safety_class || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="Description of glass pane">
                {{ selectedApplication.pane_desc || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
            
            <el-divider content-position="left">Vehicle Information</el-divider>
            <div v-if="selectedApplication.vehicles && selectedApplication.vehicles.length > 0">
              <div v-for="(vehicle, index) in selectedApplication.vehicles" :key="index" class="vehicle-info">
                <h4>车辆 {{ index + 1 }}</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="Vehicle Manufacturer">
                    {{ vehicle.veh_mfr || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Type of vehicle">
                    {{ vehicle.veh_type || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Vehicle category">
                    {{ vehicle.veh_cat || '未填写' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Developed area (F)">
                    {{ vehicle.dev_area || '未填写' }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
            <div v-else>
              <el-empty description="暂无车辆信息" />
            </div>
            
            <el-divider content-position="left">Remarks</el-divider>
            <p>{{ selectedApplication.remarks || '暂无备注' }}</p>
            
            <el-divider content-position="left">Time Information</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Created At">
                {{ formatDate(selectedApplication.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Updated At">
                {{ formatDate(selectedApplication.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Submitted At">
                {{ formatDate(selectedApplication.submitted_at) || '未提交' }}
              </el-descriptions-item>
              <el-descriptions-item label="Approved At">
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
import { Delete, Edit, Refresh, Search, View, Setting, ArrowDown } from '@element-plus/icons-vue'
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

// 列筛选
const availableColumns = ref([
  { key: 'application_number', label: '申请书编号', visible: true },
  { key: 'approval_no', label: '批准号', visible: true },
  { key: 'company_name', label: '公司名称', visible: true },
  { key: 'created_at', label: '创建时间', visible: true },
  { key: 'updated_at', label: '更新时间', visible: true }
])

const getColumnVisibility = (columnKey: string) => {
  const column = availableColumns.value.find(col => col.key === columnKey)
  return column ? column.visible : true
}

const handleColumnFilter = (command: string) => {
  // 切换列的可见性
  const column = availableColumns.value.find(col => col.key === command)
  if (column) {
    column.visible = !column.visible
  }
}

const updateColumnVisibility = () => {
  // 当checkbox状态改变时触发
}

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

/* 操作栏样式 */
.el-table .el-table__cell:last-child {
  padding: 8px 12px;
}

.el-table .el-table__cell:last-child .el-button {
  margin-right: 8px;
}

.el-table .el-table__cell:last-child .el-button:last-child {
  margin-right: 0;
}
</style> 