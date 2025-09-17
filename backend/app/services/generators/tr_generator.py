#!/usr/bin/env python3
"""
TR测试报告生成器
生成测试报告文档
"""
from typing import Dict, Any
from .base_generator import BaseGenerator


class TrGenerator(BaseGenerator):
    """TR测试报告生成器"""
    
    def __init__(self):
        super().__init__("TR_Template.docx")
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备TR测试报告上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # TR测试报告特定的数据处理
        context.update({
            # 報告與公司資訊
            'report_no': fields.get('report_no', ''),
            'company_name': fields.get('company_name', ''),
            'approval_no': fields.get('approval_no', ''),
            'trade_names': context.get('trade_names', ''),
            'trade_marks': context.get('trade_marks', []),
            'company_address': fields.get('company_address', ''),
            'information_folder_no': fields.get('information_folder_no', ''),
            # 使用已在父类中格式化的日期，避免被原始值覆盖
            'approval_date': context.get('approval_date', ''),
            'report_date': context.get('report_date', ''),
            
            # 測試對象資訊
            'safety_class': fields.get('safety_class', ''),
            'windscreen_thick': fields.get('windscreen_thick', ''),
            'glass_layers': fields.get('glass_layers', ''),
            'interlayer_layers': fields.get('interlayer_layers', ''),
            'interlayer_thick': fields.get('interlayer_thick', ''),
            'glass_treatment': fields.get('glass_treatment', ''),
            'interlayer_type': fields.get('interlayer_type', ''),
            'coating_type': fields.get('coating_type', ''),
            'coating_thick': fields.get('coating_thick', ''),
            'test_date': context.get('test_date', ''),
            
            # 车辆信息处理
            'vehicles': fields.get('vehicles', []),
            
            # 设备信息处理
            'equipment': fields.get('equipment', []),
            
            # 系统参数 - 版本号
            'version_1': fields.get('version_1', 4),
            'version_2': fields.get('version_2', 8),
            'version_3': fields.get('version_3', 12),
            'version_4': fields.get('version_4', 1),
            
            # 系统参数 - 实验室环境参数
            'temperature': fields.get('temperature', '22°C'),
            'ambient_pressure': fields.get('ambient_pressure', '1020 mbar'),
            'relative_humidity': fields.get('relative_humidity', '50 %')
        })
        
        return context

    def _process_inline_images(self, context, doc):
        """
        直接复用基类对 trade_marks 的通用内联图片处理
        """
        return super()._process_inline_images(context, doc)

    def _get_image_height_for_field(self, field_name: str):
        # 与 IF/CERT 保持一致：商标图片固定高度 0.95cm
        from docx.shared import Cm
        if field_name == 'trade_marks':
            return Cm(0.95)
        return super()._get_image_height_for_field(field_name)

    def _get_image_width_for_field(self, field_name: str):
        # 宽度自动适配
        if field_name == 'trade_marks':
            return None
        return super()._get_image_width_for_field(field_name)
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        创建TR测试报告示例数据
        
        Returns:
            Dict[str, Any]: 示例数据
        """
        return {
            # 報告與公司資訊
            'report_no': 'TR-2024-001',
            'company_name': '示例企业名称',
            'approval_no': 'APP-2024-001',
            'trade_names': '示例品牌',
            'trade_marks': [],
            'company_address': '示例地址',
            'information_folder_no': 'INFO-2024-001',
            'approval_date': '2024-01-01',
            'report_date': '2024-01-15',
            
            # 測試對象資訊
            'safety_class': 'A级',
            'windscreen_thick': '5.0mm',
            'glass_layers': '2层',
            'interlayer_layers': '1层',
            'interlayer_thick': '0.76mm',
            'glass_treatment': '钢化处理',
            'interlayer_type': 'PVB中间膜',
            'coating_type': '防紫外线涂层',
            'coating_thick': '0.1mm',
            'test_date': '2024-01-10',
            
            # 车辆信息
            'vehicles': [
                {'veh_type': '轿车', 'brand': '示例品牌', 'model': '示例型号'}
            ],
            
            # 设备信息
            'equipment': [
                {'no': 'TST2017223', 'name': 'High and low temperature damp heat test chamber'},
                {'no': 'Y009942800', 'name': 'Intelligent transmittance tester'}
            ],
            
            # 系统参数 - 版本号
            'version_1': 4,
            'version_2': 8,
            'version_3': 12,
            'version_4': 1,
            
            # 系统参数 - 实验室环境参数
            'temperature': '22°C',
            'ambient_pressure': '1020 mbar',
            'relative_humidity': '50 %'
        }
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成TR技术报告DOCX文档
        
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
                "message": "TR技术报告生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"TR技术报告生成失败: {str(e)}",
                "error": str(e)
            }

    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成TR技术报告PDF格式
        
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
                    "message": "TR PDF技术报告生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "TR PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"TR PDF生成失败: {str(e)}",
                "error": str(e)
            }


def generate_tr_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """
    生成TR测试报告文档
    
    Args:
        fields: 字段数据
        output_path: 输出文件路径
        format_type: 输出格式 ('docx' 或 'pdf')
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = TrGenerator()
    return generator.generate_document(fields, output_path, format_type)


def create_tr_sample_data() -> Dict[str, Any]:
    """
    创建TR测试报告示例数据
    
    Returns:
        Dict[str, Any]: 示例数据
    """
    generator = TrGenerator()
    return generator.create_sample_data()
