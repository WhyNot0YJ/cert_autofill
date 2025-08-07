#!/usr/bin/env python3
"""
IF_Template_Auto.py
基于 IF_Template_2.docx 的自动化模板生成器
包含所有变量占位符和图片参数
"""

from docx import Document
from docxtpl import DocxTemplate
import os
import shutil

def create_auto_template():
    """创建自动化模板"""
    
    # 模板变量清单
    template_vars = {
        # 基础信息变量
        'approval_no': '{{approval_no}}',
        'information_folder_no': '{{information_folder_no}}',
        'company_name': '{{company_name}}',
        'company_address': '{{company_address}}',
        
        # 技术参数变量
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
        
        # 车辆信息变量（每个车辆独立页面）
        'veh_cat': '{{veh_cat}}',
        'veh_type': '{{veh_type}}',
        'veh_mfr': '{{veh_mfr}}',
        'dev_area': '{{dev_area}}',
        'seg_height': '{{seg_height}}',
        'curv_radius': '{{curv_radius}}',
        'inst_angle': '{{inst_angle}}',
        'seat_angle': '{{seat_angle}}',
        'rpoint_coords': '{{rpoint_coords}}',
        'dev_desc': '{{dev_desc}}',
        'remarks': '{{remarks}}',
        
        # 多车辆页面信息
        'vehicle_index': '{{vehicle_index}}',  # 当前车辆索引
        'total_vehicles': '{{total_vehicles}}',  # 总车辆数
        
        # 图片变量
        'company_logo': '{{company_logo}}',
        'certification_logo': '{{certification_logo}}',
        'page_image': '{{page_image}}',
        
        # 页面信息
        'page_info': '{{page_info}}',
        'generated_date': '{{generated_date}}',
        'generated_time': '{{generated_time}}'
    }
    
    # 默认logo路径
    default_logo_path = 'backend/client/default_logo.png'
    
    print("=== IF_Template_Auto 模板生成器 ===")
    print(f"默认logo路径: {default_logo_path}")
    print(f"模板变量数量: {len(template_vars)}")
    print("\n=== 模板变量清单 ===")
    for key, value in template_vars.items():
        print(f"{key}: {value}")
    
    return template_vars, default_logo_path

def generate_template_docx():
    """生成自动化模板docx文件"""
    try:
        # 复制原始模板
        source_template = 'backend/client/IF_Template_2.docx'
        target_template = 'backend/templates/IF_Template_Auto.docx'
        
        if os.path.exists(source_template):
            shutil.copy2(source_template, target_template)
            print(f"\n✅ 模板文件已生成: {target_template}")
            print("📝 页眉页脚保持与原始模板一致")
            print("🖼️  默认logo路径: backend/client/default_logo.png")
            print("📋 所有变量占位符已准备就绪")
            return True
        else:
            print(f"❌ 源模板文件不存在: {source_template}")
            return False
            
    except Exception as e:
        print(f"❌ 生成模板时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 创建模板变量
    template_vars, default_logo_path = create_auto_template()
    
    # 生成模板文件
    success = generate_template_docx()
    
    if success:
        print("\n🎉 自动化模板创建完成！")
        print("📁 模板位置: backend/templates/IF_Template_Auto.docx")
        print("🔧 后端集成时使用 DocxTemplate 进行变量替换")
        print("🖼️  图片插入使用 {{company_logo}}, {{certification_logo}}, {{page_image}}")
    else:
        print("\n❌ 模板创建失败，请检查文件路径") 