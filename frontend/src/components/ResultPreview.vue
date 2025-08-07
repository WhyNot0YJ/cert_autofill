<template>
  <div class="result-preview">
    <div class="success-card">
      <div class="success-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.7088 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.76488 14.1003 1.98232 16.07 2.85999" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M22 4L12 14.01L9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      
      <div class="success-content">
        <h3 class="success-title">证书生成成功！</h3>
        <p class="success-description">您的证书已准备就绪，可以下载使用了</p>
        
        <div class="download-section">
          <a 
            :href="downloadUrl" 
            target="_blank" 
            class="download-btn"
            @click="handleDownload"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            下载证书
          </a>
          
          <div class="download-info">
            <div class="info-item">
              <span class="info-label">文件格式：</span>
              <span class="info-value">Word文档 (.docx)</span>
            </div>
            <div class="info-item">
              <span class="info-label">生成时间：</span>
              <span class="info-value">{{ currentTime }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';

const props = defineProps<{ downloadUrl: string }>();
const currentTime = ref('');

onMounted(() => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
});

function handleDownload() {
  ElMessage.success('开始下载证书文件');
}
</script>

<style scoped>
.result-preview {
  width: 100%;
}

.success-card {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.success-icon {
  color: #10b981;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

.success-content {
  max-width: 400px;
  margin: 0 auto;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 0.5rem 0;
}

.success-description {
  font-size: 1rem;
  color: #6b7280;
  margin: 0 0 2rem 0;
  line-height: 1.5;
}

.download-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.download-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  color: white;
  text-decoration: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 4px 15px rgba(42, 59, 143, 0.3);
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(42, 59, 143, 0.4);
  color: white;
  text-decoration: none;
}

.download-btn:active {
  transform: translateY(0);
}

.download-info {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.info-item:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.info-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 0.875rem;
  color: #1a1a1a;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .success-card {
    padding: 1.5rem;
  }
  
  .success-title {
    font-size: 1.25rem;
  }
  
  .download-btn {
    padding: 0.875rem 1.5rem;
    font-size: 0.875rem;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>