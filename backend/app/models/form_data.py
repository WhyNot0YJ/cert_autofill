from datetime import datetime, date, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..main import db

class FormData(db.Model):
    """表单数据表 - 存储所有用户填写的表单信息"""
    __tablename__ = 'form_data'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)  # 会话ID
    
    # IF_Template.docx 相关字段
    approval_no = Column(String(100))                    # 批准号
    information_folder_no = Column(String(100))          # 信息文件夹号
    safety_class = Column(String(50))                    # 安全等级
    pane_desc = Column(Text)                             # 玻璃板描述
    glass_layers = Column(String(50))                    # 玻璃层数
    interlayer_layers = Column(String(50))               # 夹层数
    windscreen_thick = Column(String(50))                # 风窗厚度
    interlayer_thick = Column(String(50))                # 夹层厚度
    glass_treatment = Column(String(100))                # 玻璃处理
    interlayer_type = Column(String(100))                # 夹层类型
    coating_type = Column(String(100))                   # 涂层类型
    coating_thick = Column(String(50))                   # 涂层厚度
    material_nature = Column(String(100))                # 材料性质
    coating_color = Column(String(50))                   # 涂层颜色
    
    # 新增字段 - 玻璃颜色和夹层相关
    glass_color_choice = Column(String(20), default='tinted_struck')  # 玻璃颜色选择
    interlayer_total = Column(Boolean, default=False)                  # 总夹层
    interlayer_partial = Column(Boolean, default=False)               # 部分夹层
    interlayer_colourless = Column(Boolean, default=False)            # 无色夹层
    
    # 新增字段 - 导体和不透明相关
    conductors_choice = Column(String(20), default='yes_struck')      # 导体选择
    opaque_obscure_choice = Column(String(20), default='yes_struck')  # 不透明/模糊选择
    
    remarks = Column(Text)                               # 备注
    
    # 报告号和公司信息
    report_no = Column(String(100))                      # 报告号
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True)  # 公司ID（保留用于快速填充）
    company_name = Column(String(200))                   # 公司名称
    company_address = Column(Text)                       # 公司地址
    trade_names = Column(String(500))                    # 商标名称（分号分隔的字符串）
    trade_marks = Column(JSON, default=lambda: [])      # 商标图片URL数组
    
    # 设备信息 (JSON数组)
    equipment = Column(JSON, default=lambda: [])                # 设备信息数组
    
    # 新增日期字段
    approval_date = Column(Date, nullable=False, default=lambda: date.today() - timedelta(days=14))   # 批准日期，默认今天-14天
    test_date = Column(Date, nullable=False, default=lambda: date.today() - timedelta(days=7))        # 测试日期，默认今天-7天  
    report_date = Column(Date, nullable=False, default=date.today)                                    # 报告日期，默认今天
    # 法规更新日期（系统自动写入）
    regulation_update_date = Column(String(20), nullable=True)
    
    # 车辆信息 (JSON数组)
    vehicles = Column(JSON, default=lambda: [])                # 车辆信息数组
    
    # 系统参数 - 版本号（统一为字符串类型，避免前导零丢失）
    version_1 = Column(String(10), default='4')                # 版本号第1部分
    version_2 = Column(String(10), default='8')                # 版本号第2部分
    version_3 = Column(String(10), default='12')               # 版本号第3部分
    version_4 = Column(String(10), default='01')               # 版本号第4部分
    # 新增：玻璃类型（可配置的下拉选项值）
    glass_type = Column(String(50))
    
    # 系统参数 - 实验室环境参数
    temperature = Column(String(20), default='22°C')           # 温度（包含单位）
    ambient_pressure = Column(String(20), default='1020 mbar') # 环境压力（包含单位）
    relative_humidity = Column(String(20), default='50 %')     # 相对湿度（包含单位）
    
    # 状态管理（移除status列，仅保留is_active）
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    company = relationship("Company", back_populates="form_data")
    
    def __repr__(self):
        return f"<FormData(id={self.id}, session_id='{self.session_id}')>"