<template>
  <div class="marks-editor">
    <div class="editor-header">
      <el-text>商标图案 (Trade Marks)</el-text>
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileUpload"
        accept="image/*"
        multiple
      >
        <el-button 
          size="small" 
          type="primary" 
          :icon="Upload"
        >
          上传图片
        </el-button>
      </el-upload>
    </div>
    
    <div v-if="modelValue.length === 0" class="empty-state">
      <el-text type="info">暂无商标图片，点击"上传图片"按钮添加</el-text>
    </div>
    
    <div v-else class="marks-list">
      <div 
        v-for="(mark, index) in modelValue" 
        :key="index"
        class="mark-item"
      >
        <div class="mark-preview">
          <el-image
            v-if="mark"
            :src="getImageUrl(mark)"
            class="preview-image"
            fit="cover"
            :preview-src-list="[getImageUrl(mark)]"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>加载失败</span>
              </div>
            </template>
          </el-image>
          <div v-else class="placeholder">
            <el-icon><Picture /></el-icon>
            <span>无效图片</span>
          </div>
        </div>
        
        <div class="mark-info">
          <div class="mark-number">商标 {{ index + 1 }}</div>
          <div class="mark-filename" :title="getOriginalFilename(mark)">
            {{ getDisplayFilename(mark) }}
          </div>
        </div>
        
        <div class="mark-actions">
          <el-button 
            size="small" 
            type="danger" 
            @click="removeMark(index)"
            :icon="Delete"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="editor-footer">
      <el-text type="info" size="small">
        支持上传JPG、PNG、GIF、WebP、SVG等图片文件，最大5MB
      </el-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { Delete, Picture, Upload } from '@element-plus/icons-vue'
import { uploadAPI } from '@/api/upload'

interface Props {
  modelValue: string[]
}

interface Emits {
  (e: 'update:modelValue', value: string[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const removeMark = (index: number) => {
  const newMarks = props.modelValue.filter((_, i) => i !== index)
  emit('update:modelValue', newMarks)
}

const getImageUrl = (path: string): string => {
  if (!path) return ''
  // 如果是完整URL，直接返回
  if (path.startsWith('http')) return path
  // 否则拼接基础URL
  const baseUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5000'
  return `${baseUrl}${path}`
}

const getOriginalFilename = (path: string): string => {
  if (!path) return ''
  // 从路径中提取文件名
  const parts = path.split('/')
  const filename = parts[parts.length - 1]
  // 尝试从时间戳格式的文件名中提取原始名称
  const match = filename.match(/^\d+_[a-f0-9]+_(.+)$/)
  return match ? match[1] : filename
}

const getDisplayFilename = (path: string): string => {
  const originalName = getOriginalFilename(path)
  // 如果文件名太长，进行截断
  if (originalName.length > 20) {
    const ext = originalName.split('.').pop()
    const name = originalName.substring(0, 15)
    return `${name}...${ext ? '.' + ext : ''}`
  }
  return originalName
}

const handleFileUpload = async (file: any) => {
  if (!file.raw) return
  
  try {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
    if (!allowedTypes.includes(file.raw.type)) {
      ElMessage.error('只支持JPG、PNG、GIF、WebP、SVG格式的图片')
      return
    }
    
    // 验证文件大小 (5MB)
    if (file.raw.size > 5 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过5MB')
      return
    }
    
    // 调用上传API
    const response = await uploadAPI.uploadTradeMarkImage(file.raw)
    
    if (response.success) {
      // 添加到列表
      const newMarks = [...props.modelValue, response.data.url]
      emit('update:modelValue', newMarks)
      
      ElMessage.success('图片上传成功')
    } else {
      ElMessage.error(response.message || '上传失败')
    }
    
  } catch (error: any) {
    console.error('文件上传失败:', error)
    ElMessage.error('文件上传失败: ' + (error.response?.data?.error || error.message || '未知错误'))
  }
}
</script>

<style scoped>
.marks-editor {
  width: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: #fafafa;
}

.marks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mark-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #fafafa;
}

.mark-preview {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mark-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mark-number {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.mark-filename {
  color: #909399;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.placeholder {
  width: 80px;
  height: 80px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  color: #999;
  font-size: 12px;
  gap: 4px;
}

.image-error {
  width: 80px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #999;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 10px;
  gap: 4px;
}

.mark-actions {
  display: flex;
  gap: 8px;
}

.editor-footer {
  margin-top: 12px;
  text-align: center;
}
</style>
