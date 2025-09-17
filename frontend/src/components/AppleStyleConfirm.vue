<template>
  <Teleport to="body">
    <Transition name="confirm-dialog">
      <div v-if="visible" class="confirm-overlay" @click="handleOverlayClick">
        <div class="confirm-dialog" @click.stop>
          <!-- 头部 -->
          <div class="dialog-header">
            <div class="header-icon">🏢</div>
            <h2 class="header-title">{{ title }}</h2>
            <p class="header-subtitle">{{ subtitle }}</p>
          </div>
          
          <!-- 内容区域 -->
          <div class="dialog-content">
            <!-- 公司信息卡片 -->
            <div class="info-card">
              <!-- 公司名称 -->
              <div class="info-item company-name">
                <span class="info-icon">🏢</span>
                <span class="info-text">{{ companyName || '未提供公司名称' }}</span>
              </div>
              
              <!-- 公司地址 -->
              <div class="info-item company-address">
                <span class="info-icon">📍</span>
                <span class="info-text">{{ companyAddress || '未提供地址信息' }}</span>
              </div>
              
              <!-- 额外信息展示区域 -->
              <div v-if="additionalInfo" class="info-item extra-info">
                <div class="extra-info-title">
                  <span class="info-icon">🔍</span>
                  <span>提取的额外信息</span>
                </div>
                <div class="extra-info-content">
                  <div v-if="keyInfo.length > 0" class="key-info-list">
                    <div v-for="info in keyInfo" :key="info" class="key-info-item">
                      • {{ info }}
                    </div>
                  </div>
                  <div v-else class="no-extra-info">
                    暂无额外信息
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 说明文字 -->
            <div class="description">
              <strong>💡 提示：</strong>{{ description }}
            </div>
          </div>
          
          <!-- 按钮区域 -->
          <div class="dialog-actions">
            <button class="action-btn cancel-btn" @click="handleCancel">
              {{ cancelText }}
            </button>
            <button class="action-btn confirm-btn" @click="handleConfirm">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

interface Props {
  visible: boolean
  companyName: string
  companyAddress?: string
  additionalInfo?: any
  title?: string
  subtitle?: string
  description?: string
  confirmText?: string
  cancelText?: string
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '发现新公司',
  subtitle: '从文档中提取到新的公司信息',
  description: '该公司不在现有列表中，您可以将其添加到系统中，以便后续使用。',
  confirmText: '新增公司',
  cancelText: '暂不新增'
})

const emit = defineEmits<Emits>()

// 计算关键信息列表
const keyInfo = computed(() => {
  if (!props.additionalInfo) return []
  
  const info = []
  if (props.additionalInfo.approval_no) info.push(`批准号: ${props.additionalInfo.approval_no}`)
          if (props.additionalInfo.information_folder_no) info.push(`信息文件夹号: ${props.additionalInfo.information_folder_no}`)
  if (props.additionalInfo.safety_class) info.push(`安全等级: ${props.additionalInfo.safety_class}`)
  if (props.additionalInfo.pane_desc) info.push(`窗格描述: ${props.additionalInfo.pane_desc}`)
  
  return info
})

// 处理确认
const handleConfirm = () => {
  emit('confirm')
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}

// 处理遮罩层点击
const handleOverlayClick = (event: Event) => {
  if (event.target === event.currentTarget) {
    emit('cancel')
  }
}

// 键盘事件处理
const handleKeydown = (event: KeyboardEvent) => {
  if (!props.visible) return
  
  if (event.key === 'Escape') {
    emit('cancel')
  } else if (event.key === 'Enter') {
    emit('confirm')
  }
}

// 生命周期钩子
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.confirm-dialog {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

/* 头部样式 */
.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px 24px 20px;
  text-align: center;
  position: relative;
}

.header-icon {
  font-size: 48px;
  margin-bottom: 16px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.header-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.header-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  opacity: 0.9;
  font-weight: 400;
}

/* 内容区域样式 */
.dialog-content {
  padding: 24px;
  background: white;
}

/* 信息卡片样式 */
.info-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.info-item {
  transition: all 0.3s ease;
  cursor: pointer;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-icon {
  margin-right: 12px;
  font-size: 20px;
  margin-top: 2px;
}

.info-text {
  flex: 1;
  line-height: 1.6;
}

/* 公司名称样式 */
.company-name {
  border-left: 4px solid #667eea;
}

.company-name .info-text {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
}

.company-name .info-icon {
  font-size: 24px;
}

/* 公司地址样式 */
.company-address {
  border-left: 4px solid #27ae60;
}

.company-address .info-text {
  font-size: 16px;
  color: #6c757d;
}

/* 额外信息样式 */
.extra-info {
  border-left: 4px solid #f39c12;
  margin-top: 16px;
}

.extra-info-title {
  font-size: 14px;
  font-weight: 600;
  color: #e67e22;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.extra-info-content {
  font-size: 13px;
  color: #7f8c8d;
  line-height: 1.5;
}

.key-info-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.key-info-item {
  color: #7f8c8d;
}

.no-extra-info {
  color: #95a5a6;
  font-style: italic;
}

/* 说明文字样式 */
.description {
  font-size: 14px;
  color: #6c757d;
  line-height: 1.6;
  text-align: center;
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(52, 152, 219, 0.1);
  border-radius: 12px;
  border-left: 4px solid #3498db;
}

/* 按钮区域样式 */
.dialog-actions {
  padding: 20px 24px 24px;
  background: #f8f9fa;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.action-btn {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
  border: none;
  outline: none;
}

/* 取消按钮样式 */
.cancel-btn {
  background: transparent;
  border: 1px solid #dee2e6;
  color: #6c757d;
}

.cancel-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

/* 确认按钮样式 */
.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.confirm-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.confirm-btn:hover::before {
  left: 100%;
}

.confirm-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 过渡动画 */
.confirm-dialog-enter-active,
.confirm-dialog-leave-active {
  transition: all 0.3s ease;
}

.confirm-dialog-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

.confirm-dialog-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .confirm-dialog {
    width: 95%;
    margin: 20px;
  }
  
  .dialog-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>
