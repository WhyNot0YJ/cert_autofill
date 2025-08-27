<template>
  <div class="trade-names-editor">
    <div class="editor-header">
      <el-text>商标名称 (Trade Names)</el-text>
      <el-button 
        size="small" 
        type="primary" 
        @click="addName"
        :icon="Plus"
      >
        添加
      </el-button>
    </div>
    
    <div v-if="modelValue.length === 0" class="empty-state">
      <el-text type="info">暂无商标名称，点击"添加"按钮添加</el-text>
    </div>
    
    <div v-else class="names-list">
      <div 
        v-for="(name, index) in modelValue" 
        :key="index"
        class="name-item"
      >
        <div class="name-input">
          <el-input
            :model-value="name"
            @input="updateName(index, $event)"
            placeholder="请输入商标名称"
            clearable
          >
            <template #prepend>{{ index + 1 }}</template>
          </el-input>
        </div>
        
        <div class="name-actions">
          <el-button 
            size="small" 
            type="danger" 
            @click="removeName(index)"
            :icon="Delete"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="editor-footer">
      <el-text type="info" size="small">
        支持添加多个商标名称
      </el-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus, Delete } from '@element-plus/icons-vue'

interface Props {
  modelValue: string[]
}

interface Emits {
  (e: 'update:modelValue', value: string[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const addName = () => {
  const newNames = [...props.modelValue, '']
  emit('update:modelValue', newNames)
}

const removeName = (index: number) => {
  const newNames = props.modelValue.filter((_, i) => i !== index)
  emit('update:modelValue', newNames)
}

const updateName = (index: number, value: string) => {
  const newNames = [...props.modelValue]
  newNames[index] = value
  emit('update:modelValue', newNames)
}
</script>

<style scoped>
.trade-names-editor {
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

.names-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.name-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #fafafa;
}

.name-input {
  flex: 1;
}

.name-actions {
  display: flex;
  gap: 8px;
}

.editor-footer {
  margin-top: 12px;
  text-align: center;
}
</style>
