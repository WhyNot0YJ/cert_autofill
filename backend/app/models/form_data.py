from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from ..main import db

class FormData(db.Model):
    """表单数据表 - 存储所有用户填写的表单信息"""
    __tablename__ = 'form_data'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)  # 会话ID
    title = Column(String(200))  # 项目标题
    
    # IF_Template_2.docx 相关字段
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
    remarks = Column(Text)                               # 备注
    
    # 公司信息
    company_name = Column(String(200))                   # 公司名称
    
    # 车辆信息 (JSON数组)
    vehicles = Column(JSON, default=lambda: [])                # 车辆信息数组
    
    # 状态管理
    status = Column(String(20), default='draft')  # draft, completed, submitted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FormData(id={self.id}, session_id='{self.session_id}', title='{self.title}')>" 