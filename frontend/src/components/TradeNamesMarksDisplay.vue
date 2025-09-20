<template>
  <div class="trade-names-marks-display">
    <!-- 空状态 -->
    <div v-if="isEmpty" class="empty-state">
      <el-text type="info" size="small">暂无商标信息</el-text>
    </div>
    
    <!-- 有内容时的显示 -->
    <div v-else class="content">
      <!-- 商标名称 -->
      <div v-if="tradeNames && tradeNames.length > 0" class="trade-names">
        <el-tag 
          v-for="(name, index) in tradeNames" 
          :key="index" 
          :size="size" 
          type="primary"
          class="trade-name-tag"
        >
          {{ name }}
        </el-tag>
      </div>
      
      <!-- 商标图片 -->
      <div v-if="tradeMarks && tradeMarks.length > 0" class="trade-marks">
        <div 
          v-for="(mark, index) in displayMarks" 
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
              </div>
            </template>
          </el-image>
        </div>
        
        <!-- 显示更多提示 -->
        <div v-if="hasMore" class="more-indicator">
          <el-tag :size="size" type="info">+{{ moreCount }}</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Picture } from '@element-plus/icons-vue'

interface Props {
  tradeNames?: string[]  // 改为字符串数组
  tradeMarks?: string[]
  size?: 'small' | 'default' | 'large'
  maxImages?: number  // 最大显示图片数量
}

const props = withDefaults(defineProps<Props>(), {
  tradeNames: () => [],  // 改为数组默认值
  tradeMarks: () => [],
  size: 'default',
  maxImages: 3
})

const isEmpty = computed(() => {
  return (!props.tradeNames || props.tradeNames.length === 0) && 
         (!props.tradeMarks || props.tradeMarks.length === 0)
})

const sizeClass = computed(() => {
  return `mark-image--${props.size}`
})

const displayMarks = computed(() => {
  if (!props.tradeMarks) return []
  return props.tradeMarks.slice(0, props.maxImages)
})

const hasMore = computed(() => {
  return props.tradeMarks && props.tradeMarks.length > props.maxImages
})

const moreCount = computed(() => {
  if (!props.tradeMarks) return 0
  return props.tradeMarks.length - props.maxImages
})

const handleImageError = (index: number) => {
  console.warn(`商标图片 ${index + 1} 加载失败:`, props.tradeMarks?.[index])
}
</script>

<style scoped>
.trade-names-marks-display {
  width: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  color: #999;
}

.content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.trade-names {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.trade-name-tag {
  margin: 2px 0;
}

.trade-marks {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mark-item {
  display: flex;
  align-items: center;
}

.mark-image {
  border-radius: 4px;
  border: 1px solid #ddd;
}

.mark-image--small {
  width: 24px;
  height: 24px;
}

.mark-image--default {
  width: 32px;
  height: 32px;
}

.mark-image--large {
  width: 48px;
  height: 48px;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
  color: #999;
  font-size: 12px;
}

.more-indicator {
  display: flex;
  align-items: center;
}
</style>
