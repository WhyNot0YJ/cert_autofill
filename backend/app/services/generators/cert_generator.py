#!/usr/bin/env python3
"""
CERT证书生成器
基于CERT_Template.docx参数化模板生成证书文档
"""
import os
from datetime import datetime
from typing import Dict, Any
from docx.shared import Cm
from docxtpl import DocxTemplate
from .base_generator import BaseGenerator


class CertGenerator(BaseGenerator):
    """CERT证书生成器"""
    
    def __init__(self):
        super().__init__("CERT_Template.docx")
        self.display_name = "CERT 证书"
        self.description = "生成CERT认证证书"
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备CERT文档上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # CERT文档特定的数据处理
        # 计算 simple_no：例如将 "E4*43R01/12*2876*00" 转为 "43R-012876"
        approval_no = (fields.get('approval_no') or '').strip()
        simple_no = ''
        if approval_no:
            parts = [p for p in approval_no.split('*') if p]
            try:
                # 解析法规段，例如 "43R01/12" → reg_code="43R"，version="01"
                reg_seg = parts[1] if len(parts) > 1 else ''
                reg_left = reg_seg.split('/') [0] if reg_seg else ''
                import re
                m = re.search(r'(\d+R)(\d{2})', reg_left)
                if not m:
                    # 尝试宽松匹配：允许前缀非数字，例如 "E43R01" 也能匹配出 43R/01
                    m = re.search(r'(?:(?:[A-Z])*)(\d+R)(\d{2})', reg_left)
                if m:
                    reg_code = m.group(1)  # e.g. 43R
                    ver2 = m.group(2)      # e.g. 01
                else:
                    reg_code, ver2 = '', ''

                # 解析编号段，例如 parts[2] = "2876" → 编号左侧补齐至少4位
                num_seg = parts[2] if len(parts) > 2 else ''
                num_clean = re.sub(r'\D', '', num_seg)
                if num_clean:
                    num_padded = num_clean.zfill(4)
                else:
                    num_padded = ''

                if reg_code and (ver2 or num_padded):
                    simple_no = f"{reg_code}-{ver2}{num_padded}"
                else:
                    # 兜底回退：保持原 approval_no
                    simple_no = approval_no
            except Exception:
                simple_no = approval_no
        else:
            simple_no = approval_no

        
        # 处理公司图片 - 使用父类方法从数据库获取
        context['company_picture'] = self._get_company_picture(fields)
        
        # 添加CERT特有的字段
        context.update({
                'simple_no': simple_no,
                'generated_date': datetime.now().strftime('%Y-%m-%d'),
                'generated_time': datetime.now().strftime('%H:%M:%S')
        })
        
        return context
    
    def _process_inline_images(self, context: Dict[str, Any], doc: DocxTemplate) -> Dict[str, Any]:
        """
        重写父类方法，处理CERT文档特有的商标图片和公司图片
        
        Args:
            context: 上下文数据
            doc: DocxTemplate 对象
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 先让基类处理通用图片（trade_marks 等）
        processed_context = super()._process_inline_images(context, doc)
        
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
            return None
        else:
            # 其他字段：使用父类的默认设置
            return super()._get_image_width_for_field(field_name)
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成CERT文档DOCX格式
        
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
                    "message": f"CERT模板文件不存在: {self.template_name}",
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
                "message": "CERT文档生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"CERT文档生成失败: {str(e)}",
                "error": str(e)
            }
    
    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成CERT文档PDF格式
        
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
                    "message": "CERT PDF文档生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "CERT PDF转换失败",
                    "error": "PDF conversion failed"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"CERT PDF生成失败: {str(e)}",
                "error": str(e)
            }

    def create_sample_data(self):
        """创建CERT文档的示例数据"""
        from datetime import date, timedelta
        
        today = date.today()
        return {
            'approval_no': 'CERT-2024-001*EXTENSION',  # 包含*用于测试simple_no
            'information_folder_no': 'CERT-FOLDER-2024-001',
            'safety_class': 'A',
            'pane_desc': '前风窗玻璃',
            'glass_layers': '2',
            'interlayer_layers': '1',
            'windscreen_thick': '5.0mm',
            'interlayer_thick': '0.76mm',
            'glass_treatment': '钢化',
            'interlayer_type': 'PVB',
            'coating_type': '无',
            'coating_thick': '0mm',
            'material_nature': '无机',
            'coating_color': '无色',
            'glass_color_choice': 'tinted_struck',
            'conductors_choice': 'yes_struck',
            'opaque_obscure_choice': 'yes_struck',
            'interlayer_total': True,
            'interlayer_partial': False,
            'interlayer_colourless': True,
            'remarks': '示例CERT证书数据',
            'report_no': 'CERT-REPORT-2024-001',
            # 新增标准日期字段
            'approval_date': today - timedelta(days=14),
            'test_date': today - timedelta(days=7),
            'report_date': today,
            'company_name': '示例企业',
            'company_address': '北京市朝阳区汽车工业园区示例路123号',
            'trade_names': '示例商标;企业标识',
            'trade_marks': [f'{current_app.config.get("SERVER_URL", "http://localhost")}/uploads/company/marks/defaut_mark.png'],
            # 设备信息（示例）
            'equipment': [
                {'no': 'TST2017223', 'name': 'High and low temperature damp heat test chamber'},
                {'no': 'Y009942800', 'name': 'Intelligent transmittance tester'}
            ],
            'vehicles': [
                {
                    'veh_mfr': '示例制造商',
                    'veh_type': '轿车',
                    'veh_cat': 'M1',
                    'dev_area': '前风窗',
                    'seg_height': '500mm',
                    'curv_radius': '1000mm',
                    'inst_angle': '65°',
                    'seat_angle': '25°',
                    'rpoint_coords': 'X:100, Y:200, Z:300',
                    'dev_desc': '前风窗玻璃开发描述'
                }
            ]
        }


# 为了向后兼容，保留原有的函数名
def generate_cert_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """向后兼容的CERT文档生成函数"""
    generator = CertGenerator()
    if format_type == 'pdf':
        result = generator.generate_pdf(fields, output_path)
    else:
        result = generator.generate_docx(fields, output_path)
    return result


def create_cert_sample_data() -> Dict[str, Any]:
    """创建CERT证书示例数据"""
    generator = CertGenerator()
    return generator.create_sample_data()