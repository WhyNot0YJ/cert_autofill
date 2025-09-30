<template>
  <div class="company-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">公司信息管理</h1>
      <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
        添加公司
      </el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索公司名称、简称或地址"
            clearable
            @input="handleSearch"
            :prefix-icon="Search"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.sort_by" @change="handleSortChange" placeholder="排序字段">
            <el-option label="创建时间" value="created_at" />
            <el-option label="公司名称" value="name" />
            <el-option label="更新时间" value="updated_at" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.sort_order" @change="handleSortChange" placeholder="排序方向">
            <el-option label="降序" value="desc" />
            <el-option label="升序" value="asc" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.per_page" @change="handlePerPageChange" placeholder="每页数量">
            <el-option label="10条/页" :value="10" />
            <el-option label="20条/页" :value="20" />
            <el-option label="50条/页" :value="50" />
            <el-option label="100条/页" :value="100" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="resetSearch" :icon="Refresh">重置</el-button>
        </el-col>
        <el-col :span="4">
          <el-dropdown @command="handleColumnFilter" trigger="click">
            <el-button>
              <el-icon><Setting /></el-icon>
              列筛选
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  v-for="column in availableColumns" 
                  :key="column.key"
                  :command="column.key"
                >
                  <el-checkbox 
                    v-model="column.visible" 
                    @change="updateColumnVisibility"
                    @click.stop
                  >
                    {{ column.label }}
                  </el-checkbox>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-col>
      </el-row>
    </div>

    <!-- 公司列表表格 -->
    <div class="table-container">
      <el-table 
        v-loading="loading" 
        :data="companyList" 
        stripe 
        style="width: 100%"
        @sort-change="handleTableSort"
        :border="true"
        :resizable="true"
        :show-overflow-tooltip="true"
      >
        <el-table-column 
          v-if="getColumnVisibility('id')"
          prop="id" 
          label="ID" 
          min-width="80" 
          sortable="custom" 
        />
        
        <el-table-column 
          v-if="getColumnVisibility('name')"
          prop="name" 
          label="公司名称" 
          min-width="200" 
          sortable="custom"
        >
          <template #default="{ row }">
            <div class="company-name">
              <el-image 
                v-if="row.picture" 
                :src="getImageUrl(row.picture)" 
                :alt="row.name"
                class="company-logo"
                fit="cover"
              />
              <div class="company-info">
                <div class="company-title">{{ row.name }}</div>
                <div v-if="row.company_contraction" class="company-contraction">{{ row.company_contraction }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="getColumnVisibility('address')"
          prop="address" 
          label="公司地址" 
          min-width="250" 
          show-overflow-tooltip 
        />
        
        <el-table-column 
          v-if="getColumnVisibility('trade_info')"
          label="商标名称/图案" 
          min-width="200"
        >
          <template #default="{ row }">
            <TradeNamesMarksDisplay 
              :trade-names="row.trade_names" 
              :trade-marks="row.trade_marks || []" 
              size="small"
              :max-images="2"
            />
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="getColumnVisibility('equipment')"
          label="设备信息" 
          min-width="150"
        >
          <template #default="{ row }">
            <div class="equipment-info">
              <el-tag v-if="row.equipment && row.equipment.length > 0" type="success" size="small">
                {{ row.equipment.length }}个设备
              </el-tag>
              <el-tag v-else type="info" size="small">无设备</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="getColumnVisibility('image_info')"
          label="图片信息" 
          min-width="120"
        >
          <template #default="{ row }">
            <div class="image-info">
              <el-tag v-if="row.picture" type="success" size="small">有图片</el-tag>
              <el-tag v-if="row.signature" type="primary" size="small">有签名</el-tag>
              <el-tag v-if="row.trade_marks && row.trade_marks.length > 0" type="warning" size="small">{{ row.trade_marks.length }}个商标</el-tag>
              <el-tag v-if="!row.picture && !row.signature && (!row.trade_marks || row.trade_marks.length === 0)" type="info" size="small">无图片</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="getColumnVisibility('created_at')"
          prop="created_at" 
          label="创建时间" 
          min-width="180" 
          sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="getColumnVisibility('updated_at')"
          prop="updated_at" 
          label="更新时间" 
          min-width="180" 
          sortable="custom"
        >
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)" :icon="View">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)" :icon="Edit">编辑</el-button>
            <el-popconfirm 
              title="确定删除这个公司吗？" 
              @confirm="handleDelete(row.id)"
              confirm-button-text="确定"
              cancel-button-text="取消"
            >
              <template #reference>
                <el-button size="small" type="danger" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页组件 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑公司对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingCompany ? '编辑公司' : '添加公司'"
      width="600px"
      @close="resetForm"
    >
      <el-form 
        ref="companyFormRef" 
        :model="companyForm" 
        :rules="companyFormRules" 
        label-width="100px"
      >
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="companyForm.name" placeholder="请输入公司名称" />
        </el-form-item>
        
        <el-form-item label="公司简称" prop="company_contraction">
          <el-input v-model="companyForm.company_contraction" placeholder="请输入公司简称" />
        </el-form-item>
        
        <el-form-item label="公司地址" prop="address">
          <el-input 
            v-model="companyForm.address" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入公司地址" 
          />
        </el-form-item>
        
        <el-form-item label="商标名称" prop="trade_names">
          <TradeNamesEditor v-model="companyForm.trade_names" />
        </el-form-item>
        
        <el-form-item label="商标图案">
          <MarksEditor v-model="companyForm.trade_marks" />
        </el-form-item>
        
        <!-- 设备信息 -->
        <el-divider content-position="left">
          设备信息
          <el-button 
            type="primary" 
            size="small" 
            @click="addEquipment"
            style="margin-left: 10px;"
          >
            <el-icon><Plus /></el-icon>
            添加设备
          </el-button>
          <el-button 
            type="success" 
            size="small" 
            @click="showBatchAddDialog = true"
            style="margin-left: 10px;"
          >
            <el-icon><Plus /></el-icon>
            批量添加
          </el-button>
        </el-divider>
        
        <!-- 设备信息列表 -->
        <div v-for="(equipment, index) in companyForm.equipment" :key="index" class="equipment-info-section">
          <div class="equipment-header">
            <h4>设备信息 {{ index + 1 }}</h4>
            <el-button 
              type="danger" 
              size="small" 
              @click="removeEquipment(index)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item :label="`设备编号`" :prop="`equipment.${index}.no`">
                <el-input 
                  v-model="equipment.no" 
                  placeholder="请输入设备编号，如：TST2017223"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item :label="`设备名称`" :prop="`equipment.${index}.name`">
                <el-input 
                  v-model="equipment.name" 
                  placeholder="请输入设备名称"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <el-form-item label="公司图片">
          <div class="upload-container">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handlePictureChange"
              accept="image/*"
            >
              <el-button :icon="Upload">选择图片</el-button>
            </el-upload>
            <div v-if="companyForm.picture || previewPicture" class="image-preview">
              <el-image 
                :src="previewPicture || getImageUrl(companyForm.picture)" 
                class="preview-image"
                fit="cover"
              />
              <el-button 
                size="small" 
                type="danger" 
                @click="clearPicture"
                :icon="Delete"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="签名图片">
          <div class="upload-container">
            <el-upload
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleSignatureChange"
              accept="image/*"
            >
              <el-button :icon="Upload">选择签名</el-button>
            </el-upload>
            <div v-if="companyForm.signature || previewSignature" class="image-preview">
              <el-image 
                :src="previewSignature || getImageUrl(companyForm.signature)" 
                class="preview-image"
                fit="cover"
              />
              <el-button 
                size="small" 
                type="danger" 
                @click="clearSignature"
                :icon="Delete"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingCompany ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看公司详情对话框 -->
    <el-dialog v-model="showViewDialog" title="公司详情" width="500px">
      <div v-if="viewingCompany" class="company-detail">
        <div class="detail-item">
          <label>公司名称：</label>
          <span>{{ viewingCompany.name }}</span>
        </div>
        <div v-if="viewingCompany.company_contraction" class="detail-item">
          <label>公司简称：</label>
          <span>{{ viewingCompany.company_contraction }}</span>
        </div>
        <div class="detail-item">
          <label>公司地址：</label>
          <span>{{ viewingCompany.address || '未填写' }}</span>
        </div>
        <div class="detail-item">
          <label>商标名称/图案：</label>
          <TradeNamesMarksDisplay 
            :trade-names="viewingCompany.trade_names" 
            :trade-marks="viewingCompany.trade_marks || []" 
            size="large"
            :max-images="10"
          />
        </div>
        <div v-if="viewingCompany.equipment && viewingCompany.equipment.length > 0" class="detail-item">
          <label>设备信息：</label>
          <div class="equipment-list">
            <div v-for="(equipment, index) in viewingCompany.equipment" :key="index" class="equipment-item">
              <div class="equipment-no">{{ equipment.no }}</div>
              <div class="equipment-name">{{ equipment.name }}</div>
            </div>
          </div>
        </div>
        <div class="detail-item">
          <label>创建时间：</label>
          <span>{{ formatDate(viewingCompany.created_at) }}</span>
        </div>
        <div class="detail-item">
          <label>更新时间：</label>
          <span>{{ formatDate(viewingCompany.updated_at) }}</span>
        </div>
        <div v-if="viewingCompany.picture" class="detail-item">
          <label>公司图片：</label>
          <div class="picture-preview">
            <el-image 
              :src="getImageUrl(viewingCompany.picture)" 
              class="detail-image"
              fit="cover"
              @error="handleImageError"
            />
          </div>
        </div>
        <div v-if="viewingCompany.signature" class="detail-item">
          <label>签名图片：</label>
          <div class="signature-preview">
            <el-image 
              :src="getImageUrl(viewingCompany.signature)" 
              class="detail-image"
              fit="cover"
              @error="handleImageError"
            />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 批量添加设备对话框 -->
    <el-dialog v-model="showBatchAddDialog" title="批量添加设备" width="600px">
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
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete, Upload, Setting, ArrowDown } from '@element-plus/icons-vue'
import { companyAPI, type Company, type CompanyListParams, type CreateCompanyRequest, type UpdateCompanyRequest, type Equipment } from '@/api/company'
import { uploadAPI } from '@/api/upload'
import { getServerBaseURL } from '@/api'
import TradeNamesMarksDisplay from '@/components/TradeNamesMarksDisplay.vue'
import TradeNamesEditor from '@/components/TradeNamesEditor.vue'
import MarksEditor from '@/components/MarksEditor.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const companyList = ref<Company[]>([])
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const showBatchAddDialog = ref(false)
const editingCompany = ref<Company | null>(null)
const viewingCompany = ref<Company | null>(null)

// 列筛选
const availableColumns = ref([
  { key: 'id', label: 'ID', visible: true },
  { key: 'name', label: '公司名称', visible: true },
  { key: 'address', label: '公司地址', visible: true },
  { key: 'trade_info', label: '商标名称/图案', visible: true },
  { key: 'equipment', label: '设备信息', visible: true },
  { key: 'image_info', label: '图片信息', visible: true },
  { key: 'created_at', label: '创建时间', visible: true },
  { key: 'updated_at', label: '更新时间', visible: true }
])

const getColumnVisibility = (columnKey: string) => {
  const column = availableColumns.value.find(col => col.key === columnKey)
  return column ? column.visible : true
}

const handleColumnFilter = (command: string) => {
  // 切换列的可见性
  const column = availableColumns.value.find(col => col.key === command)
  if (column) {
    column.visible = !column.visible
  }
}

const updateColumnVisibility = () => {
  // 当checkbox状态改变时触发
}

// 搜索参数
const searchParams = reactive<CompanyListParams>({
  page: 1,
  per_page: 10,
  search: '',
  sort_by: 'created_at',
  sort_order: 'desc'
})

// 分页信息
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0,
  pages: 0,
  has_prev: false,
  has_next: false,
  prev_num: null as number | null,
  next_num: null as number | null
})

// 表单数据
const companyForm = reactive<CreateCompanyRequest & { signature?: File | string; picture?: File | string }>({
  name: '',
  company_contraction: '',
  address: '',
  trade_names: [],  // 改为数组
  trade_marks: [],
  equipment: [{ no: '', name: '' }],  // 设备信息数组，默认有一个空项
  signature: undefined,
  picture: undefined
})

// 图片预览
const previewPicture = ref<string>('')
const previewSignature = ref<string>('')

// 批量添加设备
const batchEquipmentText = ref<string>('')
const parsedEquipment = ref<Equipment[]>([])

// 表单引用
const companyFormRef = ref()

// 表单验证规则
const companyFormRules = {
  name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' },
    { min: 2, max: 255, message: '公司名称长度应在2-255个字符之间', trigger: 'blur' }
  ]
}

// 搜索防抖
let searchTimeout: ReturnType<typeof setTimeout> | null = null

// 方法
const loadCompanies = async () => {
  loading.value = true
  try {
    const response = await companyAPI.getCompanies(searchParams)
    // 拦截器已经返回了业务数据，直接使用
    if (response.success) {
      companyList.value = response.data.companies
      Object.assign(pagination, response.data.pagination)
      searchParams.page = response.data.pagination.page
    }
  } catch (error) {
    ElMessage.error('加载公司列表失败')
    console.error('Load companies error:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchParams.page = 1
    loadCompanies()
  }, 500)
}

const handleSortChange = () => {
  searchParams.page = 1
  loadCompanies()
}

const handlePerPageChange = () => {
  searchParams.page = 1
  loadCompanies()
}

const handleTableSort = ({ prop, order }: { prop: string; order: string | null }) => {
  if (order) {
    searchParams.sort_by = prop
    searchParams.sort_order = order === 'ascending' ? 'asc' : 'desc'
    loadCompanies()
  }
}

const resetSearch = () => {
  Object.assign(searchParams, {
    page: 1,
    per_page: 10,
    search: '',
    sort_by: 'created_at',
    sort_order: 'desc'
  })
  loadCompanies()
}

const handleSizeChange = (size: number) => {
  searchParams.per_page = size
  searchParams.page = 1
  loadCompanies()
}

const handleCurrentChange = (page: number) => {
  searchParams.page = page
  loadCompanies()
}

const handleView = (company: Company) => {
  viewingCompany.value = company
  showViewDialog.value = true
}

const handleEdit = (company: Company) => {
  editingCompany.value = company
  Object.assign(companyForm, {
    name: company.name,
    company_contraction: company.company_contraction || '',
    address: company.address || '',
    trade_names: company.trade_names || [],  // 改为数组
    trade_marks: company.trade_marks || [],
    equipment: company.equipment || [],  // 设备信息
    signature: company.signature,
    picture: company.picture
  })
  showCreateDialog.value = true
}

const handleDelete = async (id: number) => {
  try {
    const response = await companyAPI.deleteCompany(id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadCompanies()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '删除失败')
  }
}

const handlePictureChange = async (file: any) => {
  try {
    const res = await uploadAPI.uploadCompanyPicture(file.raw)
    if (res.success) {
      companyForm.picture = res.data.url
      previewPicture.value = res.data.url
      ElMessage.success('公司图片上传成功')
    } else {
      ElMessage.error(res.message || '公司图片上传失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '公司图片上传失败')
  }
}

const handleSignatureChange = async (file: any) => {
  try {
    const res = await uploadAPI.uploadCompanySignature(file.raw)
    if (res.success) {
      companyForm.signature = res.data.url
      previewSignature.value = res.data.url
      ElMessage.success('签名图片上传成功')
    } else {
      ElMessage.error(res.message || '签名图片上传失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '签名图片上传失败')
  }
}

const clearPicture = () => {
  companyForm.picture = undefined
  previewPicture.value = ''
}

const clearSignature = () => {
  companyForm.signature = undefined
  previewSignature.value = ''
}

// 设备管理方法
const addEquipment = () => {
  if (companyForm.equipment) {
    companyForm.equipment.push({
      no: '',
      name: ''
    })
  }
}

const removeEquipment = (index: number) => {
  if (companyForm.equipment && companyForm.equipment.length > 0) {
    companyForm.equipment.splice(index, 1)
  }
}

// 批量添加设备相关方法
const parseEquipmentText = (text: string): Equipment[] => {
  const lines = text.split('\n').filter(line => line.trim())
  const equipment: Equipment[] = []
  
  for (const line of lines) {
    // 匹配格式：no. 设备编号: 设备名称 或 no. 设备编号：设备名称
    // 支持全角冒号（：）和半角冒号（:）
    const match = line.match(/no\.\s*([^:：]+)[:：]\s*(.+)/i)
    if (match) {
      const no = match[1].trim()
      const name = match[2].trim()
      if (no && name) {
        equipment.push({ no, name })
      }
    }
  }
  
  return equipment
}

const handleBatchAdd = () => {
  if (parsedEquipment.value.length === 0) {
    ElMessage.warning('没有可添加的设备')
    return
  }
  
  // 将解析的设备添加到表单中
  if (!companyForm.equipment) {
    companyForm.equipment = []
  }
  
  // 如果当前只有一个空设备，先清空
  if (companyForm.equipment.length === 1 && !companyForm.equipment[0].no && !companyForm.equipment[0].name) {
    companyForm.equipment = []
  }
  
  // 添加解析的设备
  companyForm.equipment.push(...parsedEquipment.value)
  
  ElMessage.success(`成功添加 ${parsedEquipment.value.length} 个设备`)
  showBatchAddDialog.value = false
  batchEquipmentText.value = ''
  parsedEquipment.value = []
}

const handleSubmit = async () => {
  if (!companyFormRef.value) return
  
  try {
    await companyFormRef.value.validate()
    submitting.value = true
    
    if (editingCompany.value) {
      // 更新公司
      const updateData: UpdateCompanyRequest = {
        name: companyForm.name,
        company_contraction: companyForm.company_contraction,
        address: companyForm.address,
        trade_names: companyForm.trade_names,
        trade_marks: companyForm.trade_marks,
        equipment: companyForm.equipment
      }
      // 直接传递 URL（或字符串）到后端
      if (companyForm.picture) updateData.picture = companyForm.picture as any
      if (companyForm.signature) updateData.signature = companyForm.signature as any
      
      const response = await companyAPI.updateCompany(editingCompany.value.id, updateData)
      if (response.success) {
        ElMessage.success('更新成功')
        showCreateDialog.value = false
        loadCompanies()
      }
    } else {
      // 创建公司
      const response = await companyAPI.createCompany(companyForm)
      if (response.success) {
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadCompanies()
      }
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || (editingCompany.value ? '更新失败' : '创建失败'))
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  editingCompany.value = null
  Object.assign(companyForm, {
    name: '',
    company_contraction: '',
    address: '',
    trade_names: [],  // 改为数组
    trade_marks: [],
    equipment: [{ no: '', name: '' }],  // 设备信息，默认有一个空项
    signature: undefined,
    picture: undefined
  })
  previewPicture.value = ''
  previewSignature.value = ''
  if (companyFormRef.value) {
    companyFormRef.value.resetFields()
  }
}

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

const getImageUrl = (path: string | undefined) => {
  if (!path) return ''
  // 完整URL直接返回
  if (path.startsWith('http')) return path
  // 其它一律拼接后端基础URL，确保端口（如 :81）正确
  const baseUrl = getServerBaseURL()
  return path.startsWith('/') ? `${baseUrl}${path}` : `${baseUrl}/${path}`
}

const handleImageError = (error: any) => {
  console.error('图片加载失败:', error)
}

// 监听搜索参数变化
watch(() => searchParams.per_page, () => {
  pagination.per_page = searchParams.per_page
})

// 监听批量添加文本变化，实时解析设备信息
watch(batchEquipmentText, (newText) => {
  if (newText.trim()) {
    parsedEquipment.value = parseEquipmentText(newText)
  } else {
    parsedEquipment.value = []
  }
})

// 组件挂载时加载数据
onMounted(() => {
  loadCompanies()
})
</script>

<style scoped>
.company-management {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}


.page-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2A3B8F;
}

.search-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.company-name {
  display: flex;
  align-items: center;
  gap: 10px;
}

.company-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.company-title {
  font-weight: 600;
}

.company-contraction {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.company-trade-name {
  font-size: 12px;
}

.company-logo {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.image-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.image-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.company-detail {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-item label {
  font-weight: bold;
  min-width: 80px;
  color: #666;
}

.detail-image {
  width: 120px;
  height: 120px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.signature-preview,
.picture-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 确保对话框层级正确 */
:deep(.el-dialog) {
  z-index: 2000 !important;
}

:deep(.el-dialog__wrapper) {
  z-index: 2000 !important;
}

/* 优化图片预览在对话框中的显示 */
.company-detail .detail-item {
  flex-direction: column;
  align-items: flex-start;
}

.company-detail .detail-item label {
  margin-bottom: 8px;
}

/* 为图片容器添加一些间距 */
.detail-item:has(.detail-image) {
  margin-bottom: 20px;
}

.detail-item:has(.detail-image) label {
  margin-bottom: 12px;
}

/* 设备信息样式 */
.equipment-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.equipment-info-section {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fafafa;
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.equipment-header h4 {
  margin: 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.equipment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.equipment-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.equipment-no {
  font-weight: 600;
  color: #409eff;
  font-size: 12px;
}

.equipment-name {
  color: #666;
  font-size: 12px;
  line-height: 1.4;
}

/* 批量添加设备样式 */
.batch-add-container {
  padding: 10px 0;
}

.parsed-equipment {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.parsed-equipment h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.equipment-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.equipment-preview-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.equipment-preview-item span {
  flex: 1;
  font-size: 13px;
  color: #333;
}
</style>
