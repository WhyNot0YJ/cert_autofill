<template>
  <div class="document-generator">
    <el-alert
      v-if="!sessionId"
      title="请先保存申请书以获取会话编号后再生成文档"
      type="warning"
      show-icon
      :closable="false"
      class="mb-12"
    />

    <div v-else>
      <el-descriptions :column="1" border class="mb-12">
        <el-descriptions-item label="会话编号 (Session ID)">{{ sessionId }}</el-descriptions-item>
      </el-descriptions>

      <el-form label-width="240px" class="gen-form">
        <el-form-item label="输出格式 (Output Format)">
          <el-select v-model="outputFormat" style="width: 220px">
            <el-option label="DOCX" value="docx" />
            <el-option label="PDF" value="pdf" />
            <el-option label="DOCX + PDF" value="both" />
          </el-select>
        </el-form-item>

        <el-form-item label="生成全部文档 (Generate All)">
          <el-button type="primary" :loading="generatingAll" @click="generateAll">生成</el-button>
        </el-form-item>

        <el-divider content-position="left">分项生成 (Generate Individually)</el-divider>
        <div class="grid">
          <el-button :loading="loading.cert" @click="generate('cert')">生成 CERT</el-button>
          <el-button :loading="loading.if" @click="generate('if')">生成 IF</el-button>
          <el-button :loading="loading.tr" @click="generate('tr')">生成 TR</el-button>
          <el-button :loading="loading.tm" @click="generate('tm')">生成 TM</el-button>
          <el-button :loading="loading.other" @click="generate('other')">生成 OTHER</el-button>
          <el-button :loading="loading.rcs" @click="generate('rcs')">生成 Review Control Sheet</el-button>
        </div>
      </el-form>

      <el-divider content-position="left">进度 (Progress)</el-divider>
      <el-progress :percentage="progress" />

      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { mvpAPI } from '@/api/mvp'
import { getServerBaseURL } from '@/api'

const props = defineProps<{ sessionId: string }>()

const outputFormat = ref<'docx' | 'pdf' | 'both'>('docx')
const generatingAll = ref(false)
const progress = ref(0)
const simulateTimer = ref<number | undefined>(undefined)

const loading = ref({
  cert: false,
  if: false,
  tr: false,
  tm: false,
  other: false,
  rcs: false,
  project: false,
})

const stopSimulate = () => {
  if (simulateTimer.value) {
    clearInterval(simulateTimer.value)
    simulateTimer.value = undefined
  }
}

const startSimulate = () => {
  stopSimulate()
  progress.value = 0
  // 模拟进度：前80%匀速，后20%缓慢
  simulateTimer.value = window.setInterval(() => {
    if (progress.value < 80) progress.value += 5
    else if (progress.value < 95) progress.value += 1
    else stopSimulate()
  }, 300)
}

const triggerDownload = async (filename?: string) => {
  const name = filename
  if (!name) return
  try {
    const blob = await mvpAPI.downloadDocument(name)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('自动下载失败，请手动输入文件名下载')
  }
}

const downloadZipFile = async (filename: string, downloadUrl: string) => {
  try {
    const fullUrl = `${getServerBaseURL()}${downloadUrl}`
    const response = await fetch(fullUrl)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      console.log(`✅ ZIP文件下载成功: ${filename}`)
    } else {
      console.error(`❌ ZIP文件下载失败: ${filename}`, response.status)
    }
  } catch (error) {
    console.error(`❌ ZIP文件下载错误: ${filename}`, error)
  }
}

const generateAll = async () => {
  if (!props.sessionId) return
  generatingAll.value = true
  startSimulate()
  try {
    let res: any
    
    if (outputFormat.value === 'both') {
      // 双格式生成：同时调用Word和PDF接口
      const [wordRes, pdfRes] = await Promise.all([
        mvpAPI.generateDocuments({ session_id: props.sessionId, output_format: 'docx' }),
        mvpAPI.generateDocuments({ session_id: props.sessionId, output_format: 'pdf' })
      ])
      
      // 合并结果
      if (wordRes.success && pdfRes.success) {
        res = {
          success: true,
          message: `成功生成Word和PDF文档，共 ${(wordRes.data?.total_success || 0) + (pdfRes.data?.total_success || 0)} 个文档`,
          data: {
            word_zip: {
              filename: wordRes.data?.filename,
              download_url: wordRes.data?.download_url
            },
            pdf_zip: {
              filename: pdfRes.data?.filename,
              download_url: pdfRes.data?.download_url
            }
          }
        }
      } else {
        res = {
          success: false,
          message: '部分文档生成失败',
          data: {
            word_zip: wordRes.success ? {
              filename: wordRes.data?.filename,
              download_url: wordRes.data?.download_url
            } : null,
            pdf_zip: pdfRes.success ? {
              filename: pdfRes.data?.filename,
              download_url: pdfRes.data?.download_url
            } : null
          }
        }
      }
    } else {
      // 单格式生成
      res = await mvpAPI.generateDocuments({ session_id: props.sessionId, output_format: outputFormat.value })
    }
    
    if (res.success) {
      progress.value = 100
      ElMessage.success('生成完成，开始下载')
      
      // 处理下载
      if (outputFormat.value === 'both') {
        // 双格式：下载两个ZIP文件
        if (res.data.word_zip?.download_url) {
          await downloadZipFile(res.data.word_zip.filename, res.data.word_zip.download_url)
        }
        if (res.data.pdf_zip?.download_url) {
          await downloadZipFile(res.data.pdf_zip.filename, res.data.pdf_zip.download_url)
        }
      } else {
        // 单格式：下载单个ZIP文件
        if (res.data.filename && res.data.download_url) {
          await downloadZipFile(res.data.filename, res.data.download_url)
        }
      }
    } else {
      ElMessage.error(res.message || '生成失败')
    }
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    generatingAll.value = false
  }
}

const generate = async (type: 'cert' | 'if' | 'tr' | 'tm' | 'other' | 'rcs') => {
  if (!props.sessionId) return
  loading.value[type] = true
  startSimulate()
  try {
    let res: any
    const payload = { session_id: props.sessionId, output_format: outputFormat.value }
    if (type === 'cert') res = await mvpAPI.generateCert(payload)
    else if (type === 'if') res = await mvpAPI.generateIF(payload)
    else if (type === 'tr') res = await mvpAPI.generateTR(payload)
    else if (type === 'tm') res = await mvpAPI.generateTM(payload)
    else if (type === 'other') res = await mvpAPI.generateOther(payload)
    else if (type === 'rcs') res = await mvpAPI.generateReviewControlSheet(payload)
    if (res?.success) {
      progress.value = 100
      ElMessage.success('生成完成，开始下载')
      const fname = (res.data && (res.data.filename || (res.data.download_url && res.data.download_url.split('/').pop()))) || undefined
      await triggerDownload(fname)
    } else {
      ElMessage.error(res?.message || '生成失败')
    }
  } catch (e) {
    ElMessage.error('生成失败')
  } finally {
    loading.value[type] = false
  }
}

// 手动下载区域已移除，保留自动下载逻辑
</script>

<style scoped>
.gen-form {
  max-width: 800px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.mb-12 { margin-bottom: 12px; }
</style>
