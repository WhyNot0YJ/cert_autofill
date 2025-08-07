#!/usr/bin/env python3
"""
IF_Template_Base.py
基础信息模板管理器 - 只包含玻璃相关信息
"""

from docx import Document
from docxtpl import DocxTemplate
import os
import shutil

def create_base_template():
    """创建基础信息模板"""
    
    # 基础信息模板变量清单（只包含玻璃相关信息，共享页脚）
    base_template_vars = {
        # 基础信息变量（玻璃相关信息）
        'approval_no': '{{approval_no}}',
        'information_folder_no': '{{information_folder_no}}',
        'company_name': '{{company_name}}',
        'company_address': '{{company_address}}',
        
        # 技术参数变量（玻璃相关信息）
        'windscreen_thick': '{{windscreen_thick}}',
        'interlayer_thick': '{{interlayer_thick}}',
        'glass_layers': '{{glass_layers}}',
        'interlayer_layers': '{{interlayer_layers}}',
        'interlayer_type': '{{interlayer_type}}',
        'glass_treatment': '{{glass_treatment}}',
        'coating_type': '{{coating_type}}',
        'coating_thick': '{{coating_thick}}',
        'coating_color': '{{coating_color}}',
        'material_nature': '{{material_nature}}',
        'safety_class': '{{safety_class}}',
        'pane_desc': '{{pane_desc}}',
        'remarks': '{{remarks}}',
        
        # 页面信息
        'generated_date': '{{generated_date}}',
        'generated_time': '{{generated_time}}',
        'vehicle_index': '{{vehicle_index}}',  # 基础信息部分
        'total_vehicles': '{{total_vehicles}}',  # 总车辆数
        
        # 图片变量
        'company_logo': '{{company_logo}}',
        'certification_logo': '{{certification_logo}}',
        'page_image': '{{page_image}}',
        
        # 页面信息（共享页脚）
        'page_info': '{{page_info}}'
    }
    
    # 默认logo路径
    default_logo_path = 'backend/client/default_logo.png'
    
    print("=== IF_Template_Base 基础信息模板生成器 ===")
    print(f"默认logo路径: {default_logo_path}")
    print(f"基础信息模板变量数量: {len(base_template_vars)}")
    print("\n=== 基础信息模板变量清单 ===")
    for key, value in base_template_vars.items():
        print(f"{key}: {value}")
    
    return base_template_vars, default_logo_path

def generate_base_template_docx():
    """生成基础信息模板docx文件"""
    try:
        # 复制原始模板
        source_template = '../../client/IF_Template_2.docx'
        target_template = '../../templates/IF_Template_Base.docx'
        
        if os.path.exists(source_template):
            shutil.copy2(source_template, target_template)
            print(f"\n✅ 基础信息模板文件已生成: {target_template}")
            print("📝 页眉页脚保持与原始模板一致")
            print("🖼️  默认logo路径: backend/client/default_logo.png")
            print("📋 基础信息变量占位符已准备就绪")
            print("⚠️  注意：此模板只包含玻璃相关信息，不包含车辆信息")
            print("⚠️  注意：需要手动编辑模板，移除车辆信息部分，保留基础信息和页脚")
            return True
        else:
            print(f"❌ 源模板文件不存在: {source_template}")
            return False
            
    except Exception as e:
        print(f"❌ 生成基础信息模板时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 创建基础信息模板变量
    base_template_vars, default_logo_path = create_base_template()
    
    # 生成基础信息模板文件
    success = generate_base_template_docx()
    
    if success:
        print("\n🎉 基础信息模板创建完成！")
        print("📁 模板位置: backend/templates/IF_Template_Base.docx")
        print("📋 此模板只包含玻璃相关信息，用于生成基础信息部分") 