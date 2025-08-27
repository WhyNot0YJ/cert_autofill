#!/usr/bin/env python3
"""
RCS审查控制表生成器
基于Review Control Sheet V7_Template.doc模板生成审查控制表
"""
from typing import Dict, Any
from .base_generator import BaseGenerator


class RcsGenerator(BaseGenerator):
    """RCS审查控制表生成器"""
    
    def __init__(self):
        super().__init__("Review Control Sheet V7_Template.docx")
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备RCS审查控制表上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # RCS审查控制表特定的数据处理
        # 添加必需的变量
        context.update({
            'report_no': fields.get('report_no', ''),
            'approval_no': fields.get('approval_no', ''),
            'company_name': fields.get('company_name', ''),
            'windscreen_thick': fields.get('windscreen_thick', '')
        })
        
        return context
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        创建RCS审查控制表示例数据
        
        Returns:
            Dict[str, Any]: 示例数据
        """
        return {
            # 必需的变量
            'report_no': 'RCS-REPORT-2024-001',
            'approval_no': 'RCS-APPROVAL-2024-001',
            'company_name': '示例企业A',
            'windscreen_thick': '5.0mm',
        }
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成RCS审查控制表DOCX文档
        
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
                "message": "RCS审查控制表生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"RCS审查控制表生成失败: {str(e)}",
                "error": str(e)
            }

    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成RCS审查控制表PDF格式
        
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
                    "message": "RCS PDF审查控制表生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "RCS PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"RCS PDF生成失败: {str(e)}",
                "error": str(e)
            }


def generate_rcs_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """
    生成RCS审查控制表文档
    
    Args:
        fields: 字段数据
        output_path: 输出文件路径
        format_type: 输出格式 ('docx' 或 'pdf')
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = RcsGenerator()
    return generator.generate_document(fields, output_path, format_type)


def create_rcs_sample_data() -> Dict[str, Any]:
    """
    创建RCS审查控制表示例数据
    
    Returns:
        Dict[str, Any]: 示例数据
    """
    generator = RcsGenerator()
    return generator.create_sample_data()
