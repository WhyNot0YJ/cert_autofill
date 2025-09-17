#!/usr/bin/env python3
"""
公司数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..main import db


class Company(db.Model):
    """公司信息模型"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment='公司名称')
    company_contraction = Column(String(100), nullable=True, comment='公司简称')
    address = Column(Text, nullable=True, comment='公司地址')
    signature = Column(String(500), nullable=True, comment='签名图片路径')
    picture = Column(String(500), nullable=True, comment='公司图片路径')
    trade_names = Column(Text, nullable=True, comment='商标名称数组(JSON格式)')
    trade_marks = Column(Text, nullable=True, comment='商标图片URL数组(JSON格式)')
    equipment = Column(Text, nullable=True, comment='设备信息数组(JSON格式)')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联关系
    form_data = relationship("FormData", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        import json
        from flask import current_app
        
        # 统一将图片URL规范化为以 /uploads/ 开头的相对路径，便于前端按环境拼接
        
        # 解析trade_names JSON字符串
        trade_names_list = []
        if self.trade_names:
            try:
                trade_names_list = json.loads(self.trade_names)
            except (json.JSONDecodeError, TypeError):
                trade_names_list = []
        
        # 解析trade_marks JSON字符串并转换为完整URL
        trade_marks_list = []
        if self.trade_marks:
            try:
                marks = json.loads(self.trade_marks)
                # 将相对路径转换为完整的API URL
                for mark in marks:
                    if not mark:
                        continue
                    # 若已是绝对URL，尝试提取其 `/uploads/` 之后的相对部分
                    if mark.startswith('http'):
                        idx = mark.find('/uploads/')
                        if idx != -1:
                            trade_marks_list.append(mark[idx:])
                        else:
                            trade_marks_list.append(mark)
                    else:
                        # 确保以 /uploads/ 开头
                        trade_marks_list.append(mark if mark.startswith('/uploads/') else f"/uploads/{mark.lstrip('/')}")
            except (json.JSONDecodeError, TypeError):
                trade_marks_list = []
        
        # 解析equipment JSON字符串
        equipment_list = []
        if self.equipment:
            try:
                equipment_list = json.loads(self.equipment)
                if not isinstance(equipment_list, list):
                    equipment_list = []
            except (json.JSONDecodeError, TypeError):
                equipment_list = []
        
        # 处理picture字段，输出相对路径
        picture_url = None
        if self.picture:
            pic = self.picture
            if pic.startswith('http'):
                idx = pic.find('/uploads/')
                picture_url = pic[idx:] if idx != -1 else pic
            else:
                picture_url = pic if pic.startswith('/uploads/') else f"/uploads/{pic.lstrip('/')}"
        
        # 处理signature字段，输出相对路径
        signature_url = None
        if self.signature:
            sig = self.signature
            if sig.startswith('http'):
                idx = sig.find('/uploads/')
                signature_url = sig[idx:] if idx != -1 else sig
            else:
                signature_url = sig if sig.startswith('/uploads/') else f"/uploads/{sig.lstrip('/')}"
        
        return {
            'id': self.id,
            'name': self.name,
            'company_contraction': self.company_contraction,
            'address': self.address,
            'signature': signature_url,
            'picture': picture_url,
            'trade_names': trade_names_list,  # 返回解析后的数组
            'trade_marks': trade_marks_list,  # 返回解析后的完整URL数组
            'equipment': equipment_list,  # 返回解析后的设备数组
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
