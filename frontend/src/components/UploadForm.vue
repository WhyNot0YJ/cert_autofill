<template>
  <div class="upload-container">
    <!-- AI提取说明 -->
    <div class="ai-info">
      <el-alert
        title="AI智能提取"
        description="上传申请书文档，AI将自动提取关键信息并填充到表单中。目前仅支持申请书文件上传，测试报告功能暂未开放。"
        type="info"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
      <div class="upload-content">
        <div class="upload-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 16L12 8M12 8L15 11M12 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 15V16C3 18.8284 3 20.2426 3.87868 21.1213C4.75736 22 6.17157 22 9 22H15C17.8284 22 19.2426 22 20.1213 21.1213C21 20.2426 21 18.8284 21 16V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="upload-title">拖拽申请书文档到此处</h3>
        <p class="upload-subtitle">或点击选择文件</p>
        <p class="upload-formats">支持 .doc, .docx, .pdf 格式</p>
        
        <el-upload
          ref="uploadRef"
          class="hidden-upload"
          action=""
          :auto-upload="false"
          :on-change="handleChange"
          :file-list="fileList"
          accept=".doc,.docx,.pdf"
          :show-file-list="false"
        >
          <el-button type="primary" size="large" class="select-btn">
            选择申请书文件
          </el-button>
        </el-upload>
      </div>
    </div>

    <!-- 文件列表 -->
    <div v-if="fileList.length > 0" class="file-list">
      <div v-for="file in fileList" :key="file.uid" class="file-item">
        <div class="file-info">
          <div class="file-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="file-details">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-size">{{ formatFileSize(file.size) }}</div>
            <div class="file-type">申请书文档</div>
          </div>
        </div>
        <el-button 
          type="primary" 
          size="small" 
          @click="onAIExtract" 
          :disabled="loading"
          :loading="loading"
          class="extract-btn"
        >
          {{ loading ? 'AI提取中...' : 'AI提取信息' }}
        </el-button>
      </div>
    </div>

    <!-- 测试报告上传（已禁用） -->
    <div class="disabled-upload">
      <el-alert
        title="测试报告上传"
        description="测试报告文件上传功能正在开发中，敬请期待..."
        type="warning"
        :closable="false"
        show-icon
      />
      <div class="disabled-upload-area">
        <div class="disabled-content">
          <div class="disabled-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9V13M12 17H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 21 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#909399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h4 class="disabled-title">测试报告上传</h4>
          <p class="disabled-subtitle">功能开发中，暂未开放</p>
        </div>
      </div>
    </div>

    <!-- AI提取结果预览 -->
    <div v-if="extractionResult" class="extraction-result">
      <el-divider content-position="left">
        <span class="result-title">
          <el-icon><Check /></el-icon>
          AI提取结果
        </span>
      </el-divider>
      
      <div class="result-content">
        <el-row :gutter="20">
          <!-- 企业信息 -->
          <el-col :span="12">
            <el-card class="result-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>企业信息</span>
                </div>
              </template>
              <div class="result-item">
                <label>企业名称:</label>
                <span>{{ extractionResult.enterprise_info.name || '未提取到' }}</span>
              </div>
              <div class="result-item">
                <label>英文名称:</label>
                <span>{{ extractionResult.enterprise_info.english_name || '未提取到' }}</span>
              </div>
              <div class="result-item">
                <label>地址:</label>
                <span>{{ extractionResult.enterprise_info.address || '未提取到' }}</span>
              </div>
            </el-card>
          </el-col>
          
          <!-- 认证信息 -->
          <el-col :span="12">
            <el-card class="result-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>认证信息</span>
                </div>
              </template>
              <div class="result-item">
                <label>认证类型:</label>
                <span>{{ extractionResult.certification_info.type || '未提取到' }}</span>
              </div>
              <div class="result-item">
                <label>产品名称:</label>
                <span>{{ extractionResult.certification_info.product_name || '未提取到' }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 技术规格 -->
        <el-card class="result-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>技术规格</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="result-item">
                <label>风窗厚度:</label>
                <span>{{ extractionResult.technical_specs.windscreen_thickness || '未提取到' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <label>夹层厚度:</label>
                <span>{{ extractionResult.technical_specs.interlayer_thickness || '未提取到' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <label>玻璃层数:</label>
                <span>{{ extractionResult.technical_specs.glass_layers || '未提取到' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <label>夹层类型:</label>
                <span>{{ extractionResult.technical_specs.interlayer_type || '未提取到' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <label>玻璃处理:</label>
                <span>{{ extractionResult.technical_specs.glass_treatment || '未提取到' }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-item">
                <label>涂层类型:</label>
                <span>{{ extractionResult.technical_specs.coating_type || '未提取到' }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
        
        <!-- 操作按钮 -->
        <div class="result-actions">
          <el-button type="primary" @click="applyToForm">
            <el-icon><Check /></el-icon>
            应用到表单
          </el-button>
          <el-button @click="clearResult">
            <el-icon><Delete /></el-icon>
            清除结果
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';
import { Check, Delete } from '@element-plus/icons-vue';
import { ref } from 'vue';
import { applicationAPI } from '../api/application';
import type { AIExtractionResult } from '../api/application';

const emit = defineEmits(['success', 'error', 'extraction-complete']);

const file = ref<File | null>(null);
const fileList = ref<any[]>([]);
const loading = ref(false);
const uploadRef = ref();
const extractionResult = ref<AIExtractionResult | null>(null);

function handleChange(fileObj: any) {
  file.value = fileObj.raw;
  fileList.value = [fileObj];
  // 清除之前的提取结果
  extractionResult.value = null;
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    const droppedFile = files[0];
    const fileObj = {
      uid: Date.now(),
      name: droppedFile.name,
      size: droppedFile.size,
      raw: droppedFile
    };
    file.value = droppedFile;
    fileList.value = [fileObj];
    // 清除之前的提取结果
    extractionResult.value = null;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function onAIExtract() {
  if (!file.value) {
    ElMessage.warning('请先选择文件');
    return;
  }
  
  loading.value = true;
  
  try {
    const response = await applicationAPI.extractDocument(file.value);
    
    if (response.data.success) {
      ElMessage.success('AI提取成功！');
      extractionResult.value = response.data.data;
      emit('extraction-complete', response.data.data);
    } else {
      ElMessage.error(response.data.error || 'AI提取失败');
      emit('error', response.data.error);
    }
  } catch (error: any) {
    console.error('AI提取失败:', error);
    const errorMessage = error.response?.data?.error || error.message || 'AI提取失败';
    ElMessage.error(errorMessage);
    emit('error', errorMessage);
  } finally {
    loading.value = false;
  }
}

function applyToForm() {
  if (extractionResult.value) {
    emit('success', extractionResult.value);
    ElMessage.success('提取结果已应用到表单');
  }
}

function clearResult() {
  extractionResult.value = null;
  fileList.value = [];
  file.value = null;
  ElMessage.info('已清除提取结果');
}
</script>

<style scoped>
.upload-container {
  width: 100%;
}

.ai-info {
  margin-bottom: 1.5rem;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 2rem;
}

.upload-area:hover {
  border-color: #2A3B8F;
  background: rgba(42, 59, 143, 0.05);
}

.upload-area.dragover {
  border-color: #2A3B8F;
  background: rgba(42, 59, 143, 0.1);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.upload-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.upload-subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.upload-formats {
  font-size: 0.875rem;
  color: #9ca3af;
  margin: 0;
}

.hidden-upload {
  display: none;
}

.select-btn {
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  border: none;
  border-radius: 12px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(42, 59, 143, 0.3);
  transition: all 0.3s ease;
}

.select-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(42, 59, 143, 0.4);
}

/* 文件列表 */
.file-list {
  margin-bottom: 2rem;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.file-icon {
  color: #2A3B8F;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.file-size {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.file-type {
  font-size: 0.75rem;
  color: #2A3B8F;
  background: rgba(42, 59, 143, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.extract-btn {
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.extract-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(42, 59, 143, 0.3);
}

/* 禁用的测试报告上传 */
.disabled-upload {
  margin-bottom: 2rem;
}

.disabled-upload-area {
  border: 2px dashed #e4e7ed;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  background: rgba(245, 247, 250, 0.8);
  margin-top: 1rem;
}

.disabled-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.disabled-icon {
  color: #909399;
  margin-bottom: 0.5rem;
}

.disabled-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #909399;
  margin: 0;
}

.disabled-subtitle {
  font-size: 0.875rem;
  color: #c0c4cc;
  margin: 0;
}

/* AI提取结果 */
.extraction-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  border: 1px solid rgba(42, 59, 143, 0.1);
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2A3B8F;
  font-weight: 600;
}

.result-content {
  margin-top: 1.5rem;
}

.result-card {
  margin-bottom: 1rem;
}

.card-header {
  font-weight: 600;
  color: #2A3B8F;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item label {
  font-weight: 500;
  color: #606266;
  min-width: 100px;
}

.result-item span {
  color: #303133;
  text-align: right;
  flex: 1;
  margin-left: 1rem;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-area {
    padding: 2rem 1rem;
  }
  
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .extract-btn {
    width: 100%;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .result-item span {
    text-align: left;
    margin-left: 0;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>