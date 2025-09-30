<template>
  <Teleport to="body">
    <Transition name="confirm-dialog">
      <div v-if="visible" class="confirm-overlay">
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

          <!-- 在弹窗中直接完善公司信息（必填） -->
          <div class="edit-form">
            <div class="form-row">
              <label>公司名称</label>
              <input v-model="form.name" disabled />
            </div>
            <div class="form-row">
              <label>公司地址</label>
              <textarea v-model="form.address" rows="2" placeholder="请输入公司地址"></textarea>
            </div>
            <div class="form-row">
              <label>公司简称</label>
              <input v-model="form.company_contraction" placeholder="请输入公司简称" />
            </div>
            <div class="form-row">
              <label>签名人名称</label>
              <input v-model="form.signature_name" placeholder="请输入签名人名称" />
            </div>
            <div class="form-row">
              <label>公司位置</label>
              <input v-model="form.place" placeholder="请输入公司位置" />
            </div>
            <div class="form-row">
              <label>国家/地区</label>
              <input v-model="form.country" placeholder="请输入国家/地区" />
            </div>
            <div class="form-row">
              <label>联系邮箱</label>
              <input v-model="form.email_address" placeholder="请输入联系邮箱" />
            </div>
            <div class="form-row">
              <label>商标名称</label>
              <textarea v-model="form.trade_names_text" rows="2" placeholder="以分号; 分隔（示例：名称1; 名称2）"></textarea>
            </div>
            <div class="form-row">
              <label>商标图案</label>
              <div class="flex-1">
                <MarksEditor v-model="form.trade_marks" />
              </div>
            </div>
            <div class="form-row">
              <label>公司图片</label>
              <div class="flex-1 upload-wrap">
                <el-upload
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handlePictureChange"
                  accept="image/*"
                >
                  <el-button>选择图片</el-button>
                </el-upload>
                <div v-if="form.picture || previewPicture" class="image-preview">
                  <el-image :src="previewPicture || getImageUrl(form.picture)" class="preview-image" fit="cover" />
                  <el-button size="small" type="danger" @click="clearPicture">删除</el-button>
                </div>
              </div>
            </div>
            <div class="form-row">
              <label>签名图片</label>
              <div class="flex-1 upload-wrap">
                <el-upload
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleSignatureChange"
                  accept="image/*"
                >
                  <el-button>选择签名</el-button>
                </el-upload>
                <div v-if="form.signature || previewSignature" class="image-preview">
                  <el-image :src="previewSignature || getImageUrl(form.signature)" class="preview-image" fit="cover" />
                  <el-button size="small" type="danger" @click="clearSignature">删除</el-button>
                </div>
              </div>
            </div>

            <!-- 设备信息（可选，结构与公司管理一致，支持添加/删除） -->
            <el-divider content-position="left">
              设备信息
              <el-button 
                type="primary" 
                size="small" 
                @click="addEquipment"
                style="margin-left: 10px;"
              >
                添加设备
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                @click="showBatchAddDialog = true"
                style="margin-left: 10px;"
              >
                批量添加
              </el-button>
            </el-divider>

            <div 
              v-for="(equipment, index) in form.equipment" 
              :key="index" 
              class="equipment-info-section"
            >
              <div class="equipment-header">
                <h4>设备信息 {{ index + 1 }}</h4>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeEquipment(index)"
                >
                  删除
                </el-button>
              </div>

              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item :label="`设备编号`">
                    <el-input 
                      v-model="equipment.no" 
                      placeholder="请输入设备编号，如：TST2017223"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item :label="`设备名称`">
                    <el-input 
                      v-model="equipment.name" 
                      placeholder="请输入设备名称"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </div>
          <!-- 批量添加设备对话框 -->
          <el-dialog 
            v-model="showBatchAddDialog" 
            title="批量添加设备" 
            width="600px"
            append-to-body
            :z-index="10001"
          >
            <div class="batch-add-container">
              <el-alert
                title="使用说明"
                type="info"
                :closable="false"
                style="margin-bottom: 20px;"
              >
                <template #default>
                  <p>请按照以下格式输入设备信息，每行一个设备：</p>
                  <p><strong>格式：</strong> no. 设备编号: 设备名称 或 no. 设备编号：设备名称</p>
                  <p><strong>示例：</strong> no. FYGZT09007: High and low temperature damp heat test chamber</p>
                  <p><strong>支持：</strong> 半角冒号(:) 和 全角冒号(：)</p>
                </template>
              </el-alert>

              <el-form-item label="设备信息">
                <el-input
                  v-model="batchEquipmentText"
                  type="textarea"
                  :rows="10"
                  placeholder="请输入设备信息，每行一个设备，格式：no. 设备编号: 设备名称 或 no. 设备编号：设备名称"
                  style="width: 100%;"
                />
              </el-form-item>

              <div v-if="parsedEquipment.length > 0" class="parsed-equipment">
                <h4>解析结果预览：</h4>
                <div class="equipment-preview">
                  <div 
                    v-for="(equipment, index) in parsedEquipment" 
                    :key="index" 
                    class="equipment-preview-item"
                  >
                    <el-tag type="success" size="small">{{ equipment.no }}</el-tag>
                    <span>{{ equipment.name }}</span>
                  </div>
                </div>
              </div>
            </div>

            <template #footer>
              <el-button @click="showBatchAddDialog = false">取消</el-button>
              <el-button type="primary" @click="handleBatchAdd" :disabled="parsedEquipment.length === 0">
                确认添加 {{ parsedEquipment.length }} 个设备
              </el-button>
            </template>
          </el-dialog>
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
import { computed, onMounted, onUnmounted, reactive, watch, ref } from 'vue'
import MarksEditor from './MarksEditor.vue'
import { getServerBaseURL } from '../api'
import { uploadAPI } from '../api/upload'

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
  (e: 'confirm', payload: {
    name: string
    company_contraction: string
    address: string
    signature_name: string
    place: string
    email_address: string
  country?: string
    trade_names: string[]
    trade_marks?: string[]
    signature?: string
    picture?: string
    equipment?: Array<{ no: string; name: string }>
  }): void
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

// 可编辑表单（在当前弹窗中完善公司信息）
const form = reactive({
  name: '',
  company_contraction: '',
  address: '',
  signature_name: '',
  place: '',
  email_address: '',
  country: '',
  trade_names_text: '',
  trade_marks: [] as string[],
  picture: '',
  signature: ''
})

// 设备信息（可为空）
const formAny: any = form
if (!Array.isArray(formAny.equipment)) {
  formAny.equipment = []
}

const addEquipment = () => {
  if (!Array.isArray(formAny.equipment)) formAny.equipment = []
  formAny.equipment.push({ no: '', name: '' })
}

const removeEquipment = (index: number) => {
  if (Array.isArray(formAny.equipment) && index >= 0 && index < formAny.equipment.length) {
    formAny.equipment.splice(index, 1)
  }
}

// 批量添加设备
const showBatchAddDialog = ref(false)
const batchEquipmentText = ref<string>('')
const parsedEquipment = ref<Array<{ no: string; name: string }>>([])

const parseEquipmentText = (text: string): Array<{ no: string; name: string }> => {
  const lines = text.split('\n').filter(line => line.trim())
  const result: Array<{ no: string; name: string }> = []
  for (const line of lines) {
    const match = line.match(/no\.\s*([^:：]+)[:：]\s*(.+)/i)
    if (match) {
      const no = match[1].trim()
      const name = match[2].trim()
      if (no && name) result.push({ no, name })
    }
  }
  return result
}

watch(batchEquipmentText, (newText) => {
  if (newText && newText.trim()) parsedEquipment.value = parseEquipmentText(newText)
  else parsedEquipment.value = []
})

const handleBatchAdd = () => {
  if (!Array.isArray(formAny.equipment)) formAny.equipment = []
  if (parsedEquipment.value.length > 0) {
    formAny.equipment.push(...parsedEquipment.value)
  }
  showBatchAddDialog.value = false
  batchEquipmentText.value = ''
  parsedEquipment.value = []
}

// 预览/工具
const previewPicture = ref<string>('')
const previewSignature = ref<string>('')

const getImageUrl = (path?: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = getServerBaseURL()
  return path.startsWith('/') ? `${base}${path}` : `${base}/${path}`
}

const handlePictureChange = async (file: any) => {
  try {
    const res = await uploadAPI.uploadCompanyPicture(file.raw)
    if (res.success) {
      form.picture = res.data.url
      previewPicture.value = res.data.url
    } else {
      alert(res.message || '公司图片上传失败')
    }
  } catch (e: any) {
    alert(e?.message || '公司图片上传失败')
  }
}

const handleSignatureChange = async (file: any) => {
  try {
    const res = await uploadAPI.uploadCompanySignature(file.raw)
    if (res.success) {
      form.signature = res.data.url
      previewSignature.value = res.data.url
    } else {
      alert(res.message || '签名图片上传失败')
    }
  } catch (e: any) {
    alert(e?.message || '签名图片上传失败')
  }
}

const clearPicture = () => {
  form.picture = ''
  previewPicture.value = ''
}

const clearSignature = () => {
  form.signature = ''
  previewSignature.value = ''
}

// 初始填充：名称、地址来源于 props
watch(
  () => [props.companyName, props.companyAddress, props.additionalInfo],
  () => {
    form.name = props.companyName || ''
    form.address = props.companyAddress || ''
    try {
      const info = props.additionalInfo || {}
      if (Array.isArray(info.trade_names)) {
        form.trade_names_text = info.trade_names.join('; ')
      }
      // 其余字段留空，由用户补齐
    } catch {}
  },
  { immediate: true }
)

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

// 基础校验
const isEmail = (val: string) => /.+@.+\..+/.test(val)

// 处理确认：在当前弹窗中直接回传完善后的必填信息
const handleConfirm = () => {
  if (!form.name || !form.address || !form.company_contraction || !form.signature_name || !form.place || !form.email_address) {
    alert('请完善公司名称、地址、简称、签名人名称、公司位置、国家/地区、联系邮箱等必填信息')
    return
  }
  if (!isEmail(form.email_address)) {
    alert('联系邮箱格式不正确')
    return
  }
  const tradeNames = form.trade_names_text
    ? form.trade_names_text.split(';').map(s => s.trim()).filter(Boolean)
    : []
  const tradeMarks = Array.isArray(form.trade_marks) ? form.trade_marks : []
  emit('confirm', {
    name: form.name,
    company_contraction: form.company_contraction,
    address: form.address,
    signature_name: form.signature_name,
    place: form.place,
    country: form.country || '',
    email_address: form.email_address,
    trade_names: tradeNames,
    trade_marks: tradeMarks,
    equipment: Array.isArray(formAny.equipment) ? formAny.equipment : [],
    signature: form.signature || undefined,
    picture: form.picture || undefined
  })
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
  max-height: 90vh;
  display: flex;
  flex-direction: column;
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
  overflow: auto;
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

/* 简易内嵌表单样式 */
.edit-form {
  margin-top: 12px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 12px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.form-row label {
  width: 96px;
  color: #333;
  font-weight: 600;
}

.form-row input,
.form-row textarea {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
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
