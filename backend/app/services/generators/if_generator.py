import os
from typing import Dict, Any
from docx.shared import Cm
from docxtpl import DocxTemplate
from .base_generator import BaseGenerator


class IfGenerator(BaseGenerator):
    """IF文档生成器"""
    
    def __init__(self):
        super().__init__("IF_Template.docx")
        self.display_name = "IF 文档"
        self.description = "生成IF认证文档"
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备IF文档上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # IF文档特定的数据处理
        # 处理商标图片 - 使用父类方法转换为本地路径数组
        if 'trade_marks' in fields and fields['trade_marks']:
            context['trade_marks'] = self._process_image_urls_to_paths(fields['trade_marks'])
        
        # 处理公司图片 - 使用父类方法从数据库获取
        context['company_picture'] = self._get_company_picture(fields)
        
        return context
    
    def _process_inline_images(self, context: Dict[str, Any], doc: DocxTemplate) -> Dict[str, Any]:
        """
        重写父类方法，处理IF文档特有的商标图片和公司图片
        
        Args:
            context: 上下文数据
            doc: DocxTemplate 对象
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        processed_context = context.copy()
        
        # 处理商标图片数组 - 使用父类的数组处理方法
        if 'trade_marks' in processed_context and isinstance(processed_context['trade_marks'], list):
            processed_context['trade_marks'] = self._create_inline_image_array(
                doc, 
                processed_context['trade_marks'], 
                'trade_marks',
                height=self._get_image_height_for_field('trade_marks'),
                width=self._get_image_width_for_field('trade_marks')
            )
        
        # 处理公司图片 - 使用父类的单个图片处理方法
        if 'company_picture' in processed_context and isinstance(processed_context['company_picture'], str) and processed_context['company_picture'] != '[公司图片]':
            processed_context['company_picture'] = self._create_single_inline_image(
                doc, 
                processed_context['company_picture'], 
                'company_picture',
                height=self._get_image_height_for_field('company_picture'),
                width=self._get_image_width_for_field('company_picture')
            )
        
        return processed_context
    
    def _get_image_height_for_field(self, field_name: str) -> Cm:
        """
        根据字段名称获取图片高度
        
        Args:
            field_name: 字段名称
            
        Returns:
            Cm: 图片高度
        """
        if field_name == 'trade_marks':
            return Cm(0.95)  # 商标图片固定高度0.95cm
        elif field_name == 'company_picture':
            return Cm(0.9)   # 公司图片固定高度0.9cm
        else:
            return super()._get_image_height_for_field(field_name)
    
    def _get_image_width_for_field(self, field_name: str) -> Cm:
        """
        根据字段名称获取图片宽度
        
        Args:
            field_name: 字段名称
            
        Returns:
            Cm: 图片宽度，如果不需要固定宽度则返回None（自动适配）
        """
        if field_name == 'trade_marks':
            # 商标图片：固定高度，宽度自动适配
            return None
        elif field_name == 'company_picture':
            # 公司图片：固定高度，宽度自动适配
            return Cm(13) 
        else:
            # 其他字段：使用父类的默认设置
            return super()._get_image_width_for_field(field_name)
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成IF文档DOCX格式
        
        Args:
            fields: 表单字段数据
            output_path: 输出文件路径
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        try:
            # 获取模板路径
            template_path = os.path.join(self.template_dir, self.template_name)
            
            # 检查模板文件是否存在
            if not os.path.exists(template_path):
                return {
                    "success": False,
                    "message": f"IF模板文件不存在: {self.template_name}",
                    "error": "Template file not found"
                }
            
            # 准备上下文数据
            context = self.prepare_context(fields)
            
            # 创建模板文档
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
                "message": "IF文档生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"IF文档生成失败: {str(e)}",
                "error": str(e)
            }
    
    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成IF文档PDF格式
        
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
                    "message": "IF PDF文档生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "IF PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"IF PDF生成失败: {str(e)}",
                "error": str(e)
            }


# 为了向后兼容，保留原有的函数名
def generate_if_document(fields, output_path, template_type="IF_Template"):
    """向后兼容的IF文档生成函数"""
    generator = IfGenerator()
    result = generator.generate_docx(fields, output_path)
    return result  # 返回完整的字典结果，而不是布尔值


def generate_if_pdf_from_docx(docx_path, pdf_path):
    """向后兼容的PDF转换函数"""
    generator = IfGenerator()
    return generator._convert_docx_to_pdf(docx_path, pdf_path)
