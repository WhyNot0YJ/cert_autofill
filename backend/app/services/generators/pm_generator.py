#!/usr/bin/env python3
"""
PM项目管理表生成器
生成项目管理表文档
"""
from typing import Dict, Any
from .base_generator import BaseGenerator


class PmGenerator(BaseGenerator):
    """PM项目管理表生成器"""
    
    def __init__(self):
        super().__init__("项目管理表模版-V3.4 福耀广州 20250807.xlsx")
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备PM项目管理表上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        # 调用父类方法获取基础上下文
        context = super().prepare_context(fields)
        
        # PM项目管理表特定的数据处理
        # 这里可以根据需要添加PM特定的数据处理逻辑
        
        return context
    
    def create_sample_data(self) -> Dict[str, Any]:
        """
        创建PM项目管理表示例数据
        
        Returns:
            Dict[str, Any]: 示例数据
        """
        return {
            'project_name': '汽车安全玻璃认证项目',
            'project_number': 'PM-2024-001',
            'project_manager': '王五',
            'project_manager_phone': '010-12345678',
            'project_manager_email': 'pm@example.com',
            'company_name': '示例企业名称',
            'start_date': '2024-01-01',
            'planned_end_date': '2024-06-30',
            'actual_end_date': '2024-06-15',
            'project_status': '进行中',
            'project_phase': '技术评审阶段',
            'project_scope': '汽车安全玻璃质量管理体系认证',
            'project_objectives': [
                '建立完善的质量管理体系',
                '通过TÜV NORD认证审核',
                '获得相关产品认证证书'
            ],
            'key_milestones': [
                {'name': '项目启动', 'date': '2024-01-01', 'status': '已完成'},
                {'name': '体系建立', 'date': '2024-03-15', 'status': '已完成'},
                {'name': '内部审核', 'date': '2024-04-30', 'status': '已完成'},
                {'name': '外部审核', 'date': '2024-06-15', 'status': '进行中'},
                {'name': '项目完成', 'date': '2024-06-30', 'status': '计划中'}
            ],
            'team_members': [
                {'name': '王五', 'role': '项目经理', 'phone': '010-12345678'},
                {'name': '李四', 'role': '技术负责人', 'phone': '010-12345679'},
                {'name': '张三', 'role': '质量负责人', 'phone': '010-12345680'}
            ],
            'budget': {
                'total_budget': 500000,
                'used_budget': 350000,
                'remaining_budget': 150000,
                'currency': 'CNY'
            },
            'risks': [
                {'risk': '技术标准变更', 'impact': '高', 'mitigation': '密切关注标准更新'},
                {'risk': '审核延期', 'impact': '中', 'mitigation': '提前准备审核材料'},
                {'risk': '人员变动', 'impact': '低', 'mitigation': '建立知识传承机制'}
            ],
            'next_actions': [
                '完成外部审核准备',
                '整理认证申请材料',
                '安排最终技术评审'
            ],
            'approval_status': '已批准',
            'approver_name': '赵六',
            'approver_title': '技术总监'
        }
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成PM项目管理表DOCX文档
        
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
            
            # PM 生成器特殊处理 - 因为原模板是 Excel 格式
            if self.template_filename == "PM_Template_Placeholder.docx":
                return {
                    "success": False,
                    "message": "PM 项目管理表模板需要 Excel 格式，暂不支持 Word 生成",
                    "error": "PM template requires Excel format, Word generation not yet supported"
                }
            
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
                "message": "PM项目管理表生成成功",
                "data": {"output_path": output_path}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"PM项目管理表生成失败: {str(e)}",
                "error": str(e)
            }

    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        生成PM项目管理表PDF格式
        
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
                    "message": "PM PDF项目管理表生成成功",
                    "data": {"output_path": output_path}
                }
            else:
                return {
                    "success": False,
                    "message": "PM PDF转换失败",
                    "error": "PDF conversion failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"PM PDF生成失败: {str(e)}",
                "error": str(e)
            }


def generate_pm_document(fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
    """
    生成PM项目管理表文档
    
    Args:
        fields: 字段数据
        output_path: 输出文件路径
        format_type: 输出格式 ('docx' 或 'pdf')
        
    Returns:
        Dict[str, Any]: 生成结果
    """
    generator = PmGenerator()
    return generator.generate_document(fields, output_path, format_type)


def create_pm_sample_data() -> Dict[str, Any]:
    """
    创建PM项目管理表示例数据
    
    Returns:
        Dict[str, Any]: 示例数据
    """
    generator = PmGenerator()
    return generator.create_sample_data()
