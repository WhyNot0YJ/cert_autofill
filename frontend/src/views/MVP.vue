<template>
  <div class="mvp-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">智能证书生成</h1>
        

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
                      功能未开发：当前仅支持申请书文件用于提取
                    </div>
                  </template>
                </el-upload>
              </div>
            </div>
            <div class="step-actions" v-if="!applicationFiles.length || !extractionResult">
              <el-button 
                type="primary"
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
              <!-- 玻璃类型信息 -->
                <el-divider content-position="left">玻璃类型信息</el-divider>
              <!-- 玻璃类型（please select glass type） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="glass_type">
                      <template #label>
                        please select glass type<br />请选择玻璃类型
                      </template>
                      <el-select v-model="formData.glass_type" placeholder="请选择玻璃类型" style="width: 100%">
                        <el-option v-for="opt in glassTypeOptions" :key="opt" :label="opt" :value="opt" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                <!-- 重要日期信息 -->
                <el-divider content-position="left">重要日期</el-divider>
                
                <!-- 申请日期 -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="approval_date">
                      <template #label>
                        Approval Date<br />申请日期
                      </template>
                      <el-date-picker
                        v-model="formData.approval_date"
                        type="date"
                        placeholder="选择申请日期"
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
                    <el-form-item prop="test_date">
                      <template #label>
                        Test Date<br />测试日期
                      </template>
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
                    <el-form-item prop="report_date">
                      <template #label>
                        Report Date<br />报告日期
                      </template>
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
                   <!-- 证书号（Approval No.） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="approval_no">
                      <template #label>
                        Approval No.<br />证书号
                      </template>
                      <el-input v-model="formData.approval_no" placeholder="请输入证书号" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <!-- 报告号（Report No.） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="report_no">
                      <template #label>
                        Report No.<br />报告号
                      </template>
                      <el-input v-model="formData.report_no" placeholder="请输入报告号" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 选择公司（Company） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="company_id">
                      <template #label>
                        Company<br />选择公司
                      </template>
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
                
                <!-- 公司地址（Company Address） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="company_address">
                      <template #label>
                        Company Address<br />公司地址
                      </template>
                      <el-input 
                        v-model="formData.company_address" 
                        placeholder="请输入公司地址"
                        type="textarea"
                        :rows="3"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 商标名称或图案（Trade Names or Marks） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item>
                      <template #label>
                        Trade Names or Marks<br />商标名称或图案
                      </template>
                      <TradeInfoEditor 
                        v-model:trade-names-text="formData.trade_names"
                        v-model:trade-marks="formData.trade_marks"
                        :readonly-company-data="readonlyCompanyData"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                
                <!-- 信息文件名称（Information Folder No.） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="information_folder_no">
                      <template #label>
                        Information Folder No.<br />信息文件名称
                      </template>
                      <el-input v-model="formData.information_folder_no" placeholder="请输入信息文件名称" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 玻璃类型（Class of safety-glass pane） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="safety_class">
                      <template #label>
                        Class of safety-glass pane<br />玻璃类型
                      </template>
                      <el-input v-model="formData.safety_class" placeholder="请输入玻璃类型" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <!-- 玻璃板描述 (Pane Description) - 锁定不可编辑 -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="pane_desc">
                      <template #label>
                        Description of glass pane<br />玻璃板描述
                      </template>
                      <el-input v-model="formData.pane_desc" placeholder="玻璃板描述（不可编辑）" :disabled="true" />
                    </el-form-item>
                  </el-col>
                </el-row>
              <!-- 主要特性（Principal characteristics） -->
                <el-divider content-position="left">主要特性（Principal characteristics）</el-divider>
                <!-- 玻璃层数（Number of layers of glass） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="glass_layers">
                      <template #label>
                        Number of layers of glass<br />玻璃层数
                      </template>
                      <el-input v-model="formData.glass_layers" placeholder="请输入玻璃层数" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层数（Number of layers of interlayer） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="interlayer_layers">
                      <template #label>
                        Number of layers of interlayer<br />夹层数
                      </template>
                      <el-input v-model="formData.interlayer_layers" placeholder="请输入夹层数" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 风窗厚度（Nominal thickness of the windscreen） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="windscreen_thick">
                      <template #label>
                        Nominal thickness of the windscreen<br />挡风玻璃的标称厚度
                      </template>
                      <el-input v-model="formData.windscreen_thick" placeholder="请输入挡风玻璃的标称厚度">
                        <template #suffix>
                          <span class="unit-suffix unit-mm">mm</span>
                        </template>
                      </el-input>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层厚度（Nominal thickness of interlayer(s)） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="interlayer_thick">
                      <template #label>
                        Nominal thickness of interlayer(s)<br />夹层厚度
                      </template>
                      <el-input v-model="formData.interlayer_thick" placeholder="请输入夹层厚度">
                        <template #suffix>
                          <span class="unit-suffix unit-mm">mm</span>
                        </template>
                      </el-input>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 玻璃处理（Special treatment of glass） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="glass_treatment">
                      <template #label>
                        Special treatment of glass<br />玻璃特殊处理
                      </template>
                      <el-input v-model="formData.glass_treatment" placeholder="请输入玻璃特殊处理" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层性质和类型（Nature and type of interlayer(s)） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="interlayer_type">
                      <template #label>
                        Nature and type of interlayer(s)<br />夹层性质和类型
                      </template>
                      <el-input v-model="formData.interlayer_type" placeholder="请输入夹层性质和类型" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 塑料涂层性质和类型（Nature and type of plastics coating(s)） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="coating_type">
                      <template #label>
                        Nature and type of plastics coating(s)<br />塑料涂层性质和类型
                      </template>
                      <el-input v-model="formData.coating_type" placeholder="请输入塑料涂层性质和类型" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 塑料涂层厚度（Nominal thickness of plastic coating(s)） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="coating_thick">
                      <template #label>
                        Nominal thickness of plastic coating(s)<br />塑料涂层厚度
                      </template>
                      <el-input v-model="formData.coating_thick" placeholder="请输入塑料涂层厚度" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <!-- 次要特性（Secondary characteristics） -->
                <el-divider content-position="left">次要特性（Secondary characteristics ）</el-divider>
                <!-- 材料性质（Nature of the material） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="material_nature">
                      <template #label>
                        Nature of the material<br />材料性质
                      </template>
                      <el-input v-model="formData.material_nature" placeholder="请输入材料性质" />
                    </el-form-item>
                  </el-col>
                </el-row>
               <!-- 玻璃颜色（Colouring of glass） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="glass_color_choice">
                      <template #label>
                        Colouring of glass<br />玻璃颜色
                      </template>
                      <el-checkbox-group v-model="formData.glass_color_choice">
                        <el-checkbox label="colourless">Colourless</el-checkbox>
                        <el-checkbox label="tinted">Tinted</el-checkbox>
                        
                      </el-checkbox-group>
                    </el-form-item>
                  </el-col>
                </el-row>
                 <!-- 塑料涂层颜色（Colouring of plastic coating(s)） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="coating_color">
                      <template #label>
                         Colouring of plastic coating(s) <br />塑料涂层颜色
                      </template>
                       <el-input v-model="formData.coating_color" placeholder="请输入塑料涂层颜色" />
                    </el-form-item>
                  </el-col>
                </el-row>


                <!-- 导体选择（Conductors incorporated） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="conductors_choice">
                      <template #label>
                        Conductors incorporated <br />是否导线
                      </template>
                      <el-checkbox-group v-model="formData.conductors_choice">
                        <el-checkbox label="yes">yes</el-checkbox>
                        <el-checkbox label="no">no</el-checkbox>
                        
                      </el-checkbox-group>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 不透明/模糊选择（Opaque obscuration incorporated） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="opaque_obscure_choice">
                      <template #label>
                        Opaque obscuration incorporated<br />是否不透明遮挡
                      </template>
                      <el-checkbox-group v-model="formData.opaque_obscure_choice">
                               
                        <el-checkbox label="yes">yes</el-checkbox>
                        <el-checkbox label="no">no</el-checkbox>         
                      </el-checkbox-group>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 夹层相关选择（Colouring of interlayer） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item>
                      <template #label>
                        Colouring of interlayer<br />夹层颜色
                      </template>
                      <span style="margin-right: 30px;">&#40;</span>
                      <el-checkbox v-model="formData.interlayer_total">Total</el-checkbox>
                      <span style="margin-right: 30px;">/</span>
                      <el-checkbox v-model="formData.interlayer_partial">Partial</el-checkbox>
                      <span style="margin-right: 30px;">&#41;</span>
                      <el-checkbox v-model="formData.interlayer_tinted">Tinted</el-checkbox>
                      <span style="margin-right: 30px;">/</span>
                      <el-checkbox v-model="formData.interlayer_colourless">Colourless</el-checkbox>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 备注（Remarks） -->
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item prop="remarks">
                      <template #label>
                        Remarks<br/>备注
                      </template>
                      <el-input 
                        v-model="formData.remarks" 
                        type="textarea" 
                        :rows="2"
                        placeholder="请输入备注"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 车辆信息（Vehicle Information） -->
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
                
                <!-- 车辆信息列表（Vehicle Information List） -->
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
                  
                  <!-- 车辆制造商 - 改为textarea -->
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.veh_mfr`">
                        <template #label>
                          Vehicle Manufacturer<br />车辆制造商
                        </template>
                        <el-input 
                          v-model="vehicle.veh_mfr" 
                          type="textarea" 
                          :rows="3"
                          placeholder="请输入车辆制造商信息"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <!-- 车辆类型 - 改为textarea -->
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.veh_type`">
                        <template #label>
                          Type of vehicle<br />车辆类型
                        </template>
                        <el-input 
                          v-model="vehicle.veh_type" 
                          type="textarea" 
                          :rows="2"
                          placeholder="请输入车辆类型"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.veh_cat`">
                        <template #label>
                          Vehicle category<br />车辆类别
                        </template>
                        <el-input v-model="vehicle.veh_cat" placeholder="请输入车辆类别" />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.dev_area`">
                        <template #label>
                          Developed area (F)<br />开发区域
                        </template>
                        <el-input v-model="vehicle.dev_area" placeholder="请输入开发区域">
                          <template #suffix>
                            <span class="unit-suffix unit-area">m²</span>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.seg_height`">
                        <template #label>
                          Height of segment (h)<br />段高度
                        </template>
                        <el-input v-model="vehicle.seg_height" placeholder="请输入段高度">
                          <template #suffix>
                            <span class="unit-suffix unit-mm">mm</span>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.curv_radius`">
                        <template #label>
                          Curvature (r)<br />曲率半径
                        </template>
                        <el-input v-model="vehicle.curv_radius" placeholder="请输入曲率半径">
                          <template #suffix>
                            <span class="unit-suffix unit-mm">mm</span>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.inst_angle`">
                        <template #label>
                          Installation angle (α)<br />安装角度
                        </template>
                        <el-input v-model="vehicle.inst_angle" placeholder="请输入安装角度">
                          <template #suffix>
                            <span class="unit-suffix unit-angle">°</span>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.seat_angle`">
                        <template #label>
                          Seat-back angle (β)<br />座椅角度
                        </template>
                        <el-input v-model="vehicle.seat_angle" placeholder="请输入座椅角度">
                          <template #suffix>
                            <span class="unit-suffix unit-angle">°</span>
                          </template>
                        </el-input>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.rpoint_coords`">
                        <template #label>
                          R-point coordinates (A, B, C) <br />参考点坐标
                        </template>
                        <el-row :gutter="10">
                          <el-col :span="8">
                            <el-form-item :prop="`vehicles.${index}.rpoint_coords.A`">
                              <el-input v-model="vehicle.rpoint_coords.A" placeholder="A坐标">
                                <template #suffix>
                                  <span class="unit-suffix unit-mm">mm</span>
                                </template>
                              </el-input>
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item :prop="`vehicles.${index}.rpoint_coords.B`">
                              <el-input v-model="vehicle.rpoint_coords.B" placeholder="B坐标">
                                <template #suffix>
                                  <span class="unit-suffix unit-mm">mm</span>
                                </template>
                              </el-input>
                            </el-form-item>
                          </el-col>
                          <el-col :span="8">
                            <el-form-item :prop="`vehicles.${index}.rpoint_coords.C`">
                              <el-input v-model="vehicle.rpoint_coords.C" placeholder="C坐标">
                                <template #suffix>
                                  <span class="unit-suffix unit-mm">mm</span>
                                </template>
                              </el-input>
                            </el-form-item>
                          </el-col>
                        </el-row>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <!-- 开发描述 -->
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :prop="`vehicles.${index}.dev_desc`">
                        <template #label>
                          Description of the commercially available specific device<br />市售特定设备的描述
                        </template>
                        <el-input 
                          v-model="vehicle.dev_desc" 
                          placeholder="请输入开发描述"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </el-form>
            </div>

            <div class="step-actions">
              <el-button @click="currentStep = 0">上一步</el-button>
              <div style="flex:1"></div>
              <div class="draft-actions">
                <span v-if="lastDraftSavedAt" class="draft-time">上次保存：{{ new Date(lastDraftSavedAt).toLocaleTimeString() }}</span>
                <el-button 
                  :loading="draftSaving"
                  @click="manualSaveDraft"
                >
                  保存草稿
                </el-button>
                <el-button 
                  type="primary" 
                  @click="saveFormData"
                  :loading="saving"
                  style="margin-left: 12px;"
                >
                  保存并继续
                </el-button>
              </div>
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
                  <!-- 生成模式切换 -->
                  <div class="generation-mode-switch">
                    <el-radio-group v-model="generationMode" class="mode-switch">
                      <el-radio-button label="single">
                        <el-icon><Download /></el-icon>
                        单个生成
                      </el-radio-button>
                      <el-radio-button label="batch">
                        <el-icon><Collection /></el-icon>
                        批量生成
                      </el-radio-button>
                    </el-radio-group>
                  </div>

                  <!-- 生成区域 -->
                  <div class="generation-area">
                    <!-- 单个生成模式 -->
                    <div v-if="generationMode === 'single'" class="generation-section single-generation">
                      <div class="section-header">
                        <h4>单个文档生成</h4>
                        <p>选择特定文档类型和格式进行生成</p>
                      </div>
                      
                      <!-- 文档类型选择 -->
                      <div class="doc-type-selection">
                        <h3>选择文档类型</h3>
                        <el-radio-group v-model="selectedDocType" class="doc-type-group">
                          <el-radio-button label="IF">IF 文档</el-radio-button>
                          <el-radio-button label="CERT">CERT 证书</el-radio-button>
                          <el-radio-button label="OTHER">OTHER 文档</el-radio-button>
                          <el-radio-button label="TR">TR 测试报告</el-radio-button>
                          <el-radio-button label="RCS">RCS 审查控制表</el-radio-button>
                          <el-radio-button label="TM">TM 测试记录</el-radio-button>
                        </el-radio-group>
                      </div>
                      
                      <div class="format-selection">
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
                      </div>
                      
                      <el-button 
                        type="primary" 
                        size="large"
                        @click="generateSelected"
                        :loading="generating"
                        class="generate-btn"
                      >
                        <el-icon><Download /></el-icon>
                        生成 {{ docTypeDisplayName }}
                      </el-button>
                    </div>

                    <!-- 批量生成模式 -->
                    <div v-else class="generation-section batch-generation">
                      <div class="section-header">
                        <h4>批量文档生成</h4>
                        <p>一次性生成所有6种文档类型，提高效率</p>
                      </div>
                      
                      <div class="format-selection">
                        <el-radio-group v-model="batchFormat" class="format-options">
                          <el-radio label="docx">
                            <el-icon><Document /></el-icon>
                            生成所有Word文档
                          </el-radio>
                          <el-radio label="pdf">
                            <el-icon><Document /></el-icon>
                            生成所有PDF文档
                          </el-radio>
                          <el-radio label="both">
                            <el-icon><Collection /></el-icon>
                            生成所有文档（Word + PDF）
                          </el-radio>
                        </el-radio-group>
                      </div>
                      
                      <el-button 
                        type="success" 
                        size="large"
                        @click="generateAllDocuments"
                        :loading="generatingAll"
                        class="generate-btn"
                      >
                        <el-icon><Collection /></el-icon>
                        生成所有{{ batchFormat === 'both' ? '文档（Word + PDF）' : (batchFormat === 'pdf' ? 'PDF' : 'Word') + '文档' }}
                      </el-button>
                    </div>
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
                        <p><strong>单个生成模式:</strong> 选择特定文档类型和格式进行生成，适合精确控制</p>
                        <p><strong>批量生成模式:</strong> 一次性生成所有6种文档类型，提高工作效率</p>
                        <p><strong>支持格式:</strong> Word (.docx) 和 PDF (.pdf)</p>
                        <p><strong>文档类型:</strong> IF、CERT、OTHER、TR、RCS、TM</p>
                      </template>
                    </el-alert>
                  </div>
                </div>

                <!-- 右侧预览面板 -->
                <div class="right-pane">
                  <div class="preview-card">
                    <div class="preview-header">
                      <el-icon><View /></el-icon>
                      生成信息预览
                    </div>
                    <ul class="meta-list">
                      <li>
                        <span>文档类型</span>
                        <strong>{{ docTypeDisplayName }}</strong>
                      </li>
                      <li>
                        <span>会话ID</span>
                        <strong>{{ sessionId || '未生成' }}</strong>
                      </li>
                    </ul>
                    
                    <!-- 模式预览 -->
                    <div class="mode-preview" v-if="generationMode">
                      <div class="preview-divider"></div>
                      <div class="mode-preview-header">
                        <el-icon><View /></el-icon>
                        {{ generationMode === 'single' ? '单个生成预览' : '批量生成预览' }}
                      </div>
                      <div class="mode-info">
                        <p v-if="generationMode === 'single'">
                          <strong>模式:</strong> 单个文档生成
                        </p>
                        <p v-else>
                          <strong>模式:</strong> 批量文档生成
                        </p>
                        <p><strong>格式:</strong> {{ generationMode === 'single' ? (selectedFormat === 'pdf' ? 'PDF' : 'Word') : (batchFormat === 'pdf' ? 'PDF' : 'Word') }}</p>
                        <p v-if="generationMode === 'single'">
                          <strong>文档类型:</strong> {{ docTypeDisplayName }}
                        </p>
                        <p v-else>
                          <strong>文档数量:</strong> 6个文档
                        </p>
                        <p v-if="generationMode === 'batch'">
                          <strong>包含类型:</strong> IF、CERT、OTHER、TR、RCS、TM
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="generating || generatingAll" class="generation-loading">
                <el-progress type="circle" :percentage="generationProgress" />
                <p v-if="generatingAll">正在生成所有文档，请稍候...</p>
                <p v-else>正在生成{{ docTypeDisplayName }}，请稍候...</p>
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
    <!-- 自动保存浮动提示 -->
    <div v-if="showAutosaveToast" class="autosave-toast">
      <span class="dot"></span>
      已自动保存草稿
    </div>
  </div>
</template>

<script setup lang="ts">
import { Delete, Document, Download, Plus, UploadFilled, Refresh, EditPen, View, Collection } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { computed, reactive, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { mvpAPI } from '../api/mvp'
import { companyAPI, type Company } from '../api/company'
import { getServerBaseURL } from '../api'
import TradeInfoEditor from '../components/TradeInfoEditor.vue'
import AppleStyleConfirm from '../components/AppleStyleConfirm.vue'

// 自动保存提示（右下角浮动徽标）
const showAutosaveToast = ref(false)
let autosaveToastTimer: number | undefined

const triggerAutosaveToast = () => {
  showAutosaveToast.value = true
  if (autosaveToastTimer) {
    clearTimeout(autosaveToastTimer)
  }
  autosaveToastTimer = window.setTimeout(() => {
    showAutosaveToast.value = false
    autosaveToastTimer = undefined
  }, 2000)
}

// 步骤定义
const steps = [
  { label: '上传文档' },
  { label: '信息编辑' },
  { label: '生成文档' }
]

// 响应式数据
const route = useRoute()
const currentStep = ref(0)
const sessionId = ref('')


// 文件上传相关
const applicationFiles = ref<any[]>([])
const reportFiles = ref<any[]>([])

// 文档提取相关变量
const extracting = ref(false)
const extractionResult = ref<any>(null)

// 表单相关
const formRef = ref()
const saving = ref(false)
const draftSaving = ref(false)
const lastDraftSavedAt = ref<number | null>(null)
let autosaveTimer: number | undefined

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
  company_address: '',              // 公司地址
  trade_names: '',                  // 商标名称（分号 + 空格分隔的字符串）
  trade_marks: [] as string[],      // 商标图片URL数组
  
  // 新增日期字段
  approval_date: '',                // 申请日期
  test_date: '',                    // 测试日期
  report_date: '',                  // 报告日期
  
  // 核心字段 - 与后端提取格式保持一致
  approval_no: '',                    // 证书号
  information_folder_no: '',          // 信息文件夹号 (与后端字段名一致)
  glass_type: '夹层前挡玻璃',          // 玻璃类型 - 默认第一个选项
  safety_class: '',                   // 安全等级
  pane_desc: '',                      // 玻璃板描述
  glass_layers: '',                   // 玻璃层数
  interlayer_layers: '',              // 夹层数
  windscreen_thick: '',               // 风窗厚度
  interlayer_thick: '',               // 夹层厚度
  glass_treatment: 'not applicable',  // 玻璃处理 - 默认值
  interlayer_type: '',                // 夹层类型
  coating_type: 'not applicable',     // 涂层类型 - 默认值
  coating_thick: 'not applicable',    // 涂层厚度 - 默认值
  material_nature: '',                // 材料性质
  glass_color_choice: ['tinted', 'colourless'], // 玻璃颜色选择 (数组格式) - 默认全选
  coating_color: 'not applicable',    // 涂层颜色 - 默认值
  
  // 夹层相关选择
  interlayer_total: false,               // 总夹层
  interlayer_partial: false,             // 部分夹层
  interlayer_tinted: false,              // 有色夹层
  interlayer_colourless: false,          // 无色夹层
  
  // 选择项数组 - 默认全选
  conductors_choice: ['no', 'yes'],  // 导体选择 (数组格式) - 默认全选
  opaque_obscure_choice: ['no', 'yes'], // 不透明/模糊选择 (数组格式) - 默认全选
  
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
      rpoint_coords: {                  // 参考点坐标
        A: '',
        B: '',
        C: ''
      },
      dev_desc: 'not applicable'                      // 开发描述
    }
  ],
  // 设备信息（随公司选择同步）
  equipment: [] as Array<{ no: string; name: string }>
})

// 玻璃类型可选项（可从后端获取；先内置，与 system_params 同步）
const glassTypeOptions = ref<string[]>([
  '夹层前挡玻璃', '夹层非前挡玻璃', '夹层非前挡玻璃 - 加强', '钢化玻璃'
])

// =============== 本地草稿存储（纯前端） ===============
const DRAFT_KEY = 'mvp_local_draft'

const saveLocalDraft = () => {
  try {
    const payload = {
      form: JSON.parse(JSON.stringify(formData)),
      savedAt: Date.now()
    }
    localStorage.setItem(DRAFT_KEY, JSON.stringify(payload))
    lastDraftSavedAt.value = payload.savedAt
  } catch (_) {}
}

const clearLocalDraft = () => {
  localStorage.removeItem(DRAFT_KEY)
}

const loadLocalDraft = (): { form: any, savedAt: number } | null => {
  const raw = localStorage.getItem(DRAFT_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    if (parsed?.savedAt) lastDraftSavedAt.value = parsed.savedAt
    return parsed
  } catch {
    return null
  }
}

const applyDraftForm = (form: any) => {
  Object.assign(formData, form || {})
}

const tryRestoreDraft = async () => {
  const draft = loadLocalDraft()
  if (!draft) return
  
  // 检查是否有提取的结果数据（表示刚完成识别）
  const hasExtractionResult = extractionResult.value && 
    (extractionResult.value.form_data || Object.keys(extractionResult.value).length > 0)
  
  if (hasExtractionResult) {
    // 有提取结果，说明刚完成识别，不恢复草稿
    return
  }
  
  // 没有提取结果，询问用户是否恢复草稿
  try {
    await ElMessageBox.confirm('检测到本地草稿，是否恢复继续编辑？', '提示', {
      confirmButtonText: '恢复',
      cancelButtonText: '忽略',
      type: 'info'
    })
    applyDraftForm(draft.form)
    ElMessage.success('已恢复本地草稿')
  } catch (_) {
    // 用户取消
  }
}

const autoSaveDraft = () => {
  if (saving.value || draftSaving.value) return
  saveLocalDraft()
  triggerAutosaveToast()
}

const manualSaveDraft = async () => {
  if (saving.value || draftSaving.value) return
  try {
    draftSaving.value = true
    saveLocalDraft()
    ElMessage.success('草稿已保存到本地')
  } finally {
    draftSaving.value = false
  }
}

const startAutosave = () => {
  stopAutosave()
  autosaveTimer = window.setInterval(() => {
    autoSaveDraft()
  }, 30000)
}

const stopAutosave = () => {
  if (autosaveTimer) {
    clearInterval(autosaveTimer)
    autosaveTimer = undefined
  }
}

watch(currentStep, (step) => {
  if (step === 1) {
    tryRestoreDraft()
    startAutosave()
  } else {
    stopAutosave()
  }
})

onMounted(() => {
  if (currentStep.value === 1) {
    tryRestoreDraft()
    startAutosave()
  }
})

onBeforeUnmount(() => {
  stopAutosave()
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
  
  // 申请日期 = 今天-14天
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
      callback(new Error('申请日期不能晚于测试日期'))
    } else if (testDate > reportDate) {
      callback(new Error('测试日期不能晚于报告日期'))
    } else if (approvalDate > reportDate) {
      callback(new Error('申请日期不能晚于报告日期'))
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
    { required: true, message: '请选择申请日期', trigger: 'change' },
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
    { required: true, message: '请输入证书号', trigger: 'blur' }
  ],
  information_folder_no: [
    { required: true, message: '请输入信息文件夹号', trigger: 'blur' }
  ],
  safety_class: [
    { required: true, message: '请输入玻璃类型', trigger: 'blur' }
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
    { required: false, message: '请输入玻璃处理', trigger: 'blur' }
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
    { required: false, message: '请输入材料性质', trigger: 'blur' }
  ],
  coating_color: [
    { required: false, message: '请输入涂层颜色', trigger: 'blur' }
  ],
  glass_color_choice: [
    { 
      required: true, 
      type: 'array',
      min: 1,
      message: '请至少选择一个玻璃颜色选项', 
      trigger: 'change' 
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
      rpoint_coords: [{ required: false, message: '请输入参考点坐标', trigger: 'blur' }],
      'rpoint_coords.A': [{ required: true, message: '请输入A坐标', trigger: 'blur' }],
      'rpoint_coords.B': [{ required: true, message: '请输入B坐标', trigger: 'blur' }],
      'rpoint_coords.C': [{ required: true, message: '请输入C坐标', trigger: 'blur' }],
      dev_desc: [{ required: false, message: '请输入开发描述', trigger: 'blur' }]
    }
  ]
}

// 文档生成相关
const generating = ref(false)
const generatingAll = ref(false)
const generationProgress = ref(0)
const generationResult = ref<any>({
  generated_files: [],
  failed_documents: [],
  total_success: 0,
  total_failed: 0
})
const generatedDocuments = ref<any[]>([])
const selectedFormat = ref('docx')
const batchFormat = ref('docx') // 批量生成格式选择
const generationMode = ref('single') // 生成模式：single 或 batch
// const selectedDocType = ref<'IF'|'CERT'|'OTHER'|'TR'|'RCS'|'TM'>('IF')
const selectedDocType = ref<'IF'|'CERT'|'OTHER'|'TR'|'RCS'|'TM'>('IF')
const docTypeDisplayName = computed(() => {
  const map: Record<string, string> = {
    IF: 'IF',
    CERT: 'CERT 证书文档',
    OTHER: 'OTHER 文档',
    TR: 'TR 测试报告',
    RCS: 'Review Control Sheet 审查控制表',
    TM: 'TM 测试记录',
  }
  const baseName = map[selectedDocType.value] || selectedDocType.value
  return `${baseName} ${selectedFormat.value === 'pdf' ? 'PDF' : 'Word'}`
})


// 方法
const goToStep = (step: number) => {
  if (step <= currentStep.value) {
    currentStep.value = step
  }
}



const handleApplicationChange = (file: any) => {
  applicationFiles.value = [file]
  extractionResult.value = null
  
  // 自动提取，使用正确的API
  if (file.raw) {
    uploadAndExtract(file)
  }
}

const handleReportChange = (_file: any) => {
  ElMessage.info('测试报告上传功能未开发，已禁用')
}

// 直接进行解析（包含文件上传）
const uploadAndExtract = async (file: any) => {
  if (!file?.raw) {
    ElMessage.warning('文件无效')
    return
  }

  // 设置提取状态
  extracting.value = true
  
  // 显示全局loading
  const loadingInstance = ElLoading.service({
    lock: true,
    text: '正在分析申请书，请耐心等待...（通常需要10-60秒）',
    background: 'rgba(0, 0, 0, 0.7)',
    spinner: 'el-icon-loading'
  })
  
  try {
    // 直接调用提取API，后端会自动处理文件上传和解析
    const response = await mvpAPI.aiExtract(file.raw)
    
    if (response.success) {
      // 直接获取提取结果
      extractionResult.value = response.data
      
      
      // 自动应用结果到表单
      await applyExtractionResult()
      
      // 自动跳转到信息编辑步骤
      currentStep.value = 1
      ElMessage.success('解析完成，已自动应用结果并跳转到信息编辑步骤')
    } else {
      ElMessage.error(response.message || '解析失败')
    }
  } catch (error: any) {
    console.error('解析失败:', error)
    const errorMessage = error.message || '解析失败'
    ElMessage.error(errorMessage)
  } finally {
    // 关闭全局loading
    loadingInstance.close()
    extracting.value = false
  }
}

// 注意：aiExtract 函数已被移除，现在只使用自动触发的 uploadAndExtract 函数


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
      rpoint_coords: {
        A: '',
        B: '',
        C: ''
      },
    dev_desc: 'not applicable'
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
        : formData.conductors_choice[0],
      // 处理不透明选择
      opaque_obscure_choice: formData.opaque_obscure_choice.length === 2 
        ? 'both_visible' 
        : formData.opaque_obscure_choice[0],
      // 处理玻璃颜色选择：如果选择了两个，转换为"both_visible"；如果只选择一个，保持原值
      glass_color_choice: formData.glass_color_choice.length === 2 
        ? 'both_visible' 
        : formData.glass_color_choice[0],
      // 确保设备信息总是上传
      equipment: Array.isArray(formData.equipment) ? formData.equipment : []
    }
    
    // 为需要单位的字段添加单位后缀
    if (processedFormData.windscreen_thick && !processedFormData.windscreen_thick.endsWith('mm')) {
      processedFormData.windscreen_thick += ' mm'
    }
    if (processedFormData.interlayer_thick && !processedFormData.interlayer_thick.endsWith('mm')) {
      processedFormData.interlayer_thick += ' mm'
    }
    
    // 处理车辆信息中的单位
    if (processedFormData.vehicles && Array.isArray(processedFormData.vehicles)) {
      processedFormData.vehicles = processedFormData.vehicles.map(vehicle => {
        const processedVehicle = { ...vehicle }
        
        // 开发区域 - 添加 m² 单位
        if (processedVehicle.dev_area && !processedVehicle.dev_area.endsWith('m²')) {
          processedVehicle.dev_area += ' m²'
        }
        
        // 段高度 - 添加 mm 单位
        if (processedVehicle.seg_height && !processedVehicle.seg_height.endsWith('mm')) {
          processedVehicle.seg_height += ' mm'
        }
        
        // 曲率半径 - 添加 mm 单位
        if (processedVehicle.curv_radius && !processedVehicle.curv_radius.endsWith('mm')) {
          processedVehicle.curv_radius += ' mm'
        }
        
        // 安装角度 - 添加 ° 单位
        if (processedVehicle.inst_angle && !processedVehicle.inst_angle.endsWith('°')) {
          processedVehicle.inst_angle += ' °'
        }
        
        // 座椅角度 - 添加 ° 单位
        if (processedVehicle.seat_angle && !processedVehicle.seat_angle.endsWith('°')) {
          processedVehicle.seat_angle += ' °'
        }
        
        // 参考点坐标 - 添加 mm 单位并拼接成字符串
        if (processedVehicle.rpoint_coords && typeof processedVehicle.rpoint_coords === 'object') {
          const coords = []
          
          if (processedVehicle.rpoint_coords.A) {
            const aValue = processedVehicle.rpoint_coords.A.endsWith('mm') 
              ? processedVehicle.rpoint_coords.A 
              : processedVehicle.rpoint_coords.A + ' mm'
            coords.push(`A: ${aValue}`)
          }
          
          if (processedVehicle.rpoint_coords.B) {
            const bValue = processedVehicle.rpoint_coords.B.endsWith('mm') 
              ? processedVehicle.rpoint_coords.B 
              : processedVehicle.rpoint_coords.B + ' mm'
            coords.push(`B: ${bValue}`)
          }
          
          if (processedVehicle.rpoint_coords.C) {
            const cValue = processedVehicle.rpoint_coords.C.endsWith('mm') 
              ? processedVehicle.rpoint_coords.C 
              : processedVehicle.rpoint_coords.C + ' mm'
            coords.push(`C: ${cValue}`)
          }
          
          // 将坐标拼接成字符串格式 "A: A值 B: B值 C: C值"
          processedVehicle.rpoint_coords = coords.join(' ')
        }
        
        return processedVehicle
      })
    }
    
    // 保存前清理本地草稿
    clearLocalDraft()

    // 保存表单数据 - 附带 save_type 与现有 session_id（若有）
    const payload: any = {
      form_data: processedFormData
    }
    if (sessionId.value) {
      payload.session_id = sessionId.value
    }
    const response = await mvpAPI.saveFormData(payload)
    
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

const generateSingleDocument = async (type: 'if'|'cert'|'other'|'tr'|'rcs'|'tm') => {
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
      // 生成完成后自动下载
      try {
        await downloadDocument()
      } catch {}
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
    const downloadUrl = `${getServerBaseURL()}${generationResult.value.download_url}`
    console.log('下载URL:', downloadUrl)
    console.log('getServerBaseURL():', getServerBaseURL())
    console.log('download_url:', generationResult.value.download_url)
    
    // 尝试直接访问URL
    try {
      const response = await fetch(downloadUrl)
      console.log('URL访问状态:', response.status)
      if (response.ok) {
        window.open(downloadUrl, '_blank')
      } else {
        ElMessage.error(`下载失败: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error('下载错误:', error)
      ElMessage.error('下载失败，请检查网络连接')
    }
  }
}

// 已移除：downloadSpecificFile - 现在使用ZIP打包，不需要下载单个文件

const downloadZipFile = async (filename, downloadUrl) => {
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

// 已移除：downloadAllFiles - 现在使用ZIP打包，只需要下载1-2个ZIP文件

// 已移除：retryGenerateDocument - 现在使用批量生成ZIP，不需要重试单个文档

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
    
    if (batchFormat.value === 'both') {
      // 双格式生成：同时调用Word和PDF接口
      const [wordResponse, pdfResponse] = await Promise.all([
        mvpAPI.generateDocuments({ 
          session_id: sessionId.value,
          output_format: 'docx'
        }),
        mvpAPI.generateDocuments({ 
          session_id: sessionId.value,
          output_format: 'pdf'
        })
      ])
      
      // 合并两个响应结果
      if (wordResponse.success && pdfResponse.success) {
        response = {
          success: true,
          message: `成功生成Word和PDF文档，共 ${(wordResponse.data?.total_success || 0) + (pdfResponse.data?.total_success || 0)} 个文档`,
          data: {
            word_zip: {
              filename: wordResponse.data?.filename,
              download_url: wordResponse.data?.download_url
            },
            pdf_zip: {
              filename: pdfResponse.data?.filename,
              download_url: pdfResponse.data?.download_url
            },
            generated_files: [
              ...(wordResponse.data?.generated_files || []),
              ...(pdfResponse.data?.generated_files || [])
            ],
            failed_documents: [
              ...(wordResponse.data?.failed_documents || []),
              ...(pdfResponse.data?.failed_documents || [])
            ],
            total_success: (wordResponse.data?.total_success || 0) + (pdfResponse.data?.total_success || 0),
            total_failed: (wordResponse.data?.total_failed || 0) + (pdfResponse.data?.total_failed || 0)
          }
        }
      } else {
        // 如果其中一个失败，返回失败信息
        response = {
          success: false,
          message: '部分文档生成失败',
          data: {
            word_zip: wordResponse.success ? {
              filename: wordResponse.data?.filename,
              download_url: wordResponse.data?.download_url
            } : null,
            pdf_zip: pdfResponse.success ? {
              filename: pdfResponse.data?.filename,
              download_url: pdfResponse.data?.download_url
            } : null,
            generated_files: [
              ...(wordResponse.data?.generated_files || []),
              ...(pdfResponse.data?.generated_files || [])
            ],
            failed_documents: [
              ...(wordResponse.data?.failed_documents || []),
              ...(pdfResponse.data?.failed_documents || [])
            ],
            total_success: (wordResponse.data?.total_success || 0) + (pdfResponse.data?.total_success || 0),
            total_failed: (wordResponse.data?.total_failed || 0) + (pdfResponse.data?.total_failed || 0)
          }
        }
      }
    } else {
      // 单格式生成
      response = await mvpAPI.generateDocuments({ 
        session_id: sessionId.value,
        output_format: batchFormat.value
      })
    }
    
    // 拦截器已经返回了业务数据，直接使用
    const result = response.data
    
    if (response.success || (result && result.generated_files && result.generated_files.length > 0)) {
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
      // 批量生成完成后自动下载已成功的文件
      try {
        if (batchFormat.value === 'both') {
          // 双格式：下载两个ZIP文件
          if (result.word_zip?.download_url) {
            await downloadZipFile(result.word_zip.filename, result.word_zip.download_url)
          }
          if (result.pdf_zip?.download_url) {
            await downloadZipFile(result.pdf_zip.filename, result.pdf_zip.download_url)
          }
        } else {
          // 单格式：下载单个ZIP文件
          if (result.filename && result.download_url) {
            await downloadZipFile(result.filename, result.download_url)
          }
        }
      } catch {}
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
  const typeMap: Record<string, 'if'|'cert'|'other'|'tr'|'rcs'|'tm'> = {
    // IF: 'if', CERT: 'cert', OTHER: 'other', TR: 'tr', RCS: 'rcs', TM: 'tm'
     IF: 'if', CERT: 'cert', OTHER: 'other', TR: 'tr', RCS: 'rcs', TM: 'tm'
  }
  await generateSingleDocument(typeMap[selectedDocType.value])
}

const downloadSpecificDocument = (doc: any) => {
  if (doc.download_url) {
    const downloadUrl = `${getServerBaseURL()}${doc.download_url}`
    console.log('下载特定文档URL:', downloadUrl)
    window.open(downloadUrl, '_blank')
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
    // 报告号和公司信息
    report_no: "CSR043-A0-2025-07542",
    company_id: defaultCompany?.id || null,
    company_name: defaultCompany?.name || "示例企业",
    company_address: defaultCompany?.address || "示例公司地址",
    trade_names: (defaultCompany?.trade_names && defaultCompany.trade_names.length > 0 
      ? defaultCompany.trade_names.join('; ')
      : "示例商标1; 示例商标2") + '; ',
    trade_marks: defaultCompany?.trade_marks || [],
    // 设备信息（优先使用公司设备，否则给示例）
    equipment: (Array.isArray(defaultCompany?.equipment) && defaultCompany!.equipment.length > 0)
      ? defaultCompany!.equipment
      : [
          { no: 'TST2017223', name: 'High and low temperature damp heat test chamber' },
          { no: 'Y009942800', name: 'Intelligent transmittance tester' }
        ],
    
    // 核心字段
    approval_no: "E4*43R01/12*2812*00",
    information_folder_no: "GZFUYAO-L4.76~5.09mm",
    glass_type: "夹层前挡玻璃",
    safety_class: "Ordinary laminated-glass windscreen",
    pane_desc: "Please refer to Appendix 3 of ECE R43",
    glass_layers: "2",
    interlayer_layers: "1",
    windscreen_thick: "4.76~5.09",
    interlayer_thick: "0.76~1.09",
    glass_treatment: "not applicable",
    interlayer_type: "PVB (Sound insulation HUD)",
    coating_type: "not applicable",
    coating_thick: "not applicable",
    material_nature: "float",
    coating_color: "not applicable",
    glass_color_choice: ["tinted", "colourless"],
    interlayer_total: true,
    interlayer_partial: true,
    interlayer_colourless: true,
    conductors_choice: ["no", "yes"],
    opaque_obscure_choice: ["no", "yes"],
    remarks: "---",
    
    // 车辆信息
    vehicles: [
      {
        veh_mfr: `GAC Motor Co., Ltd.
GAC AION NEW ENERGY AUTOMOBILE CO., LTD.
`,
        veh_type: "AHT",
        veh_cat: "M1",
        dev_area: "1.58",
        seg_height: "59.2",
        curv_radius: "1071",
        inst_angle: "61.6",
        seat_angle: "25",
        rpoint_coords: {
          A: "381.213",
          B: "±370",
          C: "-871.85"
        },
        dev_desc: "not applicable"
      },
      {
        veh_mfr: "示例制造商2",
        veh_type: "SUV",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "120",
        curv_radius: "600",
        inst_angle: "50",
        seat_angle: "35",
        rpoint_coords: {
          A: "150",
          B: "250",
          C: "350"
        },
        dev_desc: "示例车辆2的开发描述"
      },
      {
        veh_mfr: "示例制造商2",
        veh_type: "SUV",
        veh_cat: "M1",
        dev_area: "前风窗",
        seg_height: "120",
        curv_radius: "600",
        inst_angle: "50",
        seat_angle: "35",
        rpoint_coords: {
          A: "150",
          B: "250",
          C: "350"
        },
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
    
    // 将trade_names数组转换为分号+空格分隔的字符串，并追加结尾分隔符
    formData.trade_names = selectedCompany.trade_names && selectedCompany.trade_names.length > 0 
      ? selectedCompany.trade_names.join('; ') + '; '
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

    // 同步设备信息到表单，确保保存时上传
    // companyAPI 已将 equipment 解析为对象数组
    formData.equipment = Array.isArray(selectedCompany.equipment) ? selectedCompany.equipment : []
  } else {
    formData.company_name = ''
    formData.company_address = ''
    formData.trade_names = ''
    formData.trade_marks = []
    formData.equipment = []
    selectedCompanyAddress.value = ''
    readonlyCompanyData.value = null
  }
}



// 在组件挂载时加载公司列表和设置默认日期
onMounted(() => {
  loadCompanies()
  setDefaultDates()
})



// 删除未使用的 ensureFormDefaults

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

// 智能处理提取的公司信息
const handleCompanyInfoFromExtraction = async (extractedCompanyName: string, extractedCompanyAddress: string) => {
  if (!extractedCompanyName) return
  
  // 确保公司列表已加载
  if (companies.value.length === 0) {
    await loadCompanies()
  }
  
  // 查找是否已存在匹配的公司
  const matchedCompany = companies.value.find(company => 
    company.name.toLowerCase().includes(extractedCompanyName.toLowerCase()) ||
    extractedCompanyName.toLowerCase().includes(company.name.toLowerCase())
  )
  
  if (matchedCompany) {
    // 找到匹配的公司，自动选择并填充信息
    formData.company_id = matchedCompany.id
    formData.company_name = matchedCompany.name
    formData.company_address = matchedCompany.address || extractedCompanyAddress
    
    // 同步其他相关字段
    if (matchedCompany.trade_names && matchedCompany.trade_names.length > 0) {
      formData.trade_names = matchedCompany.trade_names.join('; ') + '; '
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
    // 传递提取的完整数据作为额外信息
    const shouldAddCompany = await showAppleStyleCompanyConfirm(extractedCompanyName, extractedCompanyAddress, extractionResult.value)
    
    if (shouldAddCompany) {
      // 用户选择新增公司
      try {
        const newCompany = await addNewCompany(extractedCompanyName, extractedCompanyAddress)
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

const applyExtractionResult = async () => {
  if (!extractionResult.value) return
  
  const r = extractionResult.value

  // 调试信息：显示提取的原始数据
  console.log('🔍 提取原始数据:', r)

  // 获取实际的数据内容（可能嵌套在result字段中）
  const data = r.result || r

  // 智能处理公司信息
  await handleCompanyInfoFromExtraction(data.company_name, data.company_address)

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
    // glass_color_choice 已在下面处理为数组
    coating_color: data.coating_color || '',
    remarks: data.remarks || '',
    
    // 选择项数组 - 确保是数组类型
    conductors_choice: Array.isArray(data.conductors_choice) ? data.conductors_choice : [],
    opaque_obscure_choice: Array.isArray(data.opaque_obscure_choice) ? data.opaque_obscure_choice : [],
    glass_color_choice: Array.isArray(data.glass_color_choice) ? data.glass_color_choice : [],
    
    // 布尔值字段 - 处理字符串和布尔值的转换
    interlayer_total: data.interlayer_total === true || data.interlayer_total === 'true',
    interlayer_partial: data.interlayer_partial === true || data.interlayer_partial === 'true',
    interlayer_colourless: data.interlayer_colourless === true || data.interlayer_colourless === 'true',
    
    // 车辆信息 - 确保是数组类型
    vehicles: Array.isArray(data.vehicles) && data.vehicles.length > 0 ? data.vehicles : [{
      veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', 
      seg_height: '', curv_radius: '', inst_angle: '', 
      seat_angle: '', rpoint_coords: { A: '', B: '', C: '' }, dev_desc: ''
    }]
  }

  // 批量更新表单数据
  Object.assign(formData, fieldMappings)

  // 调试信息：显示映射后的表单数据
  console.log('📝 映射后的表单数据:', formData)

  ElMessage.success('提取结果已应用到表单')
  currentStep.value = 1
}

// 删除未使用的 clearExtractionResult

const skipToManualEdit = async () => {
  // 停止状态并清理结果
  extracting.value = false
  extractionResult.value = null
  
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
  ensure('glass_color_choice', Array.isArray(formData.glass_color_choice) ? formData.glass_color_choice : [])
  ensure('conductors_choice', Array.isArray(formData.conductors_choice) ? formData.conductors_choice : [])
  ensure('opaque_obscure_choice', Array.isArray(formData.opaque_obscure_choice) ? formData.opaque_obscure_choice : [])
  ensure('interlayer_total', !!formData.interlayer_total)
  ensure('interlayer_partial', !!formData.interlayer_partial)
  ensure('interlayer_colourless', !!formData.interlayer_colourless)
  ensure('remarks', formData.remarks ?? '')
  ensure('vehicles', (Array.isArray(formData.vehicles) && formData.vehicles.length > 0) ? formData.vehicles : [{
    veh_mfr: '', veh_type: '', veh_cat: '', dev_area: '', seg_height: '', curv_radius: '', inst_angle: '', seat_angle: '', rpoint_coords: { A: '', B: '', C: '' }, dev_desc: ''
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
:deep(.el-form-item__label){
  height: 50px;
  line-height: 25px;
  display: block;
  align-items: center;
}

/* 自动保存浮动提示 */
.autosave-toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 2000;
  background: rgba(32, 128, 240, 0.95);
  color: #fff;
  padding: 10px 14px;
  border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.18);
  display: flex;
  align-items: center;
  gap: 8px;
  transform: translateY(20px);
  opacity: 0;
  animation: autosave-fade-in 240ms ease forwards;
}

.autosave-toast .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 0 0 rgba(255,255,255,0.8);
  animation: pulse 1200ms infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255,255,255,0.9); }
  70% { box-shadow: 0 0 0 12px rgba(255,255,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); }
}

@keyframes autosave-fade-in {
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

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
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-header .el-icon {
  color: #2A3B8F;
  font-size: 1.1rem;
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

/* 模式预览样式 */
.mode-preview {
  margin-top: 1rem;
}

.preview-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
  margin: 1rem 0;
}

.mode-preview-header {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.mode-preview-header .el-icon {
  color: #2A3B8F;
  font-size: 1rem;
}

.mode-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 0.75rem;
}

.mode-info p {
  margin: 0.25rem 0;
  font-size: 0.85rem;
  color: #374151;
}

.mode-info strong {
  color: #0369a1;
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

/* 生成模式切换 */
.generation-mode-switch {
  text-align: center;
  margin: 2rem 0;
}

.mode-switch {
  display: inline-flex;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 4px;
  border: 2px solid #e9ecef;
}

.mode-switch .el-radio-button {
  margin: 0;
}

.mode-switch .el-radio-button__inner {
  border: none;
  background: transparent;
  color: #6c757d;
  padding: 12px 24px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.mode-switch .el-radio-button__inner:hover {
  background: #e9ecef;
  color: #2A3B8F;
}

.mode-switch .el-radio-button.is-active .el-radio-button__inner {
  background: #2A3B8F;
  color: white;
  box-shadow: 0 2px 8px rgba(42, 59, 143, 0.3);
}

.mode-switch .el-radio-button .el-icon {
  font-size: 1.1rem;
}

/* 生成区域 */
.generation-area {
  margin: 2rem 0;
}

.generation-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  padding: 2rem;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
  text-align: center;
}

.generation-section:hover {
  border-color: #2A3B8F;
  box-shadow: 0 8px 25px rgba(42, 59, 143, 0.1);
}

.single-generation {
  border-left: 4px solid #409eff;
}

.batch-generation {
  border-left: 4px solid #67c23a;
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h4 {
  margin: 0 0 0.5rem 0;
  color: #2A3B8F;
  font-size: 1.2rem;
  font-weight: 600;
}

.section-header p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.format-selection {
  margin-bottom: 1.5rem;
}

.format-options {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.format-options .el-radio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
  cursor: pointer;
}

.format-options .el-radio:hover {
  border-color: #2A3B8F;
  background: #f0f2ff;
}

.format-options .el-radio.is-checked {
  border-color: #2A3B8F;
  background: #2A3B8F;
  color: white;
}

.format-options .el-radio .el-icon {
  font-size: 1.1rem;
}

.generate-btn {
  min-width: 200px;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 文档类型选择样式 */
.doc-type-selection {
  margin-bottom: 1.5rem;
  text-align: center;
}

.doc-type-selection h3 {
  margin: 0 0 1rem 0;
  color: #2A3B8F;
  font-size: 1rem;
  font-weight: 600;
}

.doc-type-group {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.doc-type-group .el-radio-button {
  margin: 0;
}

.doc-type-group .el-radio-button__inner {
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid #e9ecef;
  background: white;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.doc-type-group .el-radio-button__inner:hover {
  border-color: #2A3B8F;
  background: #f0f2ff;
  color: #2A3B8F;
}

.doc-type-group .el-radio-button.is-active .el-radio-button__inner {
  background: #2A3B8F;
  border-color: #2A3B8F;
  color: white;
  box-shadow: 0 2px 8px rgba(42, 59, 143, 0.3);
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

/* 单位后缀样式 */
.unit-suffix {
  color: #2A3B8F;
  font-weight: 600;
  font-size: 14px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f0f2ff 100%);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #2A3B8F;
  box-shadow: 0 2px 4px rgba(42, 59, 143, 0.1);
  position: relative;
  display: inline-block;
  min-width: 32px;
  text-align: center;
  transition: all 0.3s ease;
}

.unit-suffix::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, #2A3B8F, #409eff);
  border-radius: 8px;
  z-index: -1;
  opacity: 0.1;
}

.unit-suffix:hover {
  background: linear-gradient(135deg, #2A3B8F 0%, #409eff 100%);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(42, 59, 143, 0.2);
}

/* 输入框聚焦时单位后缀的样式 */
:deep(.el-input.is-focus .unit-suffix) {
  background: linear-gradient(135deg, #2A3B8F 0%, #409eff 100%);
  color: white;
  box-shadow: 0 4px 8px rgba(42, 59, 143, 0.3);
}

/* 为不同单位类型添加不同颜色和样式 */
.unit-mm {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  color: white;
  font-weight: 700;
}

.unit-area {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border-color: #67c23a;
  color: white;
  font-weight: 700;
}

.unit-angle {
  background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
  border-color: #e6a23c;
  color: white;
  font-weight: 700;
}

/* 单位后缀的动画效果 */
.unit-suffix {
  animation: unitPulse 2s infinite;
}

@keyframes unitPulse {
  0%, 100% {
    box-shadow: 0 2px 4px rgba(42, 59, 143, 0.1);
  }
  50% {
    box-shadow: 0 4px 8px rgba(42, 59, 143, 0.2);
  }
}

/* 单位后缀样式优化 */
.unit-suffix {
  font-size: 13px;
  padding: 3px 6px;
  min-width: 28px;
}
</style> 