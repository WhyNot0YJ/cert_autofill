<template>
  <div class="marks-display">
    <div v-if="!marks || marks.length === 0" class="no-marks">
      <el-text type="info">暂无商标图片</el-text>
    </div>
    <div v-else class="marks-grid">
      <div 
        v-for="(mark, index) in marks" 
        :key="index" 
        class="mark-item"
      >
        <el-image
          :src="mark"
          :alt="`商标 ${index + 1}`"
          :class="['mark-image', sizeClass]"
          fit="cover"
          @error="handleImageError(index)"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>加载失败</span>
            </div>
          </template>
        </el-image>
        <div v-if="showLabels" class="mark-label">
          商标 {{ index + 1 }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Picture } from '@element-plus/icons-vue'

interface Props {
  marks?: string[]
  size?: 'small' | 'medium' | 'large'
  showLabels?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  marks: () => [],
  size: 'medium',
  showLabels: false
})

const sizeClass = computed(() => {
  return `mark-image--${props.size}`
})

const handleImageError = (index: number) => {
  console.warn(`商标图片 ${index + 1} 加载失败:`, props.marks?.[index])
}
</script>

<style scoped>
.marks-display {
  width: 100%;
}

.no-marks {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: #fafafa;
}

.marks-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.mark-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.mark-image {
  border-radius: 4px;
  border: 1px solid #ddd;
}

.mark-image--small {
  width: 32px;
  height: 32px;
}

.mark-image--medium {
  width: 64px;
  height: 64px;
}

.mark-image--large {
  width: 128px;
  height: 128px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
  color: #999;
  font-size: 12px;
}

.mark-label {
  font-size: 12px;
  color: #666;
  text-align: center;
}
</style>
