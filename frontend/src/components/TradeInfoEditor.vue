<template>
  <div class="trade-info-editor">
    <div class="editor-container">
      <!-- 只读公司数据显示 -->
      <div v-if="readonlyCompanyData" class="readonly-section">
        <div class="readonly-header">
          <el-icon><InfoFilled /></el-icon>
          <span>公司关联信息</span>
        </div>
        <div class="readonly-content">
          <!-- 显示公司的trade_names，用分号分隔 -->
          <div v-if="companyTradeNamesText" class="trade-names-display">
            <span class="label">商标名称：</span>
            <span class="content">{{ companyTradeNamesText }}</span>
          </div>
          <!-- 显示公司的trade_marks图片 -->
          <div v-if="readonlyCompanyData.trade_marks && readonlyCompanyData.trade_marks.length > 0" class="trade-marks-display">
            <span class="label">商标图片：</span>
            <div class="marks-images">
              <el-image
                v-for="(mark, index) in readonlyCompanyData.trade_marks"
                :key="index"
                :src="mark"
                :alt="`商标 ${index + 1}`"
                class="mark-image"
                fit="cover"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </div>
        </div>
      </div>

      <!-- 可编辑区域 -->
      <div class="editable-section">
        <div class="editable-header">
          <el-icon><Edit /></el-icon>
          <span>手动编辑调整</span>
          <el-tooltip content="可以在此处手动调整商标名称和图片，会覆盖公司关联的信息">
            <el-icon class="help-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
        
        <!-- 编辑trade_names -->
        <div class="edit-group">
          <label class="edit-label">商标名称（用分号+空格分隔）：</label>
          <el-input
            v-model="tradeNamesText"
            type="textarea"
            :rows="2"
            placeholder="请输入商标名称，多个名称用分号(; )分隔"
            @input="handleTradeNamesChange"
          />
          <div class="help-text">例如：主要商标; 次要商标; 备用商标</div>
        </div>

        <!-- 编辑trade_marks -->
        <div class="edit-group">
          <label class="edit-label">商标图片：</label>
          <MarksEditor v-model="localTradeMarks" @update:modelValue="handleTradeMarksChange" />
        </div>
      </div>

      <!-- 最终效果预览 -->
      <div v-if="hasAnyData" class="preview-section">
        <div class="preview-header">
          <el-icon><View /></el-icon>
          <span>最终效果预览</span>
        </div>
        <div class="preview-content">
          <TradeNamesMarksDisplay 
            :trade-names="finalTradeNames"
            :trade-marks="finalTradeMarks"
            size="default"
            :max-images="10"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { InfoFilled, Edit, QuestionFilled, View, Picture } from '@element-plus/icons-vue'
import MarksEditor from './MarksEditor.vue'
import TradeNamesMarksDisplay from './TradeNamesMarksDisplay.vue'

interface Props {
  tradeNamesText?: string  // 改为字符串格式（分号分隔）
  tradeMarks?: string[]
  readonlyCompanyData?: {
    trade_names?: string[]
    trade_marks?: string[]
  } | null
}

interface Emits {
  (e: 'update:tradeNamesText', value: string): void  // 改为字符串
  (e: 'update:tradeMarks', value: string[]): void
  (e: 'update', data: { trade_names: string[], trade_marks: string[] }): void
}

const props = withDefaults(defineProps<Props>(), {
  tradeNamesText: '',
  tradeMarks: () => [],
  readonlyCompanyData: null
})

const emit = defineEmits<Emits>()

// 本地编辑状态
const localTradeMarks = ref<string[]>([...props.tradeMarks])
const tradeNamesText = ref(props.tradeNamesText || '')

// 监听props变化
watch(() => props.tradeNamesText, (newValue) => {
  tradeNamesText.value = newValue || ''
}, { immediate: true })

watch(() => props.tradeMarks, (newValue) => {
  localTradeMarks.value = [...newValue]
}, { immediate: true })

// 计算公司商标名称文本
const companyTradeNamesText = computed(() => {
  if (props.readonlyCompanyData?.trade_names && props.readonlyCompanyData.trade_names.length > 0) {
    return props.readonlyCompanyData.trade_names.join('; ') + '; '
  }
  return ''
})

// 计算最终的trade_names（优先使用手动编辑的）
const finalTradeNames = computed(() => {
  if (tradeNamesText.value.trim()) {
    // 手动编辑的数据（按 "; " 分割）
    return tradeNamesText.value.split('; ').map(name => name.trim()).filter(name => name)
  } else if (props.readonlyCompanyData?.trade_names && props.readonlyCompanyData.trade_names.length > 0) {
    // 公司关联的数据
    return props.readonlyCompanyData.trade_names
  }
  return []
})

// 计算最终的trade_marks（优先使用手动编辑的）
const finalTradeMarks = computed(() => {
  if (localTradeMarks.value.length > 0) {
    // 手动编辑的数据
    return localTradeMarks.value
  } else if (props.readonlyCompanyData?.trade_marks && props.readonlyCompanyData.trade_marks.length > 0) {
    // 公司关联的数据
    return props.readonlyCompanyData.trade_marks
  }
  return []
})

// 是否有任何数据需要显示
const hasAnyData = computed(() => {
  return finalTradeNames.value.length > 0 || finalTradeMarks.value.length > 0
})

// 处理商标名称变化
const handleTradeNamesChange = () => {
  emit('update:tradeNamesText', tradeNamesText.value)
  emitUpdate()
}

// 处理商标图片变化
const handleTradeMarksChange = (marks: string[]) => {
  emit('update:tradeMarks', marks)
  emitUpdate()
}

// 发送更新事件（现在只在手动操作时调用，不自动监听）
const emitUpdate = () => {
  emit('update', {
    trade_names: finalTradeNames.value,  // 这里还是数组格式，供内部处理使用
    trade_marks: finalTradeMarks.value
  })
}
</script>

<style scoped>
.trade-info-editor {
  width: 100%;
}

.editor-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.readonly-section,
.editable-section,
.preview-section {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.readonly-header,
.editable-header,
.preview-header {
  background: #f5f7fa;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

.help-icon {
  color: #909399;
  cursor: help;
  margin-left: auto;
}

.readonly-content,
.preview-content {
  padding: 16px;
}

.trade-names-display,
.trade-marks-display {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
}

.trade-names-display:last-child,
.trade-marks-display:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  flex-shrink: 0;
}

.content {
  color: #303133;
  line-height: 1.5;
}

.marks-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mark-image {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #999;
}

.editable-section {
  background: #fafbfc;
}

.edit-group {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.edit-group:last-child {
  border-bottom: none;
}

.edit-label {
  display: block;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.preview-section {
  background: #f0f9ff;
  border-color: #409eff;
}

.preview-header {
  background: #e6f7ff;
  color: #409eff;
  border-bottom-color: #409eff;
}
</style>
