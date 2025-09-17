<template>
  <div class="application-editor">
    <el-form ref="formRef" :model="localForm" :rules="formRules" label-width="240px" class="editor-form">
      <el-divider content-position="left">基础信息 (Basic Information)</el-divider>
      
      <el-form-item label="公司 (Company)" prop="company_id">
        <el-select v-model="localForm.company_id" placeholder="请选择公司" filterable @change="onCompanyChange">
          <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="公司地址 (Company Address)">
        <el-input v-model="localForm.company_address" type="textarea" :rows="2" />
      </el-form-item>

      <el-divider content-position="left">证书参数 (Certificate Parameters)</el-divider>
      <el-form-item label="批准号 (Approval No.)" prop="approval_no">
        <el-input v-model="localForm.approval_no" />
      </el-form-item>
      <el-form-item label="信息文件夹号 (Information Folder No.)" prop="information_folder_no">
        <el-input v-model="localForm.information_folder_no" />
      </el-form-item>
      <el-form-item label="备注 (Remarks)">
        <el-input v-model="localForm.remarks" type="textarea" :rows="2" />
      </el-form-item>

      <el-divider content-position="left">车辆信息 (Vehicle Information)</el-divider>
      <div v-for="(vehicle, index) in localForm.vehicles" :key="index" class="vehicle-block">
        <div class="vehicle-header">
          <h4>车辆 {{ index + 1 }}</h4>
          <el-button type="danger" size="small" @click="removeVehicle(index)" :disabled="localForm.vehicles.length === 1">删除</el-button>
        </div>
        <el-form-item label="车辆制造商 (Vehicle Manufacturer)"><el-input v-model="vehicle.veh_mfr" /></el-form-item>
        <el-form-item label="车辆类型 (Vehicle Type)"><el-input v-model="vehicle.veh_type" /></el-form-item>
        <el-form-item label="车辆类别 (Vehicle Category)"><el-input v-model="vehicle.veh_cat" /></el-form-item>
        <el-form-item label="开发区域 (Development Area)"><el-input v-model="vehicle.dev_area" /></el-form-item>
        <el-form-item label="段高度 (Segment Height)"><el-input v-model="vehicle.seg_height" /></el-form-item>
        <el-form-item label="曲率半径 (Curvature Radius)"><el-input v-model="vehicle.curv_radius" /></el-form-item>
        <el-form-item label="安装角度 (Installation Angle)"><el-input v-model="vehicle.inst_angle" /></el-form-item>
        <el-form-item label="座椅角度 (Seat Angle)"><el-input v-model="vehicle.seat_angle" /></el-form-item>
        <el-form-item label="参考点坐标 (Reference Point Coordinates)"><el-input v-model="vehicle.rpoint_coords" /></el-form-item>
        <el-form-item label="开发描述 (Development Description)"><el-input v-model="vehicle.dev_desc" type="textarea" :rows="2" /></el-form-item>
      </div>
      <el-button type="primary" plain size="small" @click="addVehicle">添加车辆</el-button>

      <el-divider content-position="left">重要日期 (Important Dates)</el-divider>
      <el-form-item label="批准日期 (Approval Date)" prop="approval_date">
        <el-date-picker v-model="localForm.approval_date" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="测试日期 (Test Date)" prop="test_date">
        <el-date-picker v-model="localForm.test_date" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="报告日期 (Report Date)" prop="report_date">
        <el-date-picker v-model="localForm.report_date" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
    </el-form>

    <div class="editor-actions">
      <el-button :loading="saving" @click="emitCancel">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      <el-button type="success" @click="openGenerator">文档生成</el-button>
    </div>

    <el-dialog
      v-model="showGenerator"
      title="文档生成 (Document Generation)"
      width="860px"
      :close-on-click-modal="false"
    >
      <DocumentGenerator :session-id="effectiveSessionId()" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { mvpAPI } from '@/api/mvp'
import { companyAPI, type Company } from '@/api/company'
import DocumentGenerator from './DocumentGenerator.vue'

type EditableForm = Record<string, any>

const props = defineProps<{
  sessionId?: string
  value?: EditableForm
}>()

const emits = defineEmits<{
  (e: 'saved', payload: { session_id: string }): void
  (e: 'cancel'): void
}>()

const formRef = ref()
const saving = ref(false)
const generating = ref(false)
const showGenerator = ref(false)
const companies = ref<Company[]>([])

const localForm = reactive<EditableForm>({
  company_id: null,
  company_name: '',
  company_address: '',
  approval_no: '',
  information_folder_no: '',
  remarks: '',
  approval_date: '',
  test_date: '',
  report_date: '',
  vehicles: [
    { veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', seg_height: '', curv_radius: '', inst_angle: '', seat_angle: '', rpoint_coords: '', dev_desc: '' }
  ]
})

const formRules = {
  company_id: [{ required: true, message: '请选择公司', trigger: 'change' }],
  approval_no: [{ required: true, message: '请输入批准号', trigger: 'blur' }],
  information_folder_no: [{ required: true, message: '请输入信息文件夹号', trigger: 'blur' }],
  approval_date: [{ required: true, message: '请选择批准日期', trigger: 'change' }],
  test_date: [{ required: true, message: '请选择测试日期', trigger: 'change' }],
  report_date: [{ required: true, message: '请选择报告日期', trigger: 'change' }]
}

const formatToYMD = (d: any): string => {
  if (!d) return ''
  if (typeof d === 'string') {
    // 兼容 ISO 字符串
    if (d.includes('T')) return d.split('T')[0]
    return d
  }
  try {
    const dt = new Date(d)
    if (!isNaN(dt.getTime())) return dt.toISOString().split('T')[0]
  } catch {}
  return ''
}

watch(() => props.value, (val) => {
  if (val) {
    const incoming = { ...val }
    // 规范日期为 YYYY-MM-DD（ElDatePicker 期望）
    incoming.approval_date = formatToYMD(incoming.approval_date)
    incoming.test_date = formatToYMD(incoming.test_date)
    incoming.report_date = formatToYMD(incoming.report_date)
    // 直接预填公司名与地址（如果接口已返回）
    if (incoming.company_name) localForm.company_name = incoming.company_name
    if (incoming.company_address) localForm.company_address = incoming.company_address
    Object.assign(localForm, incoming)
  }
}, { immediate: true })

const loadCompanies = async () => {
  try {
    const res = await companyAPI.getAllCompanies()
    if (res.success) companies.value = res.data.companies
  } catch {}
}

const onCompanyChange = (companyId: number) => {
  const c = companies.value.find(x => x.id === companyId)
  if (c) {
    localForm.company_name = c.name
    localForm.company_address = c.address || ''
  }
}

const reconcileCompany = () => {
  // 如果已选择 company_id，则回填名称/地址
  if (localForm.company_id) {
    const c = companies.value.find(x => x.id === localForm.company_id)
    if (c) {
      if (!localForm.company_name) localForm.company_name = c.name
      if (!localForm.company_address) localForm.company_address = c.address || ''
      return
    }
  }
  // 否则根据 company_name 尝试匹配 company_id
  if (!localForm.company_id && localForm.company_name && companies.value.length) {
    const c = companies.value.find(x => x.name === localForm.company_name)
    if (c) {
      localForm.company_id = c.id
      if (!localForm.company_address) localForm.company_address = c.address || ''
    }
  }
}

const handleSave = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    ElMessage.warning('请完善必填信息')
    return
  }
  saving.value = true
  try {
    const payload: any = { form_data: { ...localForm } }
    if (props.sessionId) payload.session_id = props.sessionId
    const res = await mvpAPI.saveFormData(payload)
    if (res.success) {
      const sid = res.data?.session_id || props.sessionId || ''
      emits('saved', { session_id: sid })
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const effectiveSessionId = () => {
  const fromValue = (props.value as any)?.application_number
  return props.sessionId || fromValue || ''
}

const openGenerator = () => {
  const sid = effectiveSessionId()
  if (!sid) {
    ElMessage.warning('请先保存以获取会话ID')
    return
  }
  showGenerator.value = true
}

const emitCancel = () => emits('cancel')

onMounted(() => {
  loadCompanies()
  // 如果已存在公司且名称未填，尝试从公司列表补齐
  setTimeout(() => {
    if (localForm.company_id && !localForm.company_name) {
      const c = companies.value.find(x => x.id === localForm.company_id)
      if (c) {
        localForm.company_name = c.name
        if (!localForm.company_address) localForm.company_address = c.address || ''
      }
    }
    // 若仅有 company_name，也尝试匹配设定 company_id
    reconcileCompany()
  }, 0)
})

watch(companies, () => reconcileCompany())

const addVehicle = () => {
  localForm.vehicles.push({ veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', seg_height: '', curv_radius: '', inst_angle: '', seat_angle: '', rpoint_coords: '', dev_desc: '' })
}

const removeVehicle = (index: number) => {
  localForm.vehicles.splice(index, 1)
}
</script>

<style scoped>
.editor-form {
  max-width: 800px;
}
.editor-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>


