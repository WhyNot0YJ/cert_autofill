from flask import Blueprint, request, jsonify, current_app
from ..template_manager.template_generator import template_generator
import os

template_bp = Blueprint('template', __name__)

@template_bp.route('/templates', methods=['GET'])
def list_templates():
    """获取所有可用模板"""
    try:
        templates = template_generator.list_templates()
        return jsonify({
            "success": True,
            "data": templates
        })
    except Exception as e:
        return jsonify({"error": f"获取模板列表失败: {str(e)}"}), 500

@template_bp.route('/templates/variables', methods=['GET'])
def get_available_variables():
    """获取所有可用的模板变量"""
    try:
        variables = template_generator.get_available_variables()
        return jsonify({
            "success": True,
            "data": variables
        })
    except Exception as e:
        return jsonify({"error": f"获取变量列表失败: {str(e)}"}), 500

@template_bp.route('/templates', methods=['POST'])
def create_template():
    """创建新模板"""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        selected_variables = data.get('selected_variables', [])
        template_description = data.get('description', '')
        source_template = data.get('source_template')
        
        if not template_name:
            return jsonify({"error": "模板名称不能为空"}), 400
        
        if not selected_variables:
            return jsonify({"error": "请至少选择一个变量"}), 400
        
        # 检查模板名称是否已存在
        existing_templates = template_generator.list_templates()
        if any(t['name'] == template_name for t in existing_templates):
            return jsonify({"error": f"模板名称 '{template_name}' 已存在"}), 400
        
        result = template_generator.generate_template(
            template_name=template_name,
            selected_variables=selected_variables,
            template_description=template_description,
            source_template=source_template
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": f"创建模板失败: {str(e)}"}), 500

@template_bp.route('/templates/<template_name>', methods=['GET'])
def get_template_config(template_name):
    """获取模板配置"""
    try:
        config = template_generator.get_template_config(template_name)
        if 'error' in config:
            return jsonify(config), 404
        
        return jsonify({
            "success": True,
            "data": config
        })
    except Exception as e:
        return jsonify({"error": f"获取模板配置失败: {str(e)}"}), 500

@template_bp.route('/templates/<template_name>', methods=['DELETE'])
def delete_template(template_name):
    """删除模板"""
    try:
        result = template_generator.delete_template(template_name)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({"error": f"删除模板失败: {str(e)}"}), 500

@template_bp.route('/templates/<template_name>/download', methods=['GET'])
def download_template(template_name):
    """下载模板文件"""
    try:
        template_file = os.path.join(template_generator.template_dir, f"{template_name}.docx")
        
        if not os.path.exists(template_file):
            return jsonify({"error": "模板文件不存在"}), 404
        
        from flask import send_file
        return send_file(template_file, as_attachment=True, download_name=f"{template_name}.docx")
        
    except Exception as e:
        return jsonify({"error": f"下载模板失败: {str(e)}"}), 500 