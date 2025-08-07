<template>
  <div class="mvp-container">
    <!-- 页面标题和测试模式 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">智能文档处理系统</h1>
        
        <!-- 测试模式切换 -->
        <div class="test-mode-section">
          <el-switch
            v-model="testMode"
            active-text="测试模式"
            inactive-text="正常模式"
            @change="handleTestModeChange"
          />
          <div v-if="testMode" class="test-controls">
            <el-button 
              v-for="(step, index) in steps" 
              :key="index"
              size="small"
              :type="currentStep === index ? 'primary' : 'default'"
              @click="goToStep(index)"
            >
              跳转到{{ step.label }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <main class="mvp-main">
      <div class="content-wrapper">
        <!-- 步骤导航 -->
        <div class="step-navigation">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="step-item"
            :class="{ 
              'active': currentStep === index,
              'completed': currentStep > index,
              'disabled': !testMode && currentStep < index
            }"
            @click="goToStep(index)"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-label">{{ step.label }}</div>
          </div>
        </div>

        <!-- 步骤内容 -->
        <div class="step-content">
          <!-- 步骤1: 文件上传 -->
          <div v-if="currentStep === 0" class="step-panel">
            <div class="panel-header">
              <h2>上传文档</h2>
              <p>请上传申请书和检测报告文件</p>
            </div>
            
            <div class="upload-section">
              <div class="upload-card">
                <h3>申请书文件</h3>
                <el-upload
                  ref="applicationUpload"
                  :auto-upload="false"
                  :on-change="handleApplicationChange"
                  :file-list="applicationFiles"
                  accept=".pdf,.doc,.docx"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    将申请书文件拖到此处，或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、DOC、DOCX 格式文件
                    </div>
                  </template>
                </el-upload>
              </div>

              <div class="upload-card">
                <h3>检测报告文件</h3>
                <el-upload
                  ref="reportUpload"
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :file-list="reportFiles"
                  accept=".pdf,.doc,.docx"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    将检测报告文件拖到此处，或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、DOC、DOCX 格式文件
                    </div>
                  </template>
                </el-upload>
              </div>
            </div>

            <div class="step-actions">
              <el-button 
                type="primary" 
                size="large"
                :loading="uploading"
                :disabled="!canProceedToNext"
                @click="uploadDocuments"
              >
                上传文件并继续
              </el-button>
            </div>
          </div>

          <!-- 步骤2: 信息提取 -->
          <div v-if="currentStep === 1" class="step-panel">
            <div class="panel-header">
              <h2>AI信息提取</h2>
              <p>正在使用AI从文档中提取关键信息...</p>
            </div>
            
            <div class="extraction-section">
              <div v-if="extracting" class="extraction-loading">
                <el-progress type="circle" :percentage="extractionProgress" />
                <p>正在分析文档内容，请稍候...</p>
              </div>
              
              <div v-else-if="extractionResult" class="extraction-result">
                <h3>提取结果预览</h3>
                <div class="result-preview">
                  <pre>{{ JSON.stringify(extractionResult, null, 2) }}</pre>
                </div>
              </div>
            </div>

            <div class="step-actions">
              <el-button @click="currentStep = 0">上一步</el-button>
              <el-button 
                type="primary" 
                :disabled="!extractionResult"
                @click="currentStep = 2"
              >
                继续编辑
              </el-button>
            </div>
          </div>

          <!-- 步骤3: 表单编辑 -->
          <div v-if="currentStep === 2" class="step-panel">
            <div class="panel-header">
              <div class="header-content">
                <div class="header-left">
                  <h2>信息确认与编辑</h2>
                  <p>请确认并完善提取的信息</p>
                </div>
                <div class="header-right" v-if="testMode">
                  <el-button 
                    type="primary" 
                    @click="generateTestData"
                  >
                    <el-icon><Plus /></el-icon>
                    一键生成测试数据
                  </el-button>
                </div>
              </div>
            </div>
            
            <div class="form-section">
              <el-form 
                ref="formRef"
                :model="formData"
                :rules="formRules"
                label-width="140px"
                class="certification-form"
              >
                <!-- 基础信息 -->
                <el-divider content-position="left">基础信息</el-divider>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="批准号" prop="approval_no">
                      <el-input v-model="formData.approval_no" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="信息文件夹号" prop="information_folder_no">
                      <el-input v-model="formData.information_folder_no" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="安全等级" prop="safety_class">
                      <el-input v-model="formData.safety_class" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="玻璃板描述" prop="pane_desc">
                      <el-input v-model="formData.pane_desc" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="玻璃层数" prop="glass_layers">
                      <el-input v-model="formData.glass_layers" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="夹层数" prop="interlayer_layers">
                      <el-input v-model="formData.interlayer_layers" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="风窗厚度" prop="windscreen_thick">
                      <el-input v-model="formData.windscreen_thick" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="夹层厚度" prop="interlayer_thick">
                      <el-input v-model="formData.interlayer_thick" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="玻璃处理" prop="glass_treatment">
                      <el-input v-model="formData.glass_treatment" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="夹层类型" prop="interlayer_type">
                      <el-input v-model="formData.interlayer_type" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="涂层类型" prop="coating_type">
                      <el-input v-model="formData.coating_type" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="涂层厚度" prop="coating_thick">
                      <el-input v-model="formData.coating_thick" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="材料性质" prop="material_nature">
                      <el-input v-model="formData.material_nature" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="涂层颜色" prop="coating_color">
                      <el-input v-model="formData.coating_color" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item label="备注" prop="remarks">
                  <el-input 
                    v-model="formData.remarks" 
                    type="textarea" 
                    :rows="2"
                  />
                </el-form-item>

                <!-- 车辆信息 -->
                <el-divider content-position="left">
                  车辆信息
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="addVehicleInfo"
                    style="margin-left: 10px;"
                  >
                    <el-icon><Plus /></el-icon>
                    添加车辆信息
                  </el-button>
                </el-divider>
                
                <!-- 车辆信息列表 -->
                <div v-for="(vehicle, index) in formData.vehicles" :key="index" class="vehicle-info-section">
                  <div class="vehicle-header">
                    <h4>车辆信息 {{ index + 1 }}</h4>
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="removeVehicleInfo(index)"
                      :disabled="formData.vehicles.length === 1"
                    >
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                  
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`车辆制造商`" :prop="`vehicles.${index}.veh_mfr`">
                        <el-input v-model="vehicle.veh_mfr" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`车辆类型`" :prop="`vehicles.${index}.veh_type`">
                        <el-input v-model="vehicle.veh_type" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`车辆类别`" :prop="`vehicles.${index}.veh_cat`">
                        <el-input v-model="vehicle.veh_cat" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`开发区域`" :prop="`vehicles.${index}.dev_area`">
                        <el-input v-model="vehicle.dev_area" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`段高度`" :prop="`vehicles.${index}.seg_height`">
                        <el-input v-model="vehicle.seg_height" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`曲率半径`" :prop="`vehicles.${index}.curv_radius`">
                        <el-input v-model="vehicle.curv_radius" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`安装角度`" :prop="`vehicles.${index}.inst_angle`">
                        <el-input v-model="vehicle.inst_angle" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`座椅角度`" :prop="`vehicles.${index}.seat_angle`">
                        <el-input v-model="vehicle.seat_angle" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`参考点坐标`" :prop="`vehicles.${index}.rpoint_coords`">
                        <el-input v-model="vehicle.rpoint_coords" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`开发描述`" :prop="`vehicles.${index}.dev_desc`">
                        <el-input v-model="vehicle.dev_desc" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </el-form>
            </div>

            <div class="step-actions">
              <el-button @click="currentStep = 1">上一步</el-button>
              <el-button 
                type="primary" 
                @click="saveFormData"
                :loading="saving"
              >
                保存并继续
              </el-button>
            </div>
          </div>

          <!-- 步骤4: 文档生成 -->
          <div v-if="currentStep === 3" class="step-panel">
            <div class="panel-header">
              <h2>生成交付文档</h2>
              <p>根据填写的信息生成最终文档</p>
            </div>
            
            <div class="generation-section">
              <!-- 文档格式选择 -->
              <div v-if="!generating" class="format-selection">
                <h3>选择输出格式</h3>
                <div v-if="generationResult" class="format-tip">
                  <el-alert
                    title="提示"
                    type="info"
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      您已经生成了{{ generationResult.filename.endsWith('.pdf') ? 'PDF' : 'Word' }}文档，可以继续选择其他格式生成。
                    </template>
                  </el-alert>
                </div>
                <el-radio-group v-model="selectedFormat" class="format-options">
                  <el-radio label="docx">
                    <el-icon><Document /></el-icon>
                    Word文档 (.docx)
                  </el-radio>
                  <el-radio label="pdf">
                    <el-icon><Document /></el-icon>
                    PDF文档 (.pdf)
                  </el-radio>
                </el-radio-group>
                
                <div class="format-description">
                  <p v-if="selectedFormat === 'docx'">
                    <strong>Word文档格式:</strong> 可编辑的Word文档，便于后续修改和编辑。
                  </p>
                  <p v-else-if="selectedFormat === 'pdf'">
                    <strong>PDF格式:</strong> 不可编辑的PDF文档，适合正式交付和打印。
                  </p>
                </div>
                
                <div class="generate-actions">
                  <el-button 
                    type="primary" 
                    size="large"
                    @click="generateDocuments"
                    :loading="generating"
                  >
                    <el-icon><Download /></el-icon>
                    生成{{ selectedFormat === 'pdf' ? 'PDF' : 'Word' }}文档
                  </el-button>
                </div>
              </div>
              
              <div v-if="generating" class="generation-loading">
                <el-progress type="circle" :percentage="generationProgress" />
                <p>正在生成{{ selectedFormat === 'pdf' ? 'PDF' : 'Word' }}文档，请稍候...</p>
              </div>
              
              <div v-if="generationResult" class="generation-result">
                <h3>文档生成成功</h3>
                <div class="result-info">
                  <p><strong>文件名:</strong> {{ generationResult.filename }}</p>
                  <p><strong>格式:</strong> {{ generationResult.filename.endsWith('.pdf') ? 'PDF' : 'Word' }}</p>
                  <p><strong>生成时间:</strong> {{ new Date().toLocaleString() }}</p>
                </div>
                <div class="download-section">
                  <el-button 
                    type="primary" 
                    size="large"
                    @click="downloadDocument"
                  >
                    <el-icon><download /></el-icon>
                    下载{{ selectedFormat === 'pdf' ? 'PDF' : 'Word' }}文档
                  </el-button>
                </div>
              </div>
              
              <!-- 已生成文档列表 -->
              <div v-if="generatedDocuments.length > 1" class="generated-documents">
                <h3>已生成的文档</h3>
                <div class="documents-list">
                  <div 
                    v-for="(doc, index) in generatedDocuments" 
                    :key="index"
                    class="document-item"
                  >
                    <div class="document-info">
                      <span class="document-name">{{ doc.filename }}</span>
                      <span class="document-format">{{ doc.format }}</span>
                      <span class="document-time">{{ doc.generatedTime }}</span>
                    </div>
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="downloadSpecificDocument(doc)"
                    >
                      <el-icon><download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div class="step-actions">
              <el-button @click="currentStep = 2">上一步</el-button>
              <el-button 
                type="primary" 
                :disabled="!generationResult"
                @click="finishProcess"
              >
                完成
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Delete, Document, Download, Plus, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, reactive, ref } from 'vue'
import { mvpAPI } from '../api/mvp'

// 步骤定义
const steps = [
  { label: '上传文档' },
  { label: '信息提取' },
  { label: '信息编辑' },
  { label: '生成文档' }
]

// 响应式数据
const currentStep = ref(0)
const sessionId = ref('')
const testMode = ref(false)

// 文件上传相关
const applicationFiles = ref<any[]>([])
const reportFiles = ref<any[]>([])
const uploading = ref(false)

// 信息提取相关
const extracting = ref(false)
const extractionProgress = ref(0)
const extractionResult = ref<any>(null)

// 表单相关
const formRef = ref()
const saving = ref(false)
const formData = reactive<{[key: string]: any}>({
  // 基础信息
  title: '',
  
  // IF_Template_2.docx 变量
  approval_no: '',                    // 批准号
  information_folder_no: '',          // 信息文件夹号
  safety_class: '',                   // 安全等级
  pane_desc: '',                      // 玻璃板描述
  glass_layers: '',                   // 玻璃层数
  interlayer_layers: '',              // 夹层数
  windscreen_thick: '',               // 风窗厚度
  interlayer_thick: '',               // 夹层厚度
  glass_treatment: '',                // 玻璃处理
  interlayer_type: '',                // 夹层类型
  coating_type: '',                   // 涂层类型
  coating_thick: '',                  // 涂层厚度
  material_nature: '',                // 材料性质
  coating_color: '',                  // 涂层颜色
  remarks: '',                        // 备注
  
  // 车辆信息 (用于多个车辆信息)
  vehicles: [
    {
      veh_mfr: '',                      // 车辆制造商
      veh_type: '',                     // 车辆类型
      veh_cat: '',                      // 车辆类别
      dev_area: '',                     // 开发区域
      seg_height: '',                   // 段高度
      curv_radius: '',                  // 曲率半径
      inst_angle: '',                   // 安装角度
      seat_angle: '',                   // 座椅角度
      rpoint_coords: '',                // 参考点坐标
      dev_desc: ''                      // 开发描述
    }
  ]
})

// 生成测试session_id的函数
const generateTestSessionId = () => {
  if (!sessionId.value && testMode.value) {
    sessionId.value = `test_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    console.log('生成测试session_id:', sessionId.value)
  }
  return sessionId.value
}

// 表单验证规则
const formRules = {
  approval_no: [
    { required: true, message: '请输入批准号', trigger: 'blur' }
  ],
  information_folder_no: [
    { required: true, message: '请输入信息文件夹号', trigger: 'blur' }
  ],
  safety_class: [
    { required: true, message: '请输入安全等级', trigger: 'blur' }
  ],
  pane_desc: [
    { required: true, message: '请输入玻璃板描述', trigger: 'blur' }
  ],
  glass_layers: [
    { required: true, message: '请输入玻璃层数', trigger: 'blur' }
  ],
  interlayer_layers: [
    { required: true, message: '请输入夹层数', trigger: 'blur' }
  ],
  windscreen_thick: [
    { required: true, message: '请输入风窗厚度', trigger: 'blur' }
  ],
  interlayer_thick: [
    { required: true, message: '请输入夹层厚度', trigger: 'blur' }
  ],
  glass_treatment: [
    { required: true, message: '请输入玻璃处理', trigger: 'blur' }
  ],
  interlayer_type: [
    { required: true, message: '请输入夹层类型', trigger: 'blur' }
  ],
  coating_type: [
    { required: true, message: '请输入涂层类型', trigger: 'blur' }
  ],
  coating_thick: [
    { required: true, message: '请输入涂层厚度', trigger: 'blur' }
  ],
  material_nature: [
    { required: true, message: '请输入材料性质', trigger: 'blur' }
  ],
  coating_color: [
    { required: true, message: '请输入涂层颜色', trigger: 'blur' }
  ],
  remarks: [
    { required: true, message: '请输入备注', trigger: 'blur' }
  ],
  vehicles: [
    {
      veh_mfr: [{ required: true, message: '请输入车辆制造商', trigger: 'blur' }],
      veh_type: [{ required: true, message: '请输入车辆类型', trigger: 'blur' }],
      veh_cat: [{ required: true, message: '请输入车辆类别', trigger: 'blur' }],
      dev_area: [{ required: true, message: '请输入开发区域', trigger: 'blur' }],
      seg_height: [{ required: true, message: '请输入段高度', trigger: 'blur' }],
      curv_radius: [{ required: true, message: '请输入曲率半径', trigger: 'blur' }],
      inst_angle: [{ required: true, message: '请输入安装角度', trigger: 'blur' }],
      seat_angle: [{ required: true, message: '请输入座椅角度', trigger: 'blur' }],
      rpoint_coords: [{ required: true, message: '请输入参考点坐标', trigger: 'blur' }],
      dev_desc: [{ required: true, message: '请输入开发描述', trigger: 'blur' }]
    }
  ]
}

// 文档生成相关
const generating = ref(false)
const generationProgress = ref(0)
const generationResult = ref<any>(null)
const generatedDocuments = ref<any[]>([]) // 新增：保存所有生成的文档
const selectedFormat = ref('docx') // 新增：文档格式选择

// 计算属性
const canProceedToNext = computed(() => {
  return applicationFiles.value.length > 0 && reportFiles.value.length > 0
})

// 方法
const goToStep = (step: number) => {
  if (testMode.value || step <= currentStep.value) {
    currentStep.value = step
  }
}

const handleTestModeChange = (value: boolean) => {
  if (value) {
    ElMessage.info('已启用测试模式，可以自由跳转到任何步骤')
  } else {
    ElMessage.info('已切换到正常模式')
  }
}

const handleApplicationChange = (file: any) => {
  applicationFiles.value = [file]
}

const handleReportChange = (file: any) => {
  reportFiles.value = [file]
}

const uploadDocuments = async () => {
  if (!canProceedToNext.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('application_file', applicationFiles.value[0].raw)
    formData.append('report_file', reportFiles.value[0].raw)

    const response = await mvpAPI.uploadDocuments(formData)
    
    if (response.data.success) {
      sessionId.value = response.data.session_id
      ElMessage.success('文件上传成功')
      currentStep.value = 1
      await extractInfo()
    } else {
      ElMessage.error(response.data.error || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('文件上传失败')
  } finally {
    uploading.value = false
  }
}

const extractInfo = async () => {
  // 在测试模式下，如果没有session_id，自动生成一个
  const currentSessionId = generateTestSessionId()
  
  if (!currentSessionId && !testMode.value) return

  extracting.value = true
  extractionProgress.value = 0

  // 模拟进度
  const progressInterval = setInterval(() => {
    if (extractionProgress.value < 90) {
      extractionProgress.value += 10
    }
  }, 200)

  try {
    let response
    if (testMode.value) {
      // 测试模式：使用模拟数据
      await new Promise(resolve => setTimeout(resolve, 1500)) // 模拟延迟
      response = {
        data: {
          success: true,
          data: {
            approval_no: "TEST-2024-001",
            information_folder_no: "IF-001",
            safety_class: "A",
            pane_desc: "测试玻璃板",
            glass_layers: "5",
            interlayer_layers: "1",
            windscreen_thick: "5mm",
            interlayer_thick: "10mm",
            glass_treatment: "涂层",
            interlayer_type: "PVB",
            coating_type: "UV",
            coating_thick: "50μm",
            material_nature: "钢化玻璃",
            coating_color: "透明",
            remarks: "测试数据",
            vehicles: [
              {
                veh_mfr: "测试制造商1",
                veh_type: "测试类型1",
                veh_cat: "测试类别1",
                dev_area: "测试区域1",
                seg_height: "100mm",
                curv_radius: "500mm",
                inst_angle: "45°",
                seat_angle: "30°",
                rpoint_coords: "100,200",
                dev_desc: "测试描述1"
              },
              {
                veh_mfr: "测试制造商2",
                veh_type: "测试类型2",
                veh_cat: "测试类别2",
                dev_area: "测试区域2",
                seg_height: "200mm",
                curv_radius: "1000mm",
                inst_angle: "90°",
                seat_angle: "60°",
                rpoint_coords: "200,300",
                dev_desc: "测试描述2"
              }
            ]
          }
        }
      }
    } else {
      response = await mvpAPI.extractInfo({ session_id: currentSessionId })
    }
    
    if (response.data.success) {
      extractionResult.value = response.data.data
      extractionProgress.value = 100
      ElMessage.success('信息提取成功')
      
      // 填充表单数据
      fillFormData(response.data.data)
    } else {
      ElMessage.error(response.data.error || '信息提取失败')
    }
  } catch (error) {
    console.error('信息提取失败:', error)
    ElMessage.error('信息提取失败')
  } finally {
    extracting.value = false
    clearInterval(progressInterval)
  }
}

const fillFormData = (data: any) => {
  // 填充IF_Template_2.docx相关字段
  if (data.template_fields) {
    Object.assign(formData, {
      approval_no: data.template_fields.approval_no || '',
      information_folder_no: data.template_fields.information_folder_no || '',
      safety_class: data.template_fields.safety_class || '',
      pane_desc: data.template_fields.pane_desc || '',
      glass_layers: data.template_fields.glass_layers || '',
      interlayer_layers: data.template_fields.interlayer_layers || '',
      windscreen_thick: data.template_fields.windscreen_thick || '',
      interlayer_thick: data.template_fields.interlayer_thick || '',
      glass_treatment: data.template_fields.glass_treatment || '',
      interlayer_type: data.template_fields.interlayer_type || '',
      coating_type: data.template_fields.coating_type || '',
      coating_thick: data.template_fields.coating_thick || '',
      material_nature: data.template_fields.material_nature || '',
      coating_color: data.template_fields.coating_color || '',
      remarks: data.template_fields.remarks || '',
      vehicles: data.template_fields.vehicles || [{  // 默认至少有一个车辆信息
        veh_mfr: '',
        veh_type: '',
        veh_cat: '',
        dev_area: '',
        seg_height: '',
        curv_radius: '',
        inst_angle: '',
        seat_angle: '',
        rpoint_coords: '',
        dev_desc: ''
      }]
    })
  }
}

const addVehicleInfo = () => {
  formData.vehicles.push({
    veh_mfr: '',
    veh_type: '',
    veh_cat: '',
    dev_area: '',
    seg_height: '',
    curv_radius: '',
    inst_angle: '',
    seat_angle: '',
    rpoint_coords: '',
    dev_desc: ''
  })
}

const removeVehicleInfo = (index: number) => {
  formData.vehicles.splice(index, 1)
}

const saveFormData = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请完善必填信息')
    return
  }

  saving.value = true
  try {
    // 在测试模式下，如果没有session_id，自动生成一个
    const currentSessionId = generateTestSessionId()
    
    // 保存表单数据
    const response = await mvpAPI.saveFormData({
      session_id: currentSessionId,
      form_data: formData
    })
    
    if (response.data.success) {
      // 如果返回了新的session_id（测试模式），更新sessionId
      if (response.data.session_id && !sessionId.value) {
        sessionId.value = response.data.session_id
        console.log('更新session_id:', sessionId.value)
      }
      
      // 创建申请书记录
      try {
        const applicationData = {
          title: formData.title || '申请书',
          application_type: 'certification',
          session_id: sessionId.value,
          approval_no: formData.approval_no,
          information_folder_no: formData.information_folder_no,
          company_name: formData.company_name || '',
          company_address: formData.company_address || '',
          windscreen_thick: formData.windscreen_thick,
          interlayer_thick: formData.interlayer_thick,
          glass_layers: formData.glass_layers,
          interlayer_layers: formData.interlayer_layers,
          interlayer_type: formData.interlayer_type,
          glass_treatment: formData.glass_treatment,
          coating_type: formData.coating_type,
          coating_thick: formData.coating_thick,
          coating_color: formData.coating_color,
          material_nature: formData.material_nature,
          safety_class: formData.safety_class,
          pane_desc: formData.pane_desc,
          vehicles: formData.vehicles || [],
          remarks: formData.remarks
        }
        
        // 申请书就是FormData，不需要额外创建
        // const { applicationAPI } = await import('../api/application')
        // await applicationAPI.createApplication(applicationData)
        // ElMessage.success('申请书记录已创建')
      } catch (error) {
        console.error('创建申请书记录失败:', error)
        // 不阻止流程继续
      }
      
      ElMessage.success('表单数据保存成功')
      currentStep.value = 3
      // 移除自动生成文档的调用，让用户手动选择格式并生成
      // await generateDocuments()
    } else {
      ElMessage.error(response.data.error || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('表单数据保存失败')
  } finally {
    saving.value = false
  }
}

const generateDocuments = async () => {
  // 在测试模式下，如果没有session_id，自动生成一个
  const currentSessionId = generateTestSessionId()
  
  if (!currentSessionId && !testMode.value) return

  generating.value = true
  generationProgress.value = 0

  // 模拟进度
  const progressInterval = setInterval(() => {
    if (generationProgress.value < 90) {
      generationProgress.value += 10
    }
  }, 200)

  try {
    let response
    if (testMode.value) {
      // 测试模式：使用测试数据生成真实文档
      const testData = {
        session_id: currentSessionId,
        output_format: selectedFormat.value
      }
      response = await mvpAPI.generateDocuments(testData)
    } else {
      response = await mvpAPI.generateDocuments({ 
        session_id: currentSessionId,
        output_format: selectedFormat.value
      })
    }
    
    if (response.data.success) {
      const result = response.data.data
      generationResult.value = result
      // 添加到已生成文档列表
      generatedDocuments.value.push({
        ...result,
        format: result.filename.endsWith('.pdf') ? 'PDF' : 'Word',
        generatedTime: new Date().toLocaleString()
      })
      generationProgress.value = 100
      ElMessage.success('文档生成成功')
    } else {
      ElMessage.error(response.data.error || '文档生成失败')
    }
  } catch (error) {
    console.error('文档生成失败:', error)
    ElMessage.error('文档生成失败')
  } finally {
    generating.value = false
    clearInterval(progressInterval)
  }
}

const downloadDocument = async () => {
  if (generationResult.value?.download_url) {
    window.open(`http://localhost:5000${generationResult.value.download_url}`, '_blank')
  }
}



const downloadSpecificDocument = (doc: any) => {
  if (doc.download_url) {
    window.open(`http://localhost:5000${doc.download_url}`, '_blank')
  }
}

// 一键生成测试数据
const generateTestData = () => {
  if (!testMode.value) {
    ElMessage.warning('请先启用测试模式')
    return
  }
  
  // 生成测试数据
  Object.assign(formData, {
    // 基础信息
    title: '测试申请书',
    
    // IF_Template_2.docx 变量
    approval_no: "TEST-2024-001",
    information_folder_no: "IF-001",
    safety_class: "A",
    pane_desc: "测试玻璃板描述",
    glass_layers: "5",
    interlayer_layers: "1",
    windscreen_thick: "5mm",
    interlayer_thick: "10mm",
    glass_treatment: "涂层处理",
    interlayer_type: "PVB",
    coating_type: "UV涂层",
    coating_thick: "50μm",
    material_nature: "钢化玻璃",
    coating_color: "透明",
    remarks: "这是测试数据，用于验证文档生成功能",
    
    // 车辆信息
    vehicles: [
      {
        veh_mfr: "测试制造商1",
        veh_type: "轿车",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "100mm",
        curv_radius: "500mm",
        inst_angle: "45°",
        seat_angle: "30°",
        rpoint_coords: "100,200",
        dev_desc: "测试车辆1的开发描述"
      },
      {
        veh_mfr: "测试制造商2",
        veh_type: "SUV",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "120mm",
        curv_radius: "600mm",
        inst_angle: "50°",
        seat_angle: "35°",
        rpoint_coords: "150,250",
        dev_desc: "测试车辆2的开发描述"
      }
    ]
  })
  
  ElMessage.success('测试数据已生成')
}

const finishProcess = () => {
  ElMessageBox.confirm(
    '流程已完成，是否开始新的处理？',
    '完成确认',
    {
      confirmButtonText: '开始新的',
      cancelButtonText: '关闭',
      type: 'success'
    }
  ).then(() => {
    // 重置所有状态
    currentStep.value = 0
    sessionId.value = ''
    applicationFiles.value = []
    reportFiles.value = []
    extractionResult.value = null
    generationResult.value = null
    Object.keys(formData).forEach(key => {
      if (typeof formData[key] === 'string') {
        formData[key] = ''
      } else if (typeof formData[key] === 'object') {
        formData[key] = {}
      }
    })
  })
}
</script>

<style scoped>
.mvp-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
  margin-top: 1rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-graphic {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2A3B8F 0%, #1e2a5e 100%);
  border-radius: 8px;
  position: relative;
}

.logo-graphic::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 4px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-main {
  font-weight: 700;
  font-size: 1.2rem;
  color: #2A3B8F;
}

.logo-sub {
  font-size: 0.8rem;
  color: #666;
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2A3B8F;
}

.test-mode-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.test-controls {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
}

.mvp-main {
  padding: 2rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.step-navigation {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.step-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
}

.step-item:last-child {
  border-right: none;
}

.step-item.active {
  background: #2A3B8F;
  color: white;
}

.step-item.completed {
  background: #67c23a;
  color: white;
}

.step-item.disabled {
  color: #999;
  cursor: not-allowed;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.step-label {
  font-weight: 500;
}

.step-content {
  padding: 2rem;
}

.step-panel {
  min-height: 500px;
}

.panel-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.panel-header .header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header .header-left h2 {
  margin: 0 0 0.5rem 0;
  color: #2A3B8F;
  font-size: 1.5rem;
  font-weight: 600;
}

.panel-header .header-left p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.panel-header .header-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.upload-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.upload-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px dashed #ddd;
  transition: all 0.3s ease;
}

.upload-card:hover {
  border-color: #2A3B8F;
  background: #f0f2ff;
}

.upload-card h3 {
  margin: 0 0 1rem 0;
  color: #2A3B8F;
  font-size: 1.1rem;
}

.extraction-section,
.generation-section {
  text-align: center;
  padding: 3rem 0;
}

.extraction-loading,
.generation-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.extraction-result,
.generation-result {
  text-align: left;
}

.result-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
}

.result-preview pre {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.result-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.download-section {
  text-align: center;
  margin-top: 2rem;
}

.format-selection {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #ddd;
  transition: all 0.3s ease;
}

.format-selection:hover {
  border-color: #2A3B8F;
  background: #f0f2ff;
}

.format-options {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1rem;
}

.format-options .el-radio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.format-options .el-radio .el-icon {
  font-size: 1.2rem;
}

.format-description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.generate-actions {
  text-align: center;
}

.format-tip {
  margin-bottom: 1rem;
}

.generation-result {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.result-info {
  margin: 1rem 0;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.result-info p {
  margin: 0.5rem 0;
  color: #374151;
}

.download-section {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.generated-documents {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.generated-documents h3 {
  margin: 0 0 1rem 0;
  color: #2A3B8F;
  font-size: 1.1rem;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.document-item:hover {
  border-color: #2A3B8F;
  box-shadow: 0 2px 8px rgba(42, 59, 143, 0.1);
}

.document-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.document-name {
  font-weight: 600;
  color: #2A3B8F;
}

.document-format {
  font-size: 0.875rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.document-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.form-section {
  margin-bottom: 2rem;
}

.certification-form {
  max-width: 800px;
  margin: 0 auto;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

/* Element Plus 样式覆盖 */
:deep(.el-upload-dragger) {
  background: rgba(255, 255, 255, 0.8);
  border: 2px dashed #2A3B8F;
  border-radius: 12px;
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #1e2a5e;
  background: rgba(42, 59, 143, 0.05);
}

:deep(.el-divider__text) {
  background: transparent;
  color: #2A3B8F;
  font-weight: 600;
  font-size: 1rem;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #2A3B8F;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

:deep(.el-date-editor) {
  border-radius: 8px;
}

.vehicle-info-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  border: 2px dashed #ddd;
  transition: all 0.3s ease;
  position: relative;
}

.vehicle-info-section:hover {
  border-color: #2A3B8F;
  background: #f0f2ff;
  box-shadow: 0 4px 12px rgba(42, 59, 143, 0.1);
}

.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.vehicle-header h4 {
  margin: 0;
  color: #2A3B8F;
  font-size: 1.1rem;
  font-weight: 600;
}

.vehicle-header .el-button {
  margin-left: auto;
}

.vehicle-info-section:not(:last-child) {
  margin-bottom: 1.5rem;
}
</style> 