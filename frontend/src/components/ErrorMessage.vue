<template>
  <div class="error-container">
    <div class="error-card">
      <div class="error-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="error-content">
        <h4 class="error-title">操作失败</h4>
        <p class="error-message">{{ message }}</p>
      </div>
      <button class="error-close" @click="$emit('close')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

defineProps<{ message: string }>();
defineEmits(['close']);
</script>

<style scoped>
.error-container {
  width: 100%;
  margin-top: 1rem;
}

.error-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  backdrop-filter: blur(10px);
}

.error-icon {
  color: #ef4444;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #dc2626;
  margin: 0 0 0.25rem 0;
}

.error-message {
  font-size: 0.875rem;
  color: #7f1d1d;
  margin: 0;
  line-height: 1.4;
}

.error-close {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.error-close:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-card {
    padding: 1rem;
    gap: 0.75rem;
  }
  
  .error-content {
    min-width: 0;
  }
  
  .error-message {
    word-break: break-word;
  }
}
</style>