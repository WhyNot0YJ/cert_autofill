#!/usr/bin/env python3
"""
TM测试记录生成器
生成测试记录文档
"""
from typing import Dict, Any
from .base_generator import BaseGenerator


class TmGenerator(BaseGenerator):
    """TM测试记录生成器"""
    
    def __init__(self):
        super().__init__("TM_Template.docx")
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备TM测试记录上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # TM测试记录特定的数据处理
        # 添加模板所需的变量
        context.update({
            # 一般資訊與特性
            'test_date': fields.get('test_date', ''),
            'windscreen_thick': fields.get('windscreen_thick', ''),
            'glass_layers': fields.get('glass_layers', ''),
            'interlayer_layers': fields.get('interlayer_layers', ''),
            'interlayer_thick': fields.get('interlayer_thick', ''),
            'glass_treatment': fields.get('glass_treatment', ''),
            'interlayer_type': fields.get('interlayer_type', ''),
            'coating_type': fields.get('coating_type', ''),
            'coating_thick': fields.get('coating_thick', ''),
            'material_nature': fields.get('material_nature', ''),
            'coating_color': fields.get('coating_color', ''),
            'interlayer_total': fields.get('interlayer_total', False),
            'conductors_choice': fields.get('conductors_choice', ''),
            'opaque_obscure_choice': fields.get('opaque_obscure_choice', ''),
            'glass_color_choice': fields.get('glass_color_choice', '')
        })
        
        return context
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        创建TM测试记录示例数据
        
        Returns:
            Dict[str, Any]: 示例数据
        """
        return {
            # 一般資訊與特性
            'test_date': '2024-01-15',
            'windscreen_thick': '5.0mm',
            'glass_layers': '2层',
            'interlayer_layers': '1层',
            'interlayer_thick': '0.76mm',
            'glass_treatment': '钢化处理',
            'interlayer_type': 'PVB中间膜',
            'coating_type': '防紫外线涂层',
            'coating_thick': '0.1mm',
            'material_nature': '安全玻璃',
            'coating_color': '透明',
            'interlayer_total': False,
            'conductors_choice': 'yes_struck',
            'opaque_obscure_choice': 'yes_struck',
            'glass_color_choice': 'tinted_struck'
        }
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成TM测试记录DOCX文档
        
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
                "message": "TM测试记录生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TM测试记录生成失败: {str(e)}",
                "error": str(e)
            }

    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成TM测试记录PDF格式
        
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
                    "message": "TM PDF测试记录生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "TM PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"TM PDF生成失败: {str(e)}",
                "error": str(e)
            }


def generate_tm_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """
    生成TM测试记录文档
    
    Args:
        fields: 字段数据
        output_path: 输出文件路径
        format_type: 输出格式 ('docx' 或 'pdf')
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = TmGenerator()
    return generator.generate_document(fields, output_path, format_type)


def create_tm_sample_data() -> Dict[str, Any]:
    """
    创建TM测试记录示例数据
    
    Returns:
        Dict[str, Any]: 示例数据
    """
    generator = TmGenerator()
    return generator.create_sample_data()
