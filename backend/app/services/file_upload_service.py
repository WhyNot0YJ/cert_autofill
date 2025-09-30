#!/usr/bin/env python3
"""
文件上传服务类
统一处理文件上传的验证、命名、保存逻辑
"""
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set
from werkzeug.utils import secure_filename
from flask import current_app, request
from werkzeug.datastructures import FileStorage


class FileUploadService:
    """文件上传服务类"""
    
    # 默认允许的文件扩展名
    DEFAULT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: Set[str]) -> bool:
        """
        验证文件类型
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名集合
            
        Returns:
            是否通过验证
        """
        if not filename or '.' not in filename:
            return False
        
        file_ext = filename.rsplit('.', 1)[1].lower()
        return file_ext in allowed_extensions
    
    @staticmethod
    def generate_safe_filename(
        original_filename: str, 
        prefix: str = '', 
        include_timestamp: bool = True,
        include_uuid: bool = True
    ) -> str:
        """
        生成安全的文件名
        
        Args:
            original_filename: 原始文件名
            prefix: 文件名前缀
            include_timestamp: 是否包含时间戳
            include_uuid: 是否包含UUID
            
        Returns:
            生成的安全文件名
        """
        # 获取安全的基础文件名
        safe_name = secure_filename(original_filename)
        
        # 分离文件名和扩展名
        name, ext = os.path.splitext(safe_name)
        
        # 构建文件名部分
        parts = []
        
        if prefix:
            parts.append(prefix)
        
        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            parts.append(timestamp)
        
        if include_uuid:
            unique_id = uuid.uuid4().hex[:8]
            parts.append(unique_id)
        
        # 组合文件名
        if parts:
            new_name = '_'.join(parts) + '_' + name
        else:
            new_name = name
        
        return new_name + ext
    
    @staticmethod
    def create_upload_directory(base_path: str, *subdirs: str) -> str:
        """
        创建上传目录
        
        Args:
            base_path: 基础路径
            *subdirs: 子目录名称
            
        Returns:
            创建的目录路径
        """
        upload_dir = os.path.join(base_path, *subdirs)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    @staticmethod
    def upload_file(
        file: FileStorage,
        category: str,
        subcategory: str = '',
        allowed_extensions: Optional[Set[str]] = None,
        prefix: str = '',
        base_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        统一文件上传处理
        
        Args:
            file: 上传的文件对象
            category: 文件分类
            subcategory: 子分类
            allowed_extensions: 允许的文件扩展名
            prefix: 文件名前缀
            base_dir: 基础目录路径
            
        Returns:
            上传结果字典
            
        Raises:
            ValueError: 文件验证失败时抛出
        """
        if not file or not file.filename:
            raise ValueError("未选择文件")
        
        # 设置默认允许的扩展名
        if allowed_extensions is None:
            allowed_extensions = FileUploadService.DEFAULT_ALLOWED_EXTENSIONS
        
        # 验证文件类型
        if not FileUploadService.validate_file_type(file.filename, allowed_extensions):
            raise ValueError(f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}")
        
        # 生成安全文件名
        filename = FileUploadService.generate_safe_filename(
            file.filename, 
            prefix=prefix or subcategory,
            include_timestamp=True,
            include_uuid=True
        )
        
        # 确定保存目录
        if base_dir is None:
            base_dir = current_app.config['UPLOAD_FOLDER']
        
        # 创建保存目录
        if subcategory:
            save_dir = FileUploadService.create_upload_directory(base_dir, category, subcategory)
        else:
            save_dir = FileUploadService.create_upload_directory(base_dir, category)
        
        # 构建完整文件路径
        file_path = os.path.join(save_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # 生成公开访问路径
        if subcategory:
            public_path = f"{category}/{subcategory}/{filename}"
        else:
            public_path = f"{category}/{filename}"
        
        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "public_path": public_path,
            "public_url": f"/uploads/{public_path}",
            "file_size": file_size,
            "file_ext": file_ext,
            "mime_type": f"image/{file_ext}" if file_ext in FileUploadService.DEFAULT_ALLOWED_EXTENSIONS else "application/octet-stream"
        }
    
    @staticmethod
    def upload_company_file(
        file: FileStorage,
        subcategory: str,
        prefix: str = ''
    ) -> Dict[str, Any]:
        """
        上传公司相关文件（图片、签名、商标）
        
        Args:
            file: 上传的文件对象
            subcategory: 子分类（marks/picture/signature）
            prefix: 文件名前缀
            
        Returns:
            上传结果字典
        """
        if subcategory not in {'marks', 'picture', 'signature'}:
            raise ValueError("无效的子分类，仅支持: marks, picture, signature")
        
        return FileUploadService.upload_file(
            file=file,
            category='company',
            subcategory=subcategory,
            allowed_extensions=FileUploadService.DEFAULT_ALLOWED_EXTENSIONS,
            prefix=prefix or f"company_{subcategory}"
        )
    
    @staticmethod
    def upload_document_file(
        file: FileStorage,
        temp_dir: bool = False
    ) -> Dict[str, Any]:
        """
        上传文档文件（用于AI提取）
        
        Args:
            file: 上传的文件对象
            temp_dir: 是否保存到临时目录
            
        Returns:
            上传结果字典
        """
        category = 'temp' if temp_dir else 'documents'
        
        return FileUploadService.upload_file(
            file=file,
            category=category,
            allowed_extensions=FileUploadService.DOCUMENT_EXTENSIONS,
            prefix='document'
        )
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> bool:
        """
        清理临时文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功删除
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
