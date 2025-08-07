<template>
  <div class="upload-container">
    <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
      <div class="upload-content">
        <div class="upload-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 16L12 8M12 8L15 11M12 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 15V16C3 18.8284 3 20.2426 3.87868 21.1213C4.75736 22 6.17157 22 9 22H15C17.8284 22 19.2426 22 20.1213 21.1213C21 20.2426 21 18.8284 21 16V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="upload-title">拖拽文件到此处</h3>
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
            选择文件
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
          </div>
        </div>
        <el-button 
          type="primary" 
          size="small" 
          @click="onSubmit" 
          :disabled="loading"
          :loading="loading"
          class="extract-btn"
        >
          {{ loading ? '提取中...' : '提取信息' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';
import { ref } from 'vue';
import { extractFields } from '../api';

const emit = defineEmits(['success', 'error']);

const file = ref<File | null>(null);
const fileList = ref<any[]>([]);
const loading = ref(false);
const uploadRef = ref();

function handleChange(fileObj: any) {
  file.value = fileObj.raw;
  fileList.value = [fileObj];
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
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

async function onSubmit() {
  if (!file.value) {
    ElMessage.warning('请先选择文件');
    return;
  }
  
  loading.value = true;
  
  try {
    const formData = new FormData();
    formData.append('file', file.value);
    
    const response = await extractFields(formData);
    
    if (response.data.success) {
      ElMessage.success('提取成功！');
      emit('success', response.data);
    } else {
      ElMessage.error(response.data.error || '提取失败');
      emit('error', response.data.error);
    }
  } catch (error: any) {
    console.error('提取失败:', error);
    const errorMessage = error.response?.data?.error || error.message || '提取失败';
    ElMessage.error(errorMessage);
    emit('error', errorMessage);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.upload-container {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  cursor: pointer;
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
  margin-top: 2rem;
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
}
</style>