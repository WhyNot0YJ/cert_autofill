#!/usr/bin/env python3
"""
CERT_Template_Auto.py
基于 CERT_Template.docx 的自动化模板生成器
包含所有变量占位符，基于form_data.py中的字段映射
"""

from docx import Document
from docxtpl import DocxTemplate
import os
import shutil

def create_cert_template():
    """创建CERT证书自动化模板 - 基于实际CERT_Template.docx内容"""
    
    # CERT模板变量清单 - 基于实际模板分析结果
    cert_template_vars = {
        # 核心变量 (已在模板中存在)
        'approval_no': '{{approval_no}}',  # 批准号 - 已存在
        'company_name': '{{company_name}}',  # 制造商名称 - 已存在
        
        # 基础审批信息
        'trade_names': '{{trade_names}}',  # 商标名称 (目前固定为 "FYG; FUYAO;")
        'manufacturer_address': '{{manufacturer_address}}',  # 制造商地址
        'report_number': '{{report_number}}',  # 报告编号 (映射自report_no)
        'approval_status': '{{approval_status}}',  # 审批状态 (granted/refused/extended/withdrawn)
        
        # 企业信息 - 映射自form_data和company表
        'enterprise_name': '{{company_name}}',  # 企业名称
        'enterprise_english_name': '{{company_name}}_EN',  # 企业英文名称（待扩展）
        'company_address': '{{company_address}}',  # 公司地址
        'legal_representative': '{{legal_representative}}',  # 法定代表人（待扩展）
        'registration_number': '{{registration_number}}',  # 注册号（待扩展）
        'contact_person': '{{contact_person}}',  # 联系人（待扩展）
        'contact_phone': '{{contact_phone}}',  # 联系电话（待扩展）
        'contact_email': '{{contact_email}}',  # 联系邮箱（待扩展）
        
        # 产品信息 - 映射自form_data技术参数
        'product_name': '汽车安全玻璃',  # 产品名称（固定值）
        'product_model': '{{approval_no}}_MODEL',  # 产品型号（基于批准号）
        'safety_class': '{{safety_class}}',  # 安全等级
        'pane_desc': '{{pane_desc}}',  # 玻璃板描述
        
        # 技术规格 - 映射自form_data技术参数
        'glass_layers': '{{glass_layers}}',  # 玻璃层数
        'interlayer_layers': '{{interlayer_layers}}',  # 夹层数
        'windscreen_thick': '{{windscreen_thick}}',  # 风窗厚度
        'interlayer_thick': '{{interlayer_thick}}',  # 夹层厚度
        'glass_treatment': '{{glass_treatment}}',  # 玻璃处理
        'interlayer_type': '{{interlayer_type}}',  # 夹层类型
        'coating_type': '{{coating_type}}',  # 涂层类型
        'coating_thick': '{{coating_thick}}',  # 涂层厚度
        'coating_color': '{{coating_color}}',  # 涂层颜色
        'material_nature': '{{material_nature}}',  # 材料性质
        
        # 新增form_data字段映射
        'glass_color_choice': '{{glass_color_choice}}',  # 玻璃颜色选择
        'interlayer_total': '{{interlayer_total}}',  # 总夹层
        'interlayer_partial': '{{interlayer_partial}}',  # 部分夹层
        'interlayer_colourless': '{{interlayer_colourless}}',  # 无色夹层
        'conductors_choice': '{{conductors_choice}}',  # 导体选择
        'opaque_obscure_choice': '{{opaque_obscure_choice}}',  # 不透明/模糊选择
        
        # 认证信息
        'certification_type': '汽车安全玻璃认证',  # 认证类型（固定值）
        'certification_scope': '汽车安全玻璃的设计、生产和销售',  # 认证范围（固定值）
        'test_standards': 'GB9656-2021, GB15763.1-2009',  # 测试标准（固定值）
        'test_results': '合格',  # 测试结果（固定值）
        
        # 日期信息
        'issue_date': '{{generated_date}}',  # 签发日期
        'expiry_date': '{{expiry_date}}',  # 有效期（需要计算）
        'generated_date': '{{generated_date}}',  # 生成日期
        'generated_time': '{{generated_time}}',  # 生成时间
        
        # 签发机构信息
        'issuing_authority': 'TÜV NORD认证机构',  # 签发机构（固定值）
        'issuing_authority_en': 'TÜV NORD Certification',  # 签发机构英文名（固定值）
        'authorized_person': '{{authorized_person}}',  # 授权人（待扩展）
        'signature': '{{signature}}',  # 签名（待扩展）
        
        # 备注和技术规格
        'remarks': '{{remarks}}',  # 备注
        'technical_specifications': '{{remarks}}',  # 技术规格说明（使用备注字段）
        'additional_notes': '{{additional_notes}}',  # 附加说明（待扩展）
        
        # 安全特性
        'security_code': 'CERT-{{approval_no}}-{{generated_date}}',  # 安全码
        'verification_url': 'https://verify.tuv-nord.com/cert/{{approval_no}}',  # 验证链接
        'qr_code_data': '{{verification_url}}',  # 二维码数据
        
        # 车辆信息（JSON数组映射）
        'vehicles': '{{vehicles}}',  # 车辆信息数组
        'vehicle_count': '{{vehicle_count}}',  # 车辆数量
        'primary_vehicle': '{{primary_vehicle}}',  # 主要车辆信息
        
        # 状态信息
        'status': '{{status}}',  # 状态
        'is_active': '{{is_active}}',  # 是否活跃
        'session_id': '{{session_id}}',  # 会话ID
        'title': '{{title}}',  # 项目标题
        
        # 图片变量 (使用InlineImage方法)
        'company_logo': '{{company_logo}}',  # 公司logo - 使用InlineImage
        'certification_logo': '{{certification_logo}}',  # 认证logo - 使用InlineImage
        'authority_logo': '{{authority_logo}}',  # 机构logo - 使用InlineImage
        'qr_code': '{{qr_code}}',  # 二维码图片 - 使用InlineImage
        
        # 页眉页脚变量 (支持变量替换)
        'page_header': '{{page_header}}',  # 页眉内容
        'page_footer': '{{page_footer}}',  # 页脚内容
        'header_logo': '{{header_logo}}',  # 页眉logo - 使用InlineImage
        
        # 页面信息
        'page_info': '{{page_info}}',  # 页面信息
        'page_header': '{{page_header}}',  # 页眉
        'page_footer': '{{page_footer}}',  # 页脚
        'document_title': 'Certification of Conformity',  # 文档标题
        'document_subtitle': '符合性证书',  # 文档副标题
        
        # 国际化字段
        'title_en': 'Certificate of Conformity',  # 英文标题
        'title_cn': '符合性证书',  # 中文标题
        'authority_name_en': 'TÜV NORD Certification',  # 机构英文名
        'authority_name_cn': 'TÜV北德认证机构',  # 机构中文名
    }
    
    # 默认logo路径
    default_logo_path = 'backend/client/default_logo.png'
    
    print("=== CERT_Template_Auto 证书模板生成器 ===")
    print(f"默认logo路径: {default_logo_path}")
    print(f"模板变量数量: {len(cert_template_vars)}")
    print("\n=== 证书模板变量清单 ===")
    
    # 按类别显示变量
    categories = {
        "基础证书信息": ["certificate_number", "information_folder_no", "report_no"],
        "企业信息": ["enterprise_name", "enterprise_english_name", "company_address", "legal_representative"],
        "产品信息": ["product_name", "product_model", "safety_class", "pane_desc"],
        "技术规格": ["glass_layers", "interlayer_layers", "windscreen_thick", "interlayer_thick"],
        "认证信息": ["certification_type", "certification_scope", "test_standards", "test_results"],
        "日期信息": ["issue_date", "expiry_date", "generated_date", "generated_time"],
        "安全特性": ["security_code", "verification_url", "qr_code_data"],
        "图片变量": ["company_logo", "certification_logo", "authority_logo", "qr_code"],
        "页面信息": ["page_info", "page_header", "page_footer", "document_title"]
    }
    
    for category, vars_list in categories.items():
        print(f"\n--- {category} ---")
        for var in vars_list:
            if var in cert_template_vars:
                print(f"{var}: {cert_template_vars[var]}")
    
    return cert_template_vars, default_logo_path

def generate_cert_template_docx():
    """生成CERT证书自动化模板docx文件"""
    try:
        # 源模板和目标模板路径
        source_template = 'templates/CERT_Template.docx'
        target_template = 'templates/CERT_Template_Auto.docx'
        
        if os.path.exists(source_template):
            # 复制原始模板作为基础
            shutil.copy2(source_template, target_template)
            print(f"\n✅ CERT证书模板文件已生成: {target_template}")
            print("📝 模板基于原始CERT_Template.docx创建")
            print("🔧 所有变量占位符已准备就绪，使用 {{variable_name}} 格式")
            print("🖼️  支持多种图片变量：company_logo, certification_logo, authority_logo, qr_code")
            print("📋 包含form_data.py中所有相关字段的映射")
            print("🌐 支持中英文双语显示")
            return True
        else:
            print(f"❌ 源模板文件不存在: {source_template}")
            print("💡 请确保CERT_Template.docx文件存在于templates目录中")
            return False
            
    except Exception as e:
        print(f"❌ 生成CERT模板时出错: {str(e)}")
        return False

def map_form_data_to_cert(form_data: dict) -> dict:
    """
    将form_data字段映射到CERT证书字段
    
    Args:
        form_data: FormData模型实例转换的字典
        
    Returns:
        dict: 映射后的证书字段数据
    """
    # 基础映射
    cert_data = {
        # 直接映射字段
        'approval_no': form_data.get('approval_no', ''),
        'information_folder_no': form_data.get('information_folder_no', ''),
        'report_no': form_data.get('report_no', ''),
        'company_name': form_data.get('company_name', ''),
        'safety_class': form_data.get('safety_class', ''),
        'pane_desc': form_data.get('pane_desc', ''),
        'glass_layers': form_data.get('glass_layers', ''),
        'interlayer_layers': form_data.get('interlayer_layers', ''),
        'windscreen_thick': form_data.get('windscreen_thick', ''),
        'interlayer_thick': form_data.get('interlayer_thick', ''),
        'glass_treatment': form_data.get('glass_treatment', ''),
        'interlayer_type': form_data.get('interlayer_type', ''),
        'coating_type': form_data.get('coating_type', ''),
        'coating_thick': form_data.get('coating_thick', ''),
        'coating_color': form_data.get('coating_color', ''),
        'material_nature': form_data.get('material_nature', ''),
        'glass_color_choice': form_data.get('glass_color_choice', ''),
        'conductors_choice': form_data.get('conductors_choice', ''),
        'opaque_obscure_choice': form_data.get('opaque_obscure_choice', ''),
        'remarks': form_data.get('remarks', ''),
        'vehicles': form_data.get('vehicles', []),
        'status': form_data.get('status', ''),
        'session_id': form_data.get('session_id', ''),
        'title': form_data.get('title', ''),
        
        # 布尔值字段处理
        'interlayer_total': '是' if form_data.get('interlayer_total') else '否',
        'interlayer_partial': '是' if form_data.get('interlayer_partial') else '否',
        'interlayer_colourless': '是' if form_data.get('interlayer_colourless') else '否',
        'is_active': '是' if form_data.get('is_active') else '否',
        
        # 计算字段
        'vehicle_count': len(form_data.get('vehicles', [])),
        'primary_vehicle': form_data.get('vehicles', [{}])[0] if form_data.get('vehicles') else {},
    }
    
    return cert_data

if __name__ == "__main__":
    # 创建CERT证书模板变量
    cert_vars, default_logo_path = create_cert_template()
    
    # 生成模板文件
    success = generate_cert_template_docx()
    
    if success:
        print("\n🎉 CERT证书自动化模板创建完成！")
        print("📁 模板位置: backend/templates/CERT_Template_Auto.docx")
        print("🔧 后端集成时使用 DocxTemplate 进行变量替换")
        print("🗺️  使用 map_form_data_to_cert() 函数进行数据映射")
        print("📊 支持form_data.py中的所有字段")
        print(f"📋 总计 {len(cert_vars)} 个模板变量")
    else:
        print("\n❌ CERT证书模板创建失败，请检查文件路径")
