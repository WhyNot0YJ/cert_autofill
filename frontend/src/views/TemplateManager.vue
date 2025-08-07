<template>
  <div class="template-manager">
    <header class="template-header">
      <div class="header-content">
        <h1 class="page-title">模板管理</h1>
      </div>
    </header>

    <main class="template-main">
      <div class="content-wrapper">
        <div class="action-bar">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            创建新模板
          </el-button>
          <el-button @click="refreshTemplates">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
        </div>

        <div class="template-list">
          <el-table :data="templates" v-loading="loading" style="width: 100%">
            <el-table-column prop="name" label="模板名称" width="200">
              <template #default="{ row }">
                <div class="template-name">
                  <el-icon><Document /></el-icon>
                  <span>{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="description" label="描述" width="300">
              <template #default="{ row }">
                <span>{{ row.description || '暂无描述' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="variables" label="变量数量" width="120">
              <template #default="{ row }">
                <el-tag type="info">{{ row.variables ? row.variables.length : 0 }} 个变量</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                <span>{{ formatDate(row.created_at) }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button size="small" @click="downloadTemplate(row.name)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button size="small" type="danger" @click="deleteTemplate(row.name)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-dialog 
          v-model="showCreateDialog" 
          title="创建新模板" 
          width="800px"
        >
          <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
            <el-form-item label="模板名称" prop="template_name">
              <el-input v-model="createForm.template_name" placeholder="请输入模板名称" />
            </el-form-item>
            
            <el-form-item label="模板描述" prop="description">
              <el-input 
                v-model="createForm.description" 
                type="textarea" 
                :rows="3"
                placeholder="请输入模板描述（可选）"
              />
            </el-form-item>
            
            <el-form-item label="选择变量" prop="selected_variables">
              <el-checkbox-group v-model="createForm.selected_variables">
                <el-checkbox 
                  v-for="(label, key) in variables" 
                  :key="key" 
                  :label="key"
                >
                  {{ label }}
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
          
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showCreateDialog = false">取消</el-button>
              <el-button type="primary" @click="createTemplate" :loading="creating">
                创建模板
              </el-button>
            </span>
          </template>
        </el-dialog>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Delete, Document, Download, Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { templateAPI } from '../api/template'

const loading = ref(false)
const creating = ref(false)
const templates = ref<any[]>([])
const variables = ref<{[key: string]: string}>({})
const showCreateDialog = ref(false)

const createFormRef = ref()
const createForm = reactive({
  template_name: '',
  description: '',
  selected_variables: [] as string[]
})

const createRules = {
  template_name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  selected_variables: [
    { type: 'array', min: 1, message: '请至少选择一个变量', trigger: 'change' }
  ]
}

const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await templateAPI.getTemplates()
    if (response.data.success) {
      templates.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const loadVariables = async () => {
  try {
    const response = await templateAPI.getVariables()
    if (response.data.success) {
      variables.value = response.data.data
    }
  } catch (error) {
    ElMessage.error('获取变量列表失败')
  }
}

const refreshTemplates = () => {
  loadTemplates()
}

const createTemplate = async () => {
  try {
    await createFormRef.value.validate()
  } catch (error) {
    return
  }

  creating.value = true
  try {
    const response = await templateAPI.createTemplate({
      template_name: createForm.template_name,
      selected_variables: createForm.selected_variables,
      description: createForm.description
    })
    
    if (response.data.success) {
      ElMessage.success('模板创建成功')
      showCreateDialog.value = false
      createForm.template_name = ''
      createForm.description = ''
      createForm.selected_variables = []
      loadTemplates()
    }
  } catch (error) {
    ElMessage.error('创建模板失败')
  } finally {
    creating.value = false
  }
}

const deleteTemplate = async (templateName: string) => {
  try {
    await ElMessageBox.confirm(`确定要删除模板 "${templateName}" 吗？`, '确认删除')
    const response = await templateAPI.deleteTemplate(templateName)
    if (response.data.success) {
      ElMessage.success('模板删除成功')
      loadTemplates()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除模板失败')
    }
  }
}

const downloadTemplate = async (templateName: string) => {
  try {
    const response = await templateAPI.downloadTemplate(templateName)
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${templateName}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('下载模板失败')
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTemplates()
  loadVariables()
})
</script>

<style scoped>
.template-manager {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.template-header {
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

.template-main {
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.action-bar {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
}

.template-list {
  padding: 1.5rem;
}

.template-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style> 