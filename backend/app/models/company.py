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
    address = Column(Text, nullable=True, comment='公司地址')
    signature = Column(String(500), nullable=True, comment='签名图片路径')
    picture = Column(String(500), nullable=True, comment='公司图片路径')
    trade_names = Column(Text, nullable=True, comment='商标名称数组(JSON格式)')
    trade_marks = Column(Text, nullable=True, comment='商标图片URL数组(JSON格式)')
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
        
        # 获取配置的服务器地址
        server_url = current_app.config.get('SERVER_URL', 'http://localhost')
        
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
                    if mark and not mark.startswith('http'):
                        # 移除开头的/uploads/（如果存在）
                        if mark.startswith('/uploads/'):
                            mark = mark[9:]  # 移除 '/uploads/'
                        trade_marks_list.append(f"{server_url}/uploads/{mark}")
                    else:
                        trade_marks_list.append(mark)
            except (json.JSONDecodeError, TypeError):
                trade_marks_list = []
        
        # 处理picture字段
        picture_url = None
        if self.picture:
            if not self.picture.startswith('http'):
                # 移除开头的/uploads/（如果存在）
                picture_path = self.picture
                if picture_path.startswith('/uploads/'):
                    picture_path = picture_path[9:]  # 移除 '/uploads/'
                picture_url = f"{server_url}/uploads/{picture_path}"
            else:
                picture_url = self.picture
        
        # 处理signature字段
        signature_url = None
        if self.signature:
            if not self.signature.startswith('http'):
                # 移除开头的/uploads/（如果存在）
                signature_path = self.signature
                if signature_path.startswith('/uploads/'):
                    signature_path = signature_path[9:]  # 移除 '/uploads/'
                signature_url = f"{server_url}/uploads/{signature_path}"
            else:
                signature_url = self.signature
        
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'signature': signature_url,
            'picture': picture_url,
            'trade_names': trade_names_list,  # 返回解析后的数组
            'trade_marks': trade_marks_list,  # 返回解析后的完整URL数组
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
