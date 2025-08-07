<template>
  <div class="field-editor">
    <!-- 第一页字段 -->
    <div class="field-section">
      <div class="section-title">
        <div class="title-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>第一页字段</h3>
      </div>
      
      <div class="fields-grid">
        <div class="field-group">
          <label class="field-label">Approval No.</label>
          <el-input 
            v-model="firstPageFields.approval_no" 
            placeholder="请输入批准号"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Information Folder No.</label>
          <el-input 
            v-model="firstPageFields.information_folder_no" 
            placeholder="请输入信息文件夹号"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Safety Class</label>
          <el-input 
            v-model="firstPageFields.safety_class" 
            placeholder="请输入安全等级"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Pane Description</label>
          <el-input 
            v-model="firstPageFields.pane_desc" 
            placeholder="请输入玻璃板描述"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Glass Layers</label>
          <el-input 
            v-model="firstPageFields.glass_layers" 
            placeholder="请输入玻璃层数"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Interlayer Layers</label>
          <el-input 
            v-model="firstPageFields.interlayer_layers" 
            placeholder="请输入夹层数"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Windscreen Thickness</label>
          <el-input 
            v-model="firstPageFields.windscreen_thick" 
            placeholder="请输入前风窗厚度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Interlayer Thickness</label>
          <el-input 
            v-model="firstPageFields.interlayer_thick" 
            placeholder="请输入夹层厚度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Glass Treatment</label>
          <el-input 
            v-model="firstPageFields.glass_treatment" 
            placeholder="请输入玻璃处理方式"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Interlayer Type</label>
          <el-input 
            v-model="firstPageFields.interlayer_type" 
            placeholder="请输入夹层类型"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Coating Type</label>
          <el-input 
            v-model="firstPageFields.coating_type" 
            placeholder="请输入涂层类型"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Coating Thickness</label>
          <el-input 
            v-model="firstPageFields.coating_thick" 
            placeholder="请输入涂层厚度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Material Nature</label>
          <el-input 
            v-model="firstPageFields.material_nature" 
            placeholder="请输入材料性质"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Coating Color</label>
          <el-input 
            v-model="firstPageFields.coating_color" 
            placeholder="请输入涂层颜色"
            class="field-input"
          />
        </div>
        
        <div class="field-group full-width">
          <label class="field-label">Remarks</label>
          <el-input 
            v-model="firstPageFields.remarks" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注"
            class="field-input"
          />
        </div>
      </div>
    </div>

    <!-- 车辆信息字段 -->
    <div class="field-section">
      <div class="section-title">
        <div class="title-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 17H5C3.89543 17 3 16.1046 3 15V11C3 9.89543 3.89543 9 5 9H19C20.1046 9 21 9.89543 21 11V15C21 16.1046 20.1046 17 19 17Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 13H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M15 13H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 17V19C7 19.5523 6.55228 20 6 20H5C4.44772 20 4 19.5523 4 19V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 17V19C20 19.5523 19.5523 20 19 20H18C17.4477 20 17 19.5523 17 19V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>车辆信息字段</h3>
      </div>
      
      <div class="fields-grid">
        <div class="field-group full-width">
          <label class="field-label">Vehicle Manufacturer</label>
          <el-input 
            v-model="repeatedPageFields.veh_mfr" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入车辆制造商"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Vehicle Type</label>
          <el-input 
            v-model="repeatedPageFields.veh_type" 
            placeholder="请输入车辆类型"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Vehicle Category</label>
          <el-input 
            v-model="repeatedPageFields.veh_cat" 
            placeholder="请输入车辆类别"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Developed Area</label>
          <el-input 
            v-model="repeatedPageFields.dev_area" 
            placeholder="请输入开发区域"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Segment Height</label>
          <el-input 
            v-model="repeatedPageFields.seg_height" 
            placeholder="请输入段高度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Curvature Radius</label>
          <el-input 
            v-model="repeatedPageFields.curv_radius" 
            placeholder="请输入曲率半径"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Installation Angle</label>
          <el-input 
            v-model="repeatedPageFields.inst_angle" 
            placeholder="请输入安装角度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">Seat Back Angle</label>
          <el-input 
            v-model="repeatedPageFields.seat_angle" 
            placeholder="请输入座椅靠背角度"
            class="field-input"
          />
        </div>
        
        <div class="field-group">
          <label class="field-label">R-Point Coordinates</label>
          <el-input 
            v-model="repeatedPageFields.rpoint_coords" 
            placeholder="请输入R点坐标"
            class="field-input"
          />
        </div>
        
        <div class="field-group full-width">
          <label class="field-label">Device Description</label>
          <el-input 
            v-model="repeatedPageFields.dev_desc" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入设备描述"
            class="field-input"
          />
        </div>
        <div class="field-group">
          <label class="field-label">车辆图片（每页）</label>
          <el-upload
            class="upload-demo"
            action=""
            :show-file-list="false"
            :before-upload="handleImageUpload"
            accept="image/*"
          >
            <el-button size="small" type="primary">点击上传</el-button>
          </el-upload>
          <div v-if="repeatedPageFields.image" class="image-preview">
            <img :src="repeatedPageFields.image" alt="车辆图片预览" style="max-width: 200px; margin-top: 10px;" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineEmits, defineProps, watch } from 'vue';

const props = defineProps<{ fields: Record<string, string> }>();
const emit = defineEmits(['update:fields']);

// 第一页字段
const firstPageFields = computed({
  get: () => ({
    approval_no: props.fields.approval_no || '',
    information_folder_no: props.fields.information_folder_no || '',
    safety_class: props.fields.safety_class || '',
    pane_desc: props.fields.pane_desc || '',
    glass_layers: props.fields.glass_layers || '',
    interlayer_layers: props.fields.interlayer_layers || '',
    windscreen_thick: props.fields.windscreen_thick || '',
    interlayer_thick: props.fields.interlayer_thick || '',
    glass_treatment: props.fields.glass_treatment || '',
    interlayer_type: props.fields.interlayer_type || '',
    coating_type: props.fields.coating_type || '',
    coating_thick: props.fields.coating_thick || '',
    material_nature: props.fields.material_nature || '',
    coating_color: props.fields.coating_color || '',
    remarks: props.fields.remarks || ''
  }),
  set: (value) => {
    emit('update:fields', { ...props.fields, ...value });
  }
});

// 重复页字段
const repeatedPageFields = computed({
  get: () => ({
    veh_mfr: props.fields.veh_mfr || '',
    veh_type: props.fields.veh_type || '',
    veh_cat: props.fields.veh_cat || '',
    dev_area: props.fields.dev_area || '',
    seg_height: props.fields.seg_height || '',
    curv_radius: props.fields.curv_radius || '',
    inst_angle: props.fields.inst_angle || '',
    seat_angle: props.fields.seat_angle || '',
    rpoint_coords: props.fields.rpoint_coords || '',
    dev_desc: props.fields.dev_desc || '',
    image: props.fields.image || '' // 新增 image 字段
  }),
  set: (value) => {
    emit('update:fields', { ...props.fields, ...value });
  }
});

// 监听字段变化并更新
watch(firstPageFields, (newValue) => {
  emit('update:fields', { ...props.fields, ...newValue });
}, { deep: true });

watch(repeatedPageFields, (newValue) => {
  emit('update:fields', { ...props.fields, ...newValue });
}, { deep: true });

function handleImageUpload(file: File) {
  const reader = new FileReader();
  reader.onload = (e) => {
    emit('update:fields', { ...props.fields, image: e.target?.result });
  };
  reader.readAsDataURL(file);
  return false; // 阻止自动上传
}
</script>

<style scoped>
.field-editor {
  width: 100%;
}

.field-section {
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.title-icon {
  color: #2A3B8F;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(42, 59, 143, 0.1);
  border-radius: 8px;
}

.section-title h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-group.full-width {
  grid-column: 1 / -1;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.field-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s ease;
}

.field-input :deep(.el-input__wrapper:hover) {
  border-color: #2A3B8F;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1);
}

.field-input :deep(.el-input__wrapper.is-focus) {
  border-color: #2A3B8F;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1);
}

.field-input :deep(.el-input__inner) {
  color: #1a1a1a;
  font-size: 0.875rem;
}

.field-input :deep(.el-input__inner::placeholder) {
  color: #9ca3af;
}

.field-input :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  color: #1a1a1a;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.field-input :deep(.el-textarea__inner:hover) {
  border-color: #2A3B8F;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1);
}

.field-input :deep(.el-textarea__inner:focus) {
  border-color: #2A3B8F;
  box-shadow: 0 0 0 3px rgba(42, 59, 143, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .fields-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .section-title {
    margin-bottom: 1rem;
  }
  
  .section-title h3 {
    font-size: 1.125rem;
  }
}
</style>