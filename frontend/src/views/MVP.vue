<template>
  <div class="mvp-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">智能文档处理系统</h1>
        

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
              'completed': currentStep > index
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
                  :disabled="true"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    测试报告上传暂未开放
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      功能未开发：当前仅支持申请书文件用于AI提取
                    </div>
                  </template>
                </el-upload>
              </div>
            </div>
            <div class="step-actions" v-if="!applicationFiles.length || !aiExtractionResult">
              <el-button 
                class="manual-input-btn"
                size="large"
                @click="skipToManualEdit"
              >
                <el-icon style="margin-right: 8px;"><EditPen /></el-icon>
                不上传文档，手动输入
              </el-button>
            </div>

          </div>   <!-- 步骤2: 信息编辑 -->
          <div v-if="currentStep === 1" class="step-panel">
            <div class="panel-header">
              <div class="header-content">
                <div class="header-left">
                  <h2>信息确认与编辑</h2>
                  <p>请确认并完善提取的信息</p>
                </div>
                <div class="header-right">
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
                label-width="280px"
                class="certification-form"
              >
                <!-- 重要日期信息 -->
                <el-divider content-position="left">重要日期</el-divider>
                
                <!-- 批准日期 -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="批准日期 (Approval Date)" prop="approval_date">
                      <el-date-picker
                        v-model="formData.approval_date"
                        type="date"
                        placeholder="选择批准日期"
                        style="width: 100%"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 测试日期 -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="测试日期 (Test Date)" prop="test_date">
                      <el-date-picker
                        v-model="formData.test_date"
                        type="date"
                        placeholder="选择测试日期"
                        style="width: 100%"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 报告日期 -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="报告日期 (Report Date)" prop="report_date">
                      <el-date-picker
                        v-model="formData.report_date"
                        type="date"
                        placeholder="选择报告日期"
                        style="width: 100%"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 基础信息 -->
                <el-divider content-position="left">基础信息</el-divider>
                
                <!-- 报告号 (Report No.) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="报告号 (Report No.)" prop="report_no">
                      <el-input v-model="formData.report_no" placeholder="请输入报告号" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 选择公司 (Company) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="选择公司 (Company)" prop="company_id">
                      <el-select 
                        v-model="formData.company_id" 
                        placeholder="请选择公司"
                        @change="handleCompanyChange"
                        style="width: 100%"
                      >
                        <el-option 
                          v-for="company in companies" 
                          :key="company.id" 
                          :label="company.name" 
                          :value="company.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 公司地址 (Company Address) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="公司地址 (Company Address)" prop="company_address">
                      <el-input 
                        v-model="formData.company_address" 
                        placeholder="请输入公司地址（会自动从选择的公司填充）"
                        type="textarea"
                        :rows="3"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 商标名称或图案 (Trade Names or Marks) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="商标名称或图案 (Trade Names or Marks)">
                      <TradeInfoEditor 
                        v-model:trade-names-text="formData.trade_names"
                        v-model:trade-marks="formData.trade_marks"
                        :readonly-company-data="readonlyCompanyData"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 批准号 (Approval No.) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="批准号 (Approval No.)" prop="approval_no">
                      <el-input v-model="formData.approval_no" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 信息文件夹号 (Information Folder No.) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="信息文件夹号 (Information Folder No.)" prop="information_folder_no">
                      <el-input v-model="formData.information_folder_no" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 安全等级 (Safety Class) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="安全等级 (Safety Class)" prop="safety_class">
                      <el-input v-model="formData.safety_class" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 玻璃板描述 (Pane Description) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="玻璃板描述 (Pane Description)" prop="pane_desc">
                      <el-input v-model="formData.pane_desc" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 玻璃层数 (Glass Layers) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="玻璃层数 (Glass Layers)" prop="glass_layers">
                      <el-input v-model="formData.glass_layers" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层数 (Interlayer Layers) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="夹层数 (Interlayer Layers)" prop="interlayer_layers">
                      <el-input v-model="formData.interlayer_layers" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 风窗厚度 (Windscreen Thickness) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="风窗厚度 (Windscreen Thickness)" prop="windscreen_thick">
                      <el-input v-model="formData.windscreen_thick" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层厚度 (Interlayer Thickness) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="夹层厚度 (Interlayer Thickness)" prop="interlayer_thick">
                      <el-input v-model="formData.interlayer_thick" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 玻璃处理 (Glass Treatment) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="玻璃处理 (Glass Treatment)" prop="glass_treatment">
                      <el-input v-model="formData.glass_treatment" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层类型 (Interlayer Type) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="夹层类型 (Interlayer Type)" prop="interlayer_type">
                      <el-input v-model="formData.interlayer_type" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 涂层类型 (Coating Type) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="涂层类型 (Coating Type)" prop="coating_type">
                      <el-input v-model="formData.coating_type" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 涂层厚度 (Coating Thickness) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="涂层厚度 (Coating Thickness)" prop="coating_thick">
                      <el-input v-model="formData.coating_thick" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 材料性质 (Material Nature) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="材料性质 (Material Nature)" prop="material_nature">
                      <el-input v-model="formData.material_nature" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 涂层颜色 (Coating Color) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="涂层颜色 (Coating Color)" prop="coating_color">
                      <el-input v-model="formData.coating_color" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 玻璃颜色选择 (Glass Color Choice) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="玻璃颜色选择 (Glass Color Choice)" prop="glass_color_choice">
                      <el-input v-model="formData.glass_color_choice" placeholder="例如: colourless/tinted, tinted, colourless" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 导体选择 (Conductors Choice) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="导体选择 (Conductors Choice)" prop="conductors_choice">
                      <el-checkbox-group v-model="formData.conductors_choice">
                        <el-checkbox label="yes_struck">有导体</el-checkbox>
                        <el-checkbox label="no_struck">无导体</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 不透明/模糊选择 (Opaque/Obscure Choice) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="不透明/模糊选择 (Opaque/Obscure Choice)" prop="opaque_obscure_choice">
                      <el-checkbox-group v-model="formData.opaque_obscure_choice">
                        <el-checkbox label="yes_struck">有不透明/模糊</el-checkbox>
                        <el-checkbox label="no_struck">无不透明/模糊</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层相关选择 (Interlayer Options) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="夹层相关选择 (Interlayer Options)">
                      <el-checkbox v-model="formData.interlayer_total">总夹层 (Total Interlayer)</el-checkbox>
                      <el-checkbox v-model="formData.interlayer_partial">部分夹层 (Partial Interlayer)</el-checkbox>
                      <el-checkbox v-model="formData.interlayer_colourless">无色夹层 (Colourless Interlayer)</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 备注 (Remarks) -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="备注 (Remarks)" prop="remarks">
                      <el-input 
                        v-model="formData.remarks" 
                        type="textarea" 
                        :rows="2"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

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
                      <el-form-item :label="`车辆制造商 (Vehicle Manufacturer)`" :prop="`vehicles.${index}.veh_mfr`">
                        <el-input v-model="vehicle.veh_mfr" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`车辆类型 (Vehicle Type)`" :prop="`vehicles.${index}.veh_type`">
                        <el-input v-model="vehicle.veh_type" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`车辆类别 (Vehicle Category)`" :prop="`vehicles.${index}.veh_cat`">
                        <el-input v-model="vehicle.veh_cat" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`开发区域 (Development Area)`" :prop="`vehicles.${index}.dev_area`">
                        <el-input v-model="vehicle.dev_area" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`段高度 (Segment Height)`" :prop="`vehicles.${index}.seg_height`">
                        <el-input v-model="vehicle.seg_height" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`曲率半径 (Curvature Radius)`" :prop="`vehicles.${index}.curv_radius`">
                        <el-input v-model="vehicle.curv_radius" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`安装角度 (Installation Angle)`" :prop="`vehicles.${index}.inst_angle`">
                        <el-input v-model="vehicle.inst_angle" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`座椅角度 (Seat Angle)`" :prop="`vehicles.${index}.seat_angle`">
                        <el-input v-model="vehicle.seat_angle" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item :label="`参考点坐标 (Reference Point Coordinates)`" :prop="`vehicles.${index}.rpoint_coords`">
                        <el-input v-model="vehicle.rpoint_coords" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item :label="`开发描述 (Development Description)`" :prop="`vehicles.${index}.dev_desc`">
                        <el-input v-model="vehicle.dev_desc" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </el-form>
            </div>

            <div class="step-actions">
              <el-button @click="currentStep = 0">上一步</el-button>
              <el-button 
                type="primary" 
                @click="saveFormData"
                :loading="saving"
              >
                保存并继续
              </el-button>
            </div>
          </div>
          <!-- 步骤3: 文档生成 -->
          <div v-if="currentStep === 2" class="step-panel">
            <div class="panel-header">
              <h2>生成交付文档</h2>
              <p>根据填写的信息生成最终文档</p>
            </div>
            
            <div class="generation-section">
              <div class="generate-grid" v-if="!generating && !generatingAll">
                <div class="left-pane">
                  <!-- 文档类型选择（并列） -->
                  <div class="doc-type-selection">
                    <h3>选择文档类型</h3>
                    <el-radio-group v-model="selectedDocType" class="doc-type-group">
                      <el-radio-button label="IF">IF 文档</el-radio-button>
                      <el-radio-button label="CERT">CERT 证书</el-radio-button>
                      <el-radio-button label="OTHER">OTHER 文档</el-radio-button>
                      <el-radio-button label="TR">TR 测试报告</el-radio-button>
                      <el-radio-button label="RCS">RCS 审查控制表</el-radio-button>
                      <el-radio-button label="TM">TM 测试记录</el-radio-button>
                      <el-radio-button label="PM">PM 项目管理表</el-radio-button>
                    </el-radio-group>
                  </div>

                  <!-- 格式选择 -->
                  <div class="format-selection">
                    <h3>选择输出格式</h3>
                    <div v-if="generationResult && generationResult.filename && !generationResult.generated_files" class="format-tip">
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
                  </div>

                  <!-- 生成按钮区域 -->
                  <div class="generate-actions">
                    <div class="button-group">
                      <el-button 
                        type="primary" 
                        size="large"
                        @click="generateSelected"
                        :loading="generating"
                        class="generate-single-btn"
                      >
                        <el-icon><Download /></el-icon>
                        生成 {{ docTypeDisplayName }}
                      </el-button>
                      
                      <el-button 
                        type="success" 
                        size="large"
                        @click="generateAllDocuments"
                        :loading="generatingAll"
                        class="generate-all-btn"
                      >
                        <el-icon><Plus /></el-icon>
                        生成所有文档
                      </el-button>
                    </div>
                    
                  <div class="generate-tips">
                    <el-alert
                      title="生成说明"
                      type="info"
                      :closable="false"
                      show-icon
                      class="generate-info"
                    >
                      <template #default>
                        <p><strong>单文档生成:</strong> 只生成当前选择的文档类型</p>
                        <p><strong>批量生成:</strong> 一次性生成所有7种文档类型，提高效率</p>
                        <p><strong>支持格式:</strong> Word (.docx) 和 PDF (.pdf)</p>
                      </template>
                    </el-alert>
                  </div>
                </div>
                </div>

                <!-- 右侧预览面板 -->
                <div class="right-pane">
                  <div class="preview-card">
                    <div class="preview-header">生成信息预览</div>
                    <ul class="meta-list">
                      <li>
                        <span>文档类型</span>
                        <strong>{{ docTypeDisplayName }}</strong>
                      </li>
                      <li>
                        <span>文件名预览</span>
                        <strong>{{ filenamePreview }}</strong>
                      </li>
                      <li>
                        <span>会话ID</span>
                        <strong>{{ sessionId || '未生成' }}</strong>
                      </li>
                    </ul>
                    <div class="tips" v-if="selectedFormat === 'pdf'">
                      说明：PDF转换需要安装 LibreOffice。
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="generating || generatingAll" class="generation-loading">
                <el-progress type="circle" :percentage="generationProgress" />
                <p v-if="generatingAll">正在生成所有文档，请稍候...</p>
                <p v-else>正在生成{{ docTypeDisplayName }}，请稍候...</p>
              </div>
              
              <div v-if="generationResult && !generating && !generatingAll" class="generation-result">
                <h3 v-if="generationResult.generated_files">
                  <span v-if="generationResult.total_success > 0 && generationResult.total_failed > 0">
                    批量文档部分生成成功
                  </span>
                  <span v-else-if="generationResult.total_success > 0">
                    批量文档生成成功
                  </span>
                  <span v-else>
                    批量文档生成失败
                  </span>
                </h3>
                <h3 v-else>文档生成成功</h3>
                
                <!-- 批量生成结果 -->
                <div v-if="generationResult.generated_files && Array.isArray(generationResult.generated_files)" class="batch-result">
                  <div class="result-summary">
                    <p><strong>成功生成:</strong> {{ generationResult.total_success || 0 }} 个文档</p>
                    <p v-if="(generationResult.total_failed || 0) > 0"><strong>失败:</strong> {{ generationResult.total_failed || 0 }} 个文档</p>
                  </div>
                  
                  <div class="generated-files-list" v-if="generationResult.generated_files && generationResult.generated_files.length > 0">
                    <div class="files-header">
                      <h4>生成的文件:</h4>
                      <el-button 
                        type="success" 
                        size="large"
                        @click="downloadAllFiles"
                        class="download-all-btn"
                        :disabled="!generationResult.generated_files || generationResult.generated_files.length === 0"
                      >
                        <el-icon><Download /></el-icon>
                        批量下载 ({{ (generationResult.generated_files && generationResult.generated_files.length) || 0 }}个文档)
                      </el-button>
                    </div>
                    <div class="files-grid">
                      <div 
                        v-for="(file, index) in generationResult.generated_files" 
                        :key="index"
                        class="file-item"
                      >
                        <div class="file-info">
                          <span class="file-name">{{ file.filename }}</span>
                          <span class="file-type">{{ file.type }}</span>
                        </div>
                        <el-button 
                          type="primary" 
                          size="small"
                          @click="downloadSpecificFile(file)"
                        >
                          <el-icon><download /></el-icon>
                          下载
                        </el-button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 失败文档信息 -->
                  <div v-if="generationResult.failed_documents && generationResult.failed_documents.length > 0" class="failed-documents">
                    <h4>生成失败的文档 ({{ generationResult.failed_documents.length }} 个):</h4>
                    <div class="failed-list">
                      <div 
                        v-for="(failed, index) in generationResult.failed_documents" 
                        :key="index"
                        class="failed-item"
                      >
                        <div class="failed-info">
                          <span class="failed-type">{{ failed.type }}</span>
                          <span class="failed-error">{{ failed.error }}</span>
                        </div>
                        <el-button 
                          type="warning" 
                          size="small"
                          @click="retryGenerateDocument(failed.type)"
                          class="retry-btn"
                        >
                          <el-icon><Refresh /></el-icon>
                          重试
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 单个文档结果 -->
                <div v-else class="single-result">
                  <div class="result-info">
                    <p><strong>文件名:</strong> {{ generationResult.filename || '未知' }}</p>
                    <p><strong>格式:</strong> {{ (generationResult.filename && generationResult.filename.endsWith('.pdf')) ? 'PDF' : 'Word' }}</p>
                    <p><strong>生成时间:</strong> {{ new Date().toLocaleString() }}</p>
                  </div>
                  <div class="download-section">
                    <el-button 
                      type="primary" 
                      size="large"
                      @click="downloadDocument"
                    >
                      <el-icon><download /></el-icon>
                      下载文档
                    </el-button>
                  </div>
                </div>
              </div>
              
              <!-- 已生成文档列表 -->
              <div v-if="generatedDocuments.length > 1 && !generating && !generatingAll" class="generated-documents">
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
              <el-button @click="currentStep = 1">上一步</el-button>
              <el-button 
                type="primary" 
                :disabled="!generationResult || generating || generatingAll"
                @click="finishProcess"
              >
                完成
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 苹果风格确认对话框 -->
    <AppleStyleConfirm
      v-model:visible="showCompanyConfirm"
      :company-name="pendingCompanyName"
      :company-address="pendingCompanyAddress"
      :additional-info="pendingCompanyAdditionalInfo"
      @confirm="handleCompanyConfirm"
      @cancel="handleCompanyCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { Delete, Document, Download, Plus, UploadFilled, Refresh,  EditPen } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { computed, reactive, ref, onMounted, nextTick } from 'vue'
import { mvpAPI } from '../api/mvp'
import { companyAPI, type Company } from '../api/company'
import TradeInfoEditor from '../components/TradeInfoEditor.vue'
import AppleStyleConfirm from '../components/AppleStyleConfirm.vue'

// 步骤定义
const steps = [
  { label: '上传文档' },
  { label: '信息编辑' },
  { label: '生成文档' }
]

// 响应式数据
const currentStep = ref(0)
const sessionId = ref('')


// 文件上传相关
const applicationFiles = ref<any[]>([])
const reportFiles = ref<any[]>([])

// 信息提取相关（已废弃，现在使用AI提取）
const extractionResult = ref<any>(null)

// AI提取相关变量
const aiExtracting = ref(false)
const aiExtractionResult = ref<any>(null)

// 表单相关
const formRef = ref()
const saving = ref(false)

// 公司相关
const companies = ref<Company[]>([])
const loadingCompanies = ref(false)
const selectedCompanyAddress = ref('')
const readonlyCompanyData = ref<{ trade_names?: string[], trade_marks?: string[] } | null>(null)

// 苹果风格确认对话框相关
const showCompanyConfirm = ref(false)
const pendingCompanyName = ref('')
const pendingCompanyAddress = ref('')
const pendingCompanyAdditionalInfo = ref<any>(null)
const companyConfirmPromise = ref<{ resolve: (value: boolean) => void } | null>(null)
const formData = reactive<{[key: string]: any}>({
  // 基础信息
  title: '',
  company_address: '',              // 公司地址
  trade_names: '',                  // 商标名称（分号分隔的字符串）
  trade_marks: [] as string[],      // 商标图片URL数组
  
  // 新增日期字段
  approval_date: '',                // 批准日期
  test_date: '',                    // 测试日期
  report_date: '',                  // 报告日期
  
  // 核心字段 - 与后端AI提取格式保持一致
  approval_no: '',                    // 批准号
  information_folder_no: '',          // 信息文件夹号 (与后端字段名一致)
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
  glass_color_choice: '',             // 玻璃颜色选择 (字符串格式)
  coating_color: '',                  // 涂层颜色
  
  // 夹层相关选择
  interlayer_total: false,               // 总夹层
  interlayer_partial: false,             // 部分夹层
  interlayer_colourless: false,          // 无色夹层
  
  // 选择项数组
  conductors_choice: [],                 // 导体选择 (数组格式)
  opaque_obscure_choice: [],             // 不透明/模糊选择 (数组格式)
  
  remarks: '',                        // 备注
  
  // 报告号和公司信息
  report_no: '',                        // 报告号
  company_id: null,                     // 公司ID
  company_name: '',                     // 公司名称（兼容旧数据）
  
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


// 设置默认日期（北京时间）
const setDefaultDates = () => {
  const today = new Date()
  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0] // YYYY-MM-DD格式
  }
  
  // 报告日期 = 今天
  const reportDate = new Date(today)
  formData.report_date = formatDate(reportDate)
  
  // 测试日期 = 今天-7天
  const testDate = new Date(today)
  testDate.setDate(testDate.getDate() - 7)
  formData.test_date = formatDate(testDate)
  
  // 批准日期 = 今天-14天
  const approvalDate = new Date(today)
  approvalDate.setDate(approvalDate.getDate() - 14)
  formData.approval_date = formatDate(approvalDate)
}

// 日期验证函数
const validateDateOrder = (rule: any, value: any, callback: any) => {
  const approvalDate = new Date(formData.approval_date)
  const testDate = new Date(formData.test_date)
  const reportDate = new Date(formData.report_date)
  
  if (formData.approval_date && formData.test_date && formData.report_date) {
    if (approvalDate > testDate) {
      callback(new Error('批准日期不能晚于测试日期'))
    } else if (testDate > reportDate) {
      callback(new Error('测试日期不能晚于报告日期'))
    } else if (approvalDate > reportDate) {
      callback(new Error('批准日期不能晚于报告日期'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

// 表单验证规则
const formRules = {
  report_no: [
    { required: true, message: '请输入报告号', trigger: 'blur' }
  ],
  company_id: [
    { required: true, message: '请选择公司', trigger: 'change' }
  ],
  approval_date: [
    { required: true, message: '请选择批准日期', trigger: 'change' },
    { validator: validateDateOrder, trigger: 'change' }
  ],
  test_date: [
    { required: true, message: '请选择测试日期', trigger: 'change' },
    { validator: validateDateOrder, trigger: 'change' }
  ],
  report_date: [
    { required: true, message: '请选择报告日期', trigger: 'change' },
    { validator: validateDateOrder, trigger: 'change' }
  ],
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
  glass_color_choice: [
    { 
      required: true, 
      message: '请输入玻璃颜色选择', 
      trigger: 'blur' 
    }
  ],
  conductors_choice: [
    { 
      required: true, 
      type: 'array',
      min: 1,
      message: '请至少选择一个导体选项', 
      trigger: 'change' 
    }
  ],
  opaque_obscure_choice: [
    { 
      required: true, 
      type: 'array',
      min: 1,
      message: '请至少选择一个不透明/模糊选项', 
      trigger: 'change' 
    }
  ],
  remarks: [
    { required: false, message: '请输入备注', trigger: 'blur' }
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
const generatingAll = ref(false)
const generationProgress = ref(0)
const generationResult = ref<any>(null)
const generatedDocuments = ref<any[]>([])
const selectedFormat = ref('docx')
const selectedDocType = ref<'IF'|'CERT'|'OTHER'|'TR'|'RCS'|'TM'|'PM'>('IF')

const docTypeDisplayName = computed(() => {
  const map: Record<string, string> = {
    IF: 'IF',
    CERT: 'CERT 证书文档',
    OTHER: 'OTHER 文档',
    TR: 'TR 测试报告',
    RCS: 'Review Control Sheet 审查控制表',
    TM: 'TM 测试记录',
    PM: '项目管理表'
  }
  const baseName = map[selectedDocType.value] || selectedDocType.value
  return `${baseName} ${selectedFormat.value === 'pdf' ? 'PDF' : 'Word'}`
})

const filenamePreview = computed(() => {
  const prefixMap: Record<string, string> = {
    IF: 'IF-', CERT: 'CERT-', OTHER: 'OTHER-', TR: 'TR-', RCS: 'Review Control Sheet V7 ', TM: 'TM-', PM: 'PM-'
  }
  const prefix = prefixMap[selectedDocType.value]
  const safeNo = (formData.approval_no || 'TEST')
    .replace(/[^a-zA-Z0-9]/g, '-')
    .replace(/-+/g, '-')
    .replace(/(^-|-$)/g, '')
  const ext = selectedFormat.value === 'pdf' ? '.pdf' : '.docx'
  return `${prefix}${safeNo}${ext}`
})

// 注意：canProceedToNext 计算属性已被移除，因为不再需要手动上传按钮

// 方法
const goToStep = (step: number) => {
  if (step <= currentStep.value) {
    currentStep.value = step
  }
}



const handleApplicationChange = (file: any) => {
  applicationFiles.value = [file]
  aiExtractionResult.value = null
  
  // 恢复自动AI提取，但使用正确的API
  if (file.raw) {
    uploadAndExtract(file)
  }
}

const handleReportChange = (_file: any) => {
  ElMessage.info('测试报告上传功能未开发，已禁用')
}

// 直接进行AI解析（包含文件上传）
const uploadAndExtract = async (file: any) => {
  if (!file?.raw) {
    ElMessage.warning('文件无效')
    return
  }

  // 设置AI提取状态
  aiExtracting.value = true
  
  // 显示全局loading
  const loadingInstance = ElLoading.service({
    lock: true,
    text: 'AI正在分析申请书，请耐心等待...（通常需要10-60秒）',
    background: 'rgba(0, 0, 0, 0.7)',
    spinner: 'el-icon-loading'
  })
  
  try {
    // 直接调用AI提取API，后端会自动处理文件上传和AI解析
    const response = await mvpAPI.aiExtract(file.raw)
    
    if (response.success) {
      // 直接获取AI提取结果
      aiExtractionResult.value = response.data
      
      
      // 自动应用AI结果到表单
      await applyAIResult()
      
      // 自动跳转到信息编辑步骤
      currentStep.value = 1
      ElMessage.success('AI解析完成，已自动应用结果并跳转到信息编辑步骤')
    } else {
      ElMessage.error(response.message || 'AI解析失败')
    }
  } catch (error: any) {
    console.error('AI解析失败:', error)
    const errorMessage = error.message || 'AI解析失败'
    ElMessage.error(errorMessage)
  } finally {
    // 关闭全局loading
    loadingInstance.close()
    aiExtracting.value = false
  }
}

// 注意：aiExtract 函数已被移除，现在只使用自动触发的 uploadAndExtract 函数


const fillFormData = (data: any) => {
  // 填充基础字段包括日期
  if (data.approval_date) formData.approval_date = data.approval_date
  if (data.test_date) formData.test_date = data.test_date
  if (data.report_date) formData.report_date = data.report_date
  
  // 填充核心字段
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
    // 转换数据为后端需要的格式
    const processedFormData = {
      ...formData,
      // 处理导体选择：如果选择了两个，转换为"both_visible"；如果只选择一个，保持原值
      conductors_choice: formData.conductors_choice.length === 2 
        ? 'both_visible' 
        : formData.conductors_choice[0] || 'yes',
      // 处理不透明选择
      opaque_obscure_choice: formData.opaque_obscure_choice.length === 2 
        ? 'both_visible' 
        : formData.opaque_obscure_choice[0] || 'yes'
    }
    
    // 保存表单数据 - 后端会自动生成session_id
    const response = await mvpAPI.saveFormData({
      form_data: processedFormData
    })
    
    // 拦截器已经返回了业务数据，直接使用
    if (response.success) {
      // 从后端响应中获取生成的session_id
      if (response.data?.session_id) {
        sessionId.value = response.data.session_id
        console.log('从后端获取生成的session_id:', sessionId.value)
      }
      ElMessage.success('表单数据保存成功')
      currentStep.value = 2
      // 移除自动生成文档的调用，让用户手动选择格式并生成
      // await generateDocuments()
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('表单数据保存失败')
  } finally {
    saving.value = false
  }
}

const generateSingleDocument = async (type: 'if'|'cert'|'other'|'tr'|'rcs'|'tm'|'pm') => {
  // 检查是否有session_id（应该由后端在save_form_data时生成）
  if (!sessionId.value) {
    ElMessage.warning('请先保存表单数据以获取session_id')
    return
  }

  generating.value = true
  generationProgress.value = 0

  // 模拟进度 - 根据生成阶段调整速度
  const progressInterval = setInterval(() => {
    if (generationProgress.value < 90) {
      // 模拟文档生成的不同阶段
      let increment = 0
      if (generationProgress.value < 20) {
        increment = 10 + Math.floor(Math.random() * 4)  // 10-13，准备阶段快速
      } else if (generationProgress.value < 50) {
        increment = 6 + Math.floor(Math.random() * 4)   // 6-9，模板处理阶段
      } else if (generationProgress.value < 75) {
        increment = 4 + Math.floor(Math.random() * 3)   // 4-6，内容生成阶段
      } else {
        increment = 2 + Math.floor(Math.random() * 3)   // 2-4，最终处理阶段
      }
      generationProgress.value = Math.min(generationProgress.value + increment, 90)
    }
  }, 300 + Math.floor(Math.random() * 100))  // 300-400ms，随机化更新频率

  try {
    let response
    const requestData = {
      session_id: sessionId.value,
      output_format: selectedFormat.value,
      format: selectedFormat.value // 为了兼容其他API的格式参数
    }

    // 根据文档类型调用对应的API
    if (type === 'if') {
      response = await mvpAPI.generateIF(requestData)
    } else if (type === 'cert') {
      response = await mvpAPI.generateCert(requestData)
    } else if (type === 'other') {
      response = await mvpAPI.generateOther(requestData)
    } else if (type === 'tr') {
      response = await mvpAPI.generateTR(requestData)
    } else if (type === 'rcs') {
      response = await mvpAPI.generateReviewControlSheet(requestData)
    } else if (type === 'tm') {
      response = await mvpAPI.generateTM(requestData)
    } else if (type === 'pm') {
      response = await mvpAPI.generateProjectSheet(requestData)
    }
    
    // 拦截器已经返回了业务数据，直接使用
    if (response?.success) {
      const result = response.data
      generationResult.value = result
      // 添加到已生成文档列表
      generatedDocuments.value.push({
        ...result,
        format: (result.filename && result.filename.endsWith('.pdf')) ? 'PDF' : 'Word',
        generatedTime: new Date().toLocaleString()
      })
      generationProgress.value = 100
      ElMessage.success(`${docTypeDisplayName.value}生成成功`)
    } else {
      ElMessage.error(response?.message || '文档生成失败')
    }
  } catch (error) {
    console.error('生成文档失败:', error)
    ElMessage.error('生成文档失败')
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

const downloadSpecificFile = async (file: any) => {
  if (file.download_url) {
    window.open(`http://localhost:5000${file.download_url}`, '_blank')
  }
}

const downloadAllFiles = async () => {
  if (generationResult.value?.generated_files && Array.isArray(generationResult.value.generated_files)) {
    // 依次下载所有文件，添加延迟以避免浏览器阻止多个下载
    for (let i = 0; i < generationResult.value.generated_files.length; i++) {
      const file = generationResult.value.generated_files[i]
      if (file.download_url) {
        setTimeout(() => {
          window.open(`http://localhost:5000${file.download_url}`, '_blank')
        }, i * 500) // 每个文件间隔500ms
      }
    }
    ElMessage.success(`开始下载 ${generationResult.value.generated_files.length} 个文档`)
  }
}

const retryGenerateDocument = async (docType: string) => {
  ElMessage.info(`正在重试生成 ${docType} 文档...`)
  // 这里可以实现单个文档的重新生成逻辑
  // 暂时提示用户可以重新点击"生成所有文档"
  ElMessage.warning('请重新点击"生成所有文档"按钮进行重试')
}

const generateAllDocuments = async () => {
  // 检查是否有session_id（应该由后端在save_form_data时生成）
  if (!sessionId.value) {
    ElMessage.warning('请先保存表单数据以获取session_id')
    return
  }

  generatingAll.value = true
  generationProgress.value = 0

  // 模拟进度 - 批量生成使用更平滑的进度
  const progressInterval = setInterval(() => {
    if (generationProgress.value < 90) {
      // 批量生成进度更平滑，模拟多个文档的处理
      let increment = 0
      if (generationProgress.value < 25) {
        increment = 5 + Math.floor(Math.random() * 4)   // 5-8，初始化阶段
      } else if (generationProgress.value < 50) {
        increment = 4 + Math.floor(Math.random() * 3)   // 4-6，第一个文档
      } else if (generationProgress.value < 70) {
        increment = 3 + Math.floor(Math.random() * 3)   // 3-5，中间文档
      } else if (generationProgress.value < 85) {
        increment = 2 + Math.floor(Math.random() * 3)   // 2-4，后期文档
      } else {
        increment = 1 + Math.floor(Math.random() * 2)   // 1-2，最后处理
      }
      generationProgress.value = Math.min(generationProgress.value + increment, 90)
    }
  }, 400 + Math.floor(Math.random() * 150))  // 400-550ms，随机化更新频率

  try {
    let response
    response = await mvpAPI.generateDocuments({ 
      session_id: sessionId.value,
      output_format: selectedFormat.value
    })
    
    // 拦截器已经返回了业务数据，直接使用
    const result = response.data
    
    console.log('批量生成响应数据:', response)
    console.log('解析的结果:', result)
    
    if (response.success || (result && result.generated_files && result.generated_files.length > 0)) {
      console.log('设置生成结果:', result)
      // 确保结果对象有必要的属性
      const safeResult = {
        ...result,
        total_success: result.total_success || 0,
        total_failed: result.total_failed || 0,
        generated_files: result.generated_files || [],
        failed_documents: result.failed_documents || []
      }
      generationResult.value = safeResult
      
      // 处理批量生成的文档
      if (result.generated_files && Array.isArray(result.generated_files)) {
        // 批量生成，添加所有成功生成的文档到列表
        result.generated_files.forEach((file: any) => {
          generatedDocuments.value.push({
            ...file,
            format: (file.filename && file.filename.endsWith('.pdf')) ? 'PDF' : 'Word',
            generatedTime: new Date().toLocaleString()
          })
        })
        
        // 显示成功信息
        if (result.total_success > 0) {
          ElMessage.success(`成功生成 ${result.total_success} 个文档`)
        }
        
        // 如果有失败的文档，显示警告
        if (result.failed_documents && result.failed_documents.length > 0) {
          ElMessage.warning(`${result.failed_documents.length} 个文档生成失败`)
          
          // 在控制台显示详细的失败信息
          console.log('失败的文档详情:', result.failed_documents)
        }
        
        // 如果所有文档都失败了
        if (result.total_success === 0) {
          ElMessage.error('所有文档生成失败')
        }
      } else if (result.filename) {
        // 单个文档生成成功
        generatedDocuments.value.push({
          ...result,
          format: result.filename.endsWith('.pdf') ? 'PDF' : 'Word',
          generatedTime: new Date().toLocaleString()
        })
        ElMessage.success('文档生成成功')
      }
      
      generationProgress.value = 100
    } else {
      // 完全失败的情况
      generationResult.value = result
      ElMessage.error(response.message || '文档生成失败')
      
      // 即使失败也显示失败信息，以便用户了解具体原因
      if (result && result.failed_documents && result.failed_documents.length > 0) {
        console.log('所有文档生成失败的详情:', result.failed_documents)
      }
    }
  } catch (error) {
    console.error('生成所有文档失败:', error)
    ElMessage.error('生成所有文档失败')
  } finally {
    generatingAll.value = false
    clearInterval(progressInterval)
  }
}



const generateSelected = async () => {
  const typeMap: Record<string, 'if'|'cert'|'other'|'tr'|'rcs'|'tm'|'pm'> = {
    IF: 'if', CERT: 'cert', OTHER: 'other', TR: 'tr', RCS: 'rcs', TM: 'tm', PM: 'pm'
  }
  await generateSingleDocument(typeMap[selectedDocType.value])
}

const downloadSpecificDocument = (doc: any) => {
  if (doc.download_url) {
    window.open(`http://localhost:5000${doc.download_url}`, '_blank')
  }
}

// 一键生成示例数据
const generateTestData = async () => {
  
  // 确保公司数据已加载
  if (companies.value.length === 0) {
    await loadCompanies()
  }
  
  // 选择第一个公司作为默认值
  const defaultCompany = companies.value[0]
  
  if (!defaultCompany) {
    ElMessage.error('没有可用的公司数据，请先添加公司信息')
    return
  }
  
      // 生成示例数据
  Object.assign(formData, {
    // 基础信息
    title: '示例申请书',
    
    // 报告号和公司信息
    report_no: "CSR043",
    company_id: defaultCompany?.id || null,
    company_name: defaultCompany?.name || "示例企业",
    company_address: defaultCompany?.address || "示例公司地址",
    trade_names: defaultCompany?.trade_names && defaultCompany.trade_names.length > 0 
      ? defaultCompany.trade_names.join(';') 
      : "示例商标1;示例商标2",
    trade_marks: defaultCompany?.trade_marks || [],
    
    // 核心字段
    approval_no: "E4*43R01/12*2812*00",
    information_folder_no: "GZFUYAO-L4.76~5.09mm",
    safety_class: "Ordinary laminated-glass windscreen",
    pane_desc: "Please refer to Appendix 3 of ECE R43",
    glass_layers: "2",
    interlayer_layers: "1",
    windscreen_thick: "4.76~5.09 mm",
    interlayer_thick: "0.76~1.09 mm",
    glass_treatment: "not applicable",
    interlayer_type: "PVB (Sound insulation HUD)",
    coating_type: "not applicable",
    coating_thick: "not applicable",
    material_nature: "float",
    coating_color: "not applicable",
    glass_color_choice: "colourless/tinted",
    interlayer_total: true,
    interlayer_partial: true,
    interlayer_colourless: true,
    conductors_choice: ["yes", "no"],
    opaque_obscure_choice: ["yes", "no"],
    remarks: "---",
    
    // 车辆信息
    vehicles: [
      {
        veh_mfr: `GAC Motor Co., Ltd.
GAC AION NEW ENERGY AUTOMOBILE CO., LTD.
`,
        veh_type: "AHT",
        veh_cat: "M1",
        dev_area: "1.58 m²",
        seg_height: "59.2 mm",
        curv_radius: "1071 mm",
        inst_angle: "61.6° ",
        seat_angle: "25°",
        rpoint_coords: "A: 381.213 mm B: ±370 mm C: -871.85 mm",
        dev_desc: "not applicable"
      },
      {
        veh_mfr: "示例制造商2",
        veh_type: "SUV",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "120mm",
        curv_radius: "600mm",
        inst_angle: "50°",
        seat_angle: "35°",
        rpoint_coords: "150,250",
        dev_desc: "示例车辆2的开发描述"
      },
      {
        veh_mfr: "示例制造商2",
        veh_type: "SUV",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "120mm",
        curv_radius: "600mm",
        inst_angle: "50°",
        seat_angle: "35°",
        rpoint_coords: "150,250",
        dev_desc: "示例车辆2的开发描述"
      }
    ]
  })
  
  // 设置公司地址
  selectedCompanyAddress.value = defaultCompany?.address || ""
  
  // 设置只读数据用于TradeInfoEditor组件显示
  readonlyCompanyData.value = {
    trade_names: defaultCompany?.trade_names || [],
    trade_marks: defaultCompany?.trade_marks || []
  }
  
  ElMessage.success('示例数据已生成')
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

// 公司相关方法
const loadCompanies = async () => {
  try {
    loadingCompanies.value = true
    const response = await companyAPI.getAllCompanies()
    
    // getAllCompanies返回格式: { success: boolean, data: Company[] }
    if (response.success && response.data) {
      companies.value = response.data.companies
    } else {
      console.error('API响应格式错误:', response)
      ElMessage.error('加载公司列表失败：响应格式错误')
    }
  } catch (error) {
    console.error('加载公司列表失败:', error)
    ElMessage.error('加载公司列表失败')
  } finally {
    loadingCompanies.value = false
  }
}

const handleCompanyChange = (companyId: number) => {
  const selectedCompany = companies.value.find(c => c.id === companyId)
  if (selectedCompany) {
    // 填充formData中的公司相关字段
    formData.company_name = selectedCompany.name
    formData.company_address = selectedCompany.address || ''
    
    // 将trade_names数组转换为分号分隔的字符串
    formData.trade_names = selectedCompany.trade_names && selectedCompany.trade_names.length > 0 
      ? selectedCompany.trade_names.join(';') 
      : ''
    
    // 直接设置trade_marks数组
    formData.trade_marks = selectedCompany.trade_marks || []
    
    // 同步到显示字段（保持向后兼容）
    selectedCompanyAddress.value = selectedCompany.address || ''
    
    // 设置只读数据用于TradeInfoEditor组件显示
    readonlyCompanyData.value = {
      trade_names: selectedCompany.trade_names || [],
      trade_marks: selectedCompany.trade_marks || []
    }
  } else {
    formData.company_name = ''
    formData.company_address = ''
    formData.trade_names = ''
    formData.trade_marks = []
    selectedCompanyAddress.value = ''
    readonlyCompanyData.value = null
  }
}



// 在组件挂载时加载公司列表和设置默认日期
onMounted(() => {
  loadCompanies()
  setDefaultDates()
})



// 确保表单字段具有安全的默认值，防止渲染异常
const ensureFormDefaults = () => {
  const ensure = (k: keyof typeof formData, v: any) => {
    if (formData[k] === undefined || formData[k] === null) {
      // @ts-ignore
      formData[k] = v
    }
  }

  // 基础与日期
  ensure('approval_date', formData.approval_date ?? '')
  ensure('test_date', formData.test_date ?? '')
  ensure('report_date', formData.report_date ?? '')
  ensure('report_no', formData.report_no ?? '')
  ensure('company_id', formData.company_id ?? '')
  ensure('company_address', formData.company_address ?? '')

  // 兼容 trade_names 既可能是数组也可能是字符串
  if (Array.isArray(formData.trade_names)) {
    // @ts-ignore 将数组转换为分号分隔字符串
    formData.trade_names = formData.trade_names.join(';')
  }
  ensure('trade_names', formData.trade_names ?? '')
  ensure('trade_marks', Array.isArray(formData.trade_marks) ? formData.trade_marks : [])

  // 核心字段
  ensure('approval_no', formData.approval_no ?? '')
  ensure('information_folder_no', formData.information_folder_no ?? '')
  ensure('safety_class', formData.safety_class ?? '')
  ensure('pane_desc', formData.pane_desc ?? '')
  ensure('glass_layers', String(formData.glass_layers ?? ''))
  ensure('interlayer_layers', String(formData.interlayer_layers ?? ''))
  ensure('windscreen_thick', formData.windscreen_thick ?? '')
  ensure('interlayer_thick', formData.interlayer_thick ?? '')
  ensure('glass_treatment', formData.glass_treatment ?? '')
  ensure('interlayer_type', formData.interlayer_type ?? '')
  ensure('coating_type', formData.coating_type ?? '')
  ensure('coating_thick', formData.coating_thick ?? '')
  ensure('material_nature', formData.material_nature ?? '')
  ensure('coating_color', formData.coating_color ?? '')

  // 选择项与布尔值
  ensure('glass_color_choice', typeof formData.glass_color_choice === 'string' ? formData.glass_color_choice : '')
  ensure('conductors_choice', Array.isArray(formData.conductors_choice) ? formData.conductors_choice : [])
  ensure('opaque_obscure_choice', Array.isArray(formData.opaque_obscure_choice) ? formData.opaque_obscure_choice : [])
  ensure('interlayer_total', !!formData.interlayer_total)
  ensure('interlayer_partial', !!formData.interlayer_partial)
  ensure('interlayer_colourless', !!formData.interlayer_colourless)
  ensure('remarks', formData.remarks ?? '')

  // 车辆列表
  ensure('vehicles', (Array.isArray(formData.vehicles) && formData.vehicles.length > 0) ? formData.vehicles : [{
    veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', seg_height: '', curv_radius: '', inst_angle: '', seat_angle: '', rpoint_coords: '', dev_desc: ''
  }])

  // 确保需要的公司列表可用，避免下拉异常（静默处理）
  try {
    if (!companies.value || companies.value.length === 0) {
      // 异步加载但不阻塞
      loadCompanies()
    }
  } catch {}
}

// 处理公司确认事件
const handleCompanyConfirm = () => {
  showCompanyConfirm.value = false
  if (companyConfirmPromise.value) {
    companyConfirmPromise.value.resolve(true)
    companyConfirmPromise.value = null
  }
}

// 处理公司取消事件
const handleCompanyCancel = () => {
  showCompanyConfirm.value = false
  if (companyConfirmPromise.value) {
    companyConfirmPromise.value.resolve(false)
    companyConfirmPromise.value = null
  }
}

// 显示苹果风格的公司确认面板
const showAppleStyleCompanyConfirm = (companyName: string, companyAddress: string, additionalInfo?: any): Promise<boolean> => {
  return new Promise((resolve) => {
    // 设置待确认的公司信息
    pendingCompanyName.value = companyName
    pendingCompanyAddress.value = companyAddress || ''
    pendingCompanyAdditionalInfo.value = additionalInfo
    
    // 保存Promise的resolve函数
    companyConfirmPromise.value = { resolve }
    
    // 显示确认对话框
    showCompanyConfirm.value = true
  })
}

// 智能处理AI提取的公司信息
const handleCompanyInfoFromAI = async (aiCompanyName: string, aiCompanyAddress: string) => {
  if (!aiCompanyName) return
  
  // 确保公司列表已加载
  if (companies.value.length === 0) {
    await loadCompanies()
  }
  
  // 查找是否已存在匹配的公司
  const matchedCompany = companies.value.find(company => 
    company.name.toLowerCase().includes(aiCompanyName.toLowerCase()) ||
    aiCompanyName.toLowerCase().includes(company.name.toLowerCase())
  )
  
  if (matchedCompany) {
    // 找到匹配的公司，自动选择并填充信息
    formData.company_id = matchedCompany.id
    formData.company_name = matchedCompany.name
    formData.company_address = matchedCompany.address || aiCompanyAddress
    
    // 同步其他相关字段
    if (matchedCompany.trade_names && matchedCompany.trade_names.length > 0) {
      formData.trade_names = matchedCompany.trade_names.join(';')
    }
    if (matchedCompany.trade_marks) {
      formData.trade_marks = matchedCompany.trade_marks
    }
    
    // 设置只读数据用于TradeInfoEditor组件显示
    readonlyCompanyData.value = {
      trade_names: matchedCompany.trade_names || [],
      trade_marks: matchedCompany.trade_marks || []
    }
    
    ElMessage.success(`已自动匹配公司: ${matchedCompany.name}`)
  } else {
    // 未找到匹配的公司，显示苹果风格的确认面板
    // 传递AI提取的完整数据作为额外信息
    const shouldAddCompany = await showAppleStyleCompanyConfirm(aiCompanyName, aiCompanyAddress, aiExtractionResult.value)
    
    if (shouldAddCompany) {
      // 用户选择新增公司
      try {
        const newCompany = await addNewCompany(aiCompanyName, aiCompanyAddress)
        if (newCompany) {
          // 新增成功，自动选择新公司
          formData.company_id = newCompany.id
          formData.company_name = newCompany.name
          formData.company_address = newCompany.address
          ElMessage.success(`已新增并选择公司: ${newCompany.name}`)
        }
      } catch (error) {
        console.error('新增公司失败:', error)
        ElMessage.error('新增公司失败，请手动处理')
        // 新增失败，不填充公司信息
        formData.company_name = ''
        formData.company_address = ''
        formData.company_id = null
      }
    } else {
      // 用户选择不新增，不填充公司信息
      ElMessage.info('已跳过公司信息，请手动选择或填写')
      formData.company_name = ''
      formData.company_address = ''
      formData.company_id = null
    }
  }
}

// 新增公司到数据库
const addNewCompany = async (name: string, address: string) => {
  try {
    console.log('🚀 开始创建公司:', { name, address })
    
    const response = await companyAPI.createCompany({
      name: name,
      address: address || '',
      trade_names: [],
      trade_marks: []
    })
    
    console.log('📡 API响应:', response)
    
    // 检查响应结构 - 现在API直接返回业务数据
    console.log('🔍 响应结构分析:', {
      hasResponse: !!response,
      success: response?.success,
      message: response?.message,
      data: response?.data
    })
    
    if (response && response.success) {
      // 新增成功后，重新加载公司列表
      await loadCompanies()
      console.log('✅ 公司创建成功:', response.data)
      return response.data
    } else {
      // 处理业务逻辑错误
      const errorMessage = response?.message || '新增公司失败'
      console.error('❌ 业务逻辑错误:', errorMessage)
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    console.error('❌ 新增公司API调用失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data
    })
    
    // 尝试从错误响应中提取具体错误信息
    let errorMessage = '新增公司失败'
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.message) {
      errorMessage = error.message
    }
    
    throw new Error(errorMessage)
  }
}

const applyAIResult = async () => {
  if (!aiExtractionResult.value) return
  
  const r = aiExtractionResult.value

  // 调试信息：显示AI提取的原始数据
  console.log('🔍 AI提取原始数据:', r)

  // 获取实际的数据内容（可能嵌套在result字段中）
  const data = r.result || r

  // 智能处理公司信息
  await handleCompanyInfoFromAI(data.company_name, data.company_address)

  // 优雅的字段映射：使用对象解构和默认值
  const fieldMappings = {
    // 基础信息
    approval_no: data.approval_no || '',
          information_folder_no: data.information_folder_no || '',
    safety_class: data.safety_class || '',
    pane_desc: data.pane_desc || '',
    trade_names: data.trade_names || '',
    // 注意：company_name 和 company_address 已在上面处理
    
    // 技术规格
    glass_layers: String(data.glass_layers || ''),
    interlayer_layers: String(data.interlayer_layers || ''),
    windscreen_thick: data.windscreen_thick || '',
    interlayer_thick: data.interlayer_thick || '',
    glass_treatment: data.glass_treatment || '',
    interlayer_type: data.interlayer_type || '',
    coating_type: data.coating_type || '',
    coating_thick: data.coating_thick || '',
    material_nature: data.material_nature || '',
    glass_color_choice: data.glass_color_choice || '',
    coating_color: data.coating_color || '',
    remarks: data.remarks || '',
    
    // 选择项数组 - 确保是数组类型
    conductors_choice: Array.isArray(data.conductors_choice) ? data.conductors_choice : [],
    opaque_obscure_choice: Array.isArray(data.opaque_obscure_choice) ? data.opaque_obscure_choice : [],
    
    // 布尔值字段 - 处理字符串和布尔值的转换
    interlayer_total: data.interlayer_total === true || data.interlayer_total === 'true',
    interlayer_partial: data.interlayer_partial === true || data.interlayer_partial === 'true',
    interlayer_colourless: data.interlayer_colourless === true || data.interlayer_colourless === 'true',
    
    // 车辆信息 - 确保是数组类型
    vehicles: Array.isArray(data.vehicles) && data.vehicles.length > 0 ? data.vehicles : [{
      veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', 
      seg_height: '', curv_radius: '', inst_angle: '', 
      seat_angle: '', rpoint_coords: '', dev_desc: ''
    }]
  }

  // 批量更新表单数据
  Object.assign(formData, fieldMappings)

  // 调试信息：显示映射后的表单数据
  console.log('📝 映射后的表单数据:', formData)

  ElMessage.success('AI提取结果已应用到表单')
  currentStep.value = 1
}

const clearAIResult = () => {
  aiExtractionResult.value = null
  ElMessage.info('已清除AI提取结果')
}

const skipToManualEdit = async () => {
  // 停止AI状态并清理结果
  aiExtracting.value = false
  aiExtractionResult.value = null
  
  // 初始化必填/依赖字段，避免渲染异常
  const ensure = (k: keyof typeof formData, v: any) => {
    if (formData[k] === undefined || formData[k] === null) {
      // @ts-ignore
      formData[k] = v
    }
  }
  ensure('approval_date', '')
  ensure('test_date', '')
  ensure('report_date', '')
  ensure('report_no', '')
  ensure('company_id', '')
  ensure('company_address', '')
  ensure('trade_names', '')
  ensure('trade_marks', Array.isArray(formData.trade_marks) ? formData.trade_marks : [])
  ensure('approval_no', '')
  ensure('information_folder_no', '')
  ensure('safety_class', '')
  ensure('pane_desc', '')
  ensure('glass_layers', '')
  ensure('interlayer_layers', '')
  ensure('windscreen_thick', '')
  ensure('interlayer_thick', '')
  ensure('glass_treatment', '')
  ensure('interlayer_type', '')
  ensure('coating_type', '')
  ensure('coating_thick', '')
  ensure('material_nature', '')
  ensure('coating_color', '')
  ensure('glass_color_choice', typeof formData.glass_color_choice === 'string' ? formData.glass_color_choice : '')
  ensure('conductors_choice', Array.isArray(formData.conductors_choice) ? formData.conductors_choice : [])
  ensure('opaque_obscure_choice', Array.isArray(formData.opaque_obscure_choice) ? formData.opaque_obscure_choice : [])
  ensure('interlayer_total', !!formData.interlayer_total)
  ensure('interlayer_partial', !!formData.interlayer_partial)
  ensure('interlayer_colourless', !!formData.interlayer_colourless)
  ensure('remarks', formData.remarks ?? '')
  ensure('vehicles', (Array.isArray(formData.vehicles) && formData.vehicles.length > 0) ? formData.vehicles : [{
    veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', seg_height: '', curv_radius: '', inst_angle: '', seat_angle: '', rpoint_coords: '', dev_desc: ''
  }])

  // 需要公司下拉时，提前拉取，避免选择框报错
  try {
    if (!companies.value || companies.value.length === 0) {
      await loadCompanies()
    }
  } catch {}

  currentStep.value = 1
  await nextTick()
  ElMessage.info('已进入手动输入模式，请填写信息')
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

.generate-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.25rem;
}

.left-pane, .right-pane {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-card {
  background: #fff;
  border: 1px solid #ebedf0;
  border-radius: 14px;
  padding: 1rem 1.25rem;
  text-align: left;
}

.preview-header {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
}

.meta-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.meta-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #eee;
}

.meta-list li:last-child {
  border-bottom: none;
}

.meta-list span {
  color: #6b7280;
}

.meta-list strong {
  color: #111827;
}

.tips {
  margin-top: 0.75rem;
  color: #6b7280;
  font-size: 12px;
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
  margin: 2rem 0;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.generate-single-btn {
  min-width: 160px;
}

.generate-all-btn {
  min-width: 160px;
}

.generate-tips {
  margin-top: 1rem;
}

.generate-info {
  text-align: left;
}

.generate-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* 批量生成结果样式 */
.batch-result {
  text-align: left;
}

.result-summary {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.result-summary p {
  margin: 0.5rem 0;
  color: #065f46;
  font-weight: 500;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.files-header h4 {
  color: #2A3B8F;
  margin: 0;
  font-size: 1rem;
}

.download-all-btn {
  flex-shrink: 0;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: #2A3B8F;
  box-shadow: 0 2px 4px rgba(42, 59, 143, 0.1);
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.file-type {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.failed-documents {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
}

.failed-documents h4 {
  color: #dc2626;
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
}

.failed-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.failed-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #fecaca;
  margin-bottom: 0.5rem;
}

.failed-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.failed-type {
  font-weight: 500;
  color: #dc2626;
  font-size: 0.9rem;
}

.failed-error {
  font-size: 0.8rem;
  color: #991b1b;
  background: #fef2f2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  word-break: break-word;
  line-height: 1.4;
}

.retry-btn {
  margin-left: 1rem;
  flex-shrink: 0;
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

/* 手动输入按钮样式 - 苹果风格 */
.manual-input-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  padding: 12px 24px !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
  position: relative !important;
  overflow: hidden !important;
}

.manual-input-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.manual-input-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

.manual-input-btn:hover::before {
  left: 100%;
}

.manual-input-btn:active {
  transform: translateY(0) !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
}

/* 确保按钮图标和文字颜色一致 */
.manual-input-btn .el-icon {
  color: white !important;
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

.ai-extraction-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #ddd;
  transition: all 0.3s ease;
}

.ai-extraction-options {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.ai-extraction-options .el-button {
  flex: 1;
}

.ai-extraction-status {
  text-align: center;
  padding: 2rem;
}

.ai-extraction-status p {
  margin-top: 1rem;
  color: #606266;
  font-size: 1rem;
}

.ai-extraction-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px dashed #ddd;
  transition: all 0.3s ease;
}

.result-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #2A3B8F;
}

.result-preview {
  margin-top: 1.5rem;
}

.result-card {
  background: #fff;
  border: 1px solid #ebedf0;
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #eee;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item label {
  font-weight: 500;
  color: #6b7280;
}

.result-item span {
  color: #111827;
}

.ai-result-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
}

.ai-result-actions .el-button {
  flex: 1;
}
</style> 