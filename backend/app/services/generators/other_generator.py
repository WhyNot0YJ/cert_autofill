#!/usr/bin/env python3
"""
OTHER文档生成器
生成其他类型的文档
"""
from typing import Dict, Any, Union
from .base_generator import BaseGenerator
from docx.shared import Cm
from docxtpl import DocxTemplate, InlineImage
import os


class OtherGenerator(BaseGenerator):
    """OTHER文档生成器"""
    
    def __init__(self):
        super().__init__("OTHER_Template.docx")
        self.signature_height = Cm(0.77)  # 签名图片高度
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备OTHER文档上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # OTHER文档特定的数据处理
        # 从 formdata 获取 approval_no
        approval_no = fields.get('approval_no', 'OTHER-2024-001')
        
        # 从 company 数据库搜索对应的 signature
        signature_image = self._get_company_signature(fields)
        
        # 准备上下文数据
        context.update({
            'approval_no': approval_no,
            'signature': signature_image
        })
        return context
    
    def _process_inline_images(self, context: Dict[str, Any], doc: DocxTemplate) -> Dict[str, Any]:
        """
        处理OTHER文档的内联图片
        
        Args:
            context: 上下文数据
            doc: DocxTemplate 对象
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        try:
            # 处理签名图片
            signature_value = context.get('signature', '')
            
            # 如果签名不是占位符，创建InlineImage对象
            if signature_value and signature_value != '[签名图片]':
                # 使用父类的_create_single_inline_image方法
                signature_image = self._create_single_inline_image(
                    doc=doc,
                    image_path=signature_value,
                    field_name='signature',
                    height=self.signature_height,
                    width=None  # 保持宽高比
                )
                
                if signature_image and not isinstance(signature_image, str):
                    context['signature'] = signature_image
                else:
                    context['signature'] = '[签名图片不可用]'
            else:
                context['signature'] = '[签名图片]'
            
            return context
            
        except Exception as e:
            # 发生错误时，使用占位符
            context['signature'] = '[签名图片处理失败]'
            return context
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        创建OTHER文档示例数据
        
        Returns:
            Dict[str, Any]: 示例数据
        """
        from datetime import date, timedelta
        
        today = date.today()
        return {
            'approval_no': 'OTHER-2024-001',
            'approval_date': today - timedelta(days=14),
            'test_date': today - timedelta(days=7),
            'report_date': today,
            'signature': '[签名图片]'
        }
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成OTHER文档DOCX文档
        
        Args:
            fields: 字段数据
            output_path: 输出文件路径
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        try:
            import os
            from docxtpl import DocxTemplate
            
            # 准备上下文数据
            context = self.prepare_context(fields)
            
            # 加载模板
            template_path = os.path.join(self.template_dir, self.template_filename)
            if not os.path.exists(template_path):
                return {
                    "success": False,
                    "message": f"模板文件不存在: {self.template_filename}",
                    "error": "Template file not found"
                }
            
            doc = DocxTemplate(template_path)
            
            # 处理内联图片
            context = self._process_inline_images(context, doc)
            
            # 渲染文档
            doc.render(context)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存文档
            doc.save(output_path)
            
            return {
                "success": True,
                "message": "OTHER文档生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"OTHER文档生成失败: {str(e)}",
                "error": str(e)
            }

    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成OTHER文档PDF格式
        
        Args:
            fields: 表单字段数据
            output_path: 输出文件路径
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        try:
            # 先生成DOCX文件
            docx_path = output_path.replace('.pdf', '.docx')
            docx_result = self.generate_docx(fields, docx_path)
            
            if not docx_result.get('success'):
                return docx_result
            
            # 转换为PDF
            pdf_success = self._convert_docx_to_pdf(docx_path, output_path)
            if pdf_success:
                return {
                    "success": True,
                    "message": "OTHER PDF文档生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "OTHER PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"OTHER PDF生成失败: {str(e)}",
                "error": str(e)
            }


def generate_other_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """
    生成OTHER文档
    
    Args:
        fields: 字段数据
        output_path: 输出文件路径
        format_type: 输出格式 ('docx' 或 'pdf')
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = OtherGenerator()
    return generator.generate_document(fields, output_path, format_type)


def create_other_sample_data() -> Dict[str, Any]:
    """
    创建OTHER文档示例数据
    
    Returns:
        Dict[str, Any]: 示例数据
    """
    generator = OtherGenerator()
    return generator.create_sample_data()
