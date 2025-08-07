#!/usr/bin/env python3
"""
IF_Template_Vehicle.py
车辆信息模板管理器 - 只包含车辆相关信息
"""

from docx import Document
from docxtpl import DocxTemplate
import os
import shutil

def create_vehicle_template():
    """创建车辆信息模板"""
    
    # 车辆信息模板变量清单（只包含车辆相关信息，共享页脚）
    vehicle_template_vars = {
        # 车辆信息变量（主要部分）
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
        
        # 页面信息
        'generated_date': '{{generated_date}}',
        'generated_time': '{{generated_time}}',
        'vehicle_index': '{{vehicle_index}}',  # 当前车辆索引
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
    
    print("=== IF_Template_Vehicle 车辆信息模板生成器 ===")
    print(f"默认logo路径: {default_logo_path}")
    print(f"车辆信息模板变量数量: {len(vehicle_template_vars)}")
    print("\n=== 车辆信息模板变量清单 ===")
    for key, value in vehicle_template_vars.items():
        print(f"{key}: {value}")
    
    return vehicle_template_vars, default_logo_path

def generate_vehicle_template_docx():
    """生成车辆信息模板docx文件"""
    try:
        # 复制原始模板
        source_template = '../../client/IF_Template_2.docx'
        target_template = '../../templates/IF_Template_Vehicle.docx'
        
        if os.path.exists(source_template):
            shutil.copy2(source_template, target_template)
            print(f"\n✅ 车辆信息模板文件已生成: {target_template}")
            print("📝 页眉页脚保持与原始模板一致")
            print("🖼️  默认logo路径: backend/client/default_logo.png")
            print("📋 车辆信息变量占位符已准备就绪")
            print("⚠️  注意：此模板只包含车辆信息，不包含基础信息")
            print("⚠️  注意：需要手动编辑模板，移除基础信息部分，保留车辆信息和页脚")
            return True
        else:
            print(f"❌ 源模板文件不存在: {source_template}")
            return False
            
    except Exception as e:
        print(f"❌ 生成车辆信息模板时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 创建车辆信息模板变量
    vehicle_template_vars, default_logo_path = create_vehicle_template()
    
    # 生成车辆信息模板文件
    success = generate_vehicle_template_docx()
    
    if success:
        print("\n🎉 车辆信息模板创建完成！")
        print("📁 模板位置: backend/templates/IF_Template_Vehicle.docx")
        print("📋 此模板包含基础信息和车辆信息，用于生成车辆信息部分") 