from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import json
import uuid
import zipfile
import tempfile
from datetime import datetime, date
from ..models import Document, DocumentUpload, FormData
from ..services.ai_extract import ai_extraction_service
from ..services.system_config import system_config

from ..services.generators import (
    generate_if_document, generate_if_pdf_from_docx,
    generate_cert_document, create_cert_sample_data,
    generate_rcs_document, create_rcs_sample_data,
    generate_other_document, create_other_sample_data,
    generate_tr_document, create_tr_sample_data,
    generate_tm_document, create_tm_sample_data,
)
from ..services.generators.rcs_generator import RcsGenerator
from ..services.generators.other_generator import OtherGenerator
from ..services.generators.tr_generator import TrGenerator
from ..services.generators.tm_generator import TmGenerator
from ..main import db
from sqlalchemy.orm import sessionmaker
from ..models.base import Base
from ..services.ai_extract import ai_extraction_service
mvp_bp = Blueprint('mvp', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
# 允许的图片扩展名（用于公司图片/签名/商标）
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _make_safe_approval_no(form_data_obj, fallback: str = "TEST") -> str:
    """Return a filesystem-safe approval_no string for filenames."""
    import re
    if form_data_obj and getattr(form_data_obj, 'approval_no', None):
        approval_no = form_data_obj.approval_no or fallback
    else:
        approval_no = fallback
    safe = re.sub(r'[^a-zA-Z0-9]', '-', approval_no)
    safe = re.sub(r'-+', '-', safe).strip('-')
    return safe or fallback

# 在文件开头添加新的辅助函数
class DocumentGeneratorFactory:
    """文档生成器工厂类"""
    
    def __init__(self):
        self.generators = {
            'if': {
                'type': 'if',
                'name': 'IF',
                'generator': generate_if_document,
                'template': "IF_Template",
                'use_class': False,
                'special_handler': self._handle_if_document
            },
            'cert': {
                'type': 'cert',
                'name': 'CERT',
                'generator': generate_cert_document,
                'template': None,
                'use_class': False
            },
            'rcs': {
                'type': 'rcs',
                'name': 'RCS',
                'generator': RcsGenerator(),
                'template': None,
                'use_class': True
            },
            'other': {
                'type': 'other',
                'name': 'OTHER',
                'generator': OtherGenerator(),
                'template': None,
                'use_class': True
            },
            'tr': {
                'type': 'tr',
                'name': 'TR',
                'generator': TrGenerator(),
                'template': None,
                'use_class': True
            },
            'tm': {
                'type': 'tm',
                'name': 'TM',
                'generator': TmGenerator(),
                'template': None,
                'use_class': True
            },
        }
    
    def get_all_document_types(self):
        """获取所有文档类型配置"""
        return list(self.generators.values())
    
    def get_generator(self, doc_type):
        """获取指定类型的生成器配置"""
        return self.generators.get(doc_type)
    
    def _handle_if_document(self, generator, generation_data, docx_path, template_name, output_format):
        """处理IF文档的特殊逻辑"""
        try:
            # 调用IF生成器函数
            result = generator(generation_data, docx_path, template_name)
            
            # IF生成器返回字典，检查success字段
            if isinstance(result, dict):
                if result.get('success', False):
                    if output_format == 'pdf':
                        # 转换为PDF
                        pdf_filename = os.path.basename(docx_path).replace('.docx', '.pdf')
                        pdf_path = docx_path.replace('.docx', '.pdf')
                        
                        pdf_success = generate_if_pdf_from_docx(docx_path, pdf_path)
                        
                        if pdf_success:
                            return {
                                "success": True,
                                "filename": pdf_filename,
                                "file_path": pdf_path,
                                "download_url": f"/api/mvp/download/{pdf_filename}"
                            }
                        else:
                            return {"success": False, "error": "PDF转换失败"}
                    else:
                        return {
                            "success": True,
                            "filename": os.path.basename(docx_path),
                            "file_path": docx_path,
                            "download_url": f"/api/mvp/download/{os.path.basename(docx_path)}"
                        }
                else:
                    error_msg = result.get('message', result.get('error', 'Word文档生成失败'))
                    return {"success": False, "error": error_msg}
            else:
                return {"success": False, "error": f"IF生成器返回了无效的结果类型: {type(result)}"}
                
        except Exception as e:
            print(f"IF文档处理异常: {str(e)}")
            return {"success": False, "error": f"IF文档处理异常: {str(e)}"}

def _prepare_generation_data(form_data):
    """准备文档生成所需的数据（以表单数据为准，不覆盖）"""
    return {
        # 基本信息字段
        "approval_no": form_data.approval_no,
        "information_folder_no": form_data.information_folder_no,
        "safety_class": form_data.safety_class,
        "pane_desc": form_data.pane_desc,
        "glass_layers": form_data.glass_layers,
        "interlayer_layers": form_data.interlayer_layers,
        "windscreen_thick": form_data.windscreen_thick,
        "interlayer_thick": form_data.interlayer_thick,
        "glass_treatment": form_data.glass_treatment,
        "interlayer_type": form_data.interlayer_type,
        "coating_type": form_data.coating_type,
        "coating_thick": form_data.coating_thick,
        "material_nature": form_data.material_nature,
        "coating_color": form_data.coating_color,
        # 新增字段 - 玻璃颜色和夹层相关
        "glass_color_choice": form_data.glass_color_choice,
        "interlayer_total": form_data.interlayer_total,
        "interlayer_partial": form_data.interlayer_partial,
        "interlayer_colourless": form_data.interlayer_colourless,
        # 新增字段 - 导体和不透明相关
        "conductors_choice": form_data.conductors_choice,
        "opaque_obscure_choice": form_data.opaque_obscure_choice,
        "remarks": form_data.remarks,
        # 报告号
        "report_no": form_data.report_no,
        # 新增日期字段
        "approval_date": form_data.approval_date,
        "test_date": form_data.test_date,
        "report_date": form_data.report_date,
        # 公司信息（从Company表获取最新信息）
        "company_id": form_data.company_id,
        "company_name": form_data.company_name or '',
        "company_address": form_data.company_address or '',
        "trade_names": form_data.trade_names or '',
        "trade_marks": form_data.trade_marks or [],
        "vehicles": form_data.vehicles or [],
        # 设备信息（从Company表获取）
        "equipment": form_data.equipment or [],
        # 系统参数 - 版本号
        "version_1": getattr(form_data, 'version_1', 4),
        "version_2": getattr(form_data, 'version_2', 8),
        "version_3": getattr(form_data, 'version_3', 12),
        "version_4": getattr(form_data, 'version_4', 1),
        # 系统参数 - 实验室环境参数
        "temperature": getattr(form_data, 'temperature', '22°C'),
        "ambient_pressure": getattr(form_data, 'ambient_pressure', '1020 mbar'),
        "relative_humidity": getattr(form_data, 'relative_humidity', '50 %')
    }

def _generate_single_document(doc_info, generation_data, output_dir, safe_approval_no, output_format):
    """生成单个文档"""
    doc_type = doc_info.get('type', 'unknown')
    doc_name = doc_info['name']
    generator = doc_info['generator']
    template_name = doc_info['template']
    use_class = doc_info['use_class']
    special_handler = doc_info.get('special_handler')
    
    try:
        if special_handler:
            # 使用特殊处理器（如IF文档）
            docx_filename = f"{doc_name}-{safe_approval_no}.docx"
            docx_path = os.path.join(output_dir, docx_filename)
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            result = special_handler(generator, generation_data, docx_path, template_name, output_format)
            return result
        
        else:
            # 其他文档类型
            # 根据输出格式确定文件名和路径
            if output_format == 'pdf':
                filename = f"{doc_name}-{safe_approval_no}.pdf"
                file_path = os.path.join(output_dir, filename)
            else:
                filename = f"{doc_name}-{safe_approval_no}.docx"
                file_path = os.path.join(output_dir, filename)
            
            if use_class:
                # 使用生成器类
                result = generator.generate_document(generation_data, file_path, output_format)
                
                if result.get('success'):
                    return {
                        "success": True,
                        "filename": filename,
                        "file_path": file_path,
                        "download_url": f"/api/mvp/download/{filename}"
                    }
                else:
                    return result
            else:
                # 使用生成器函数
                result = generator(generation_data, file_path, output_format)
                
                if result.get('success'):
                    return {
                        "success": True,
                        "filename": filename,
                        "file_path": file_path,
                        "download_url": f"/api/mvp/download/{filename}"
                    }
                else:
                    return result
            
            # 处理生成器返回的结果已经在上面处理了，这里不需要额外处理
                
    except Exception as e:
        print(f"生成异常: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return {"success": False, "error": f"生成失败: {str(e)}"}



@mvp_bp.route('/save-form-data', methods=['POST'])
def save_form_data():
    """保存表单数据"""
    try:

        data = request.get_json()
        session_id = data.get('session_id')
        form_data = data.get('form_data', {})
        
        # 如果session_id为空，自动生成一个正式的session_id
        if not session_id:
            import uuid
            import time
            # 生成格式：session_时间戳_随机UUID
            timestamp = int(time.time())
            random_uuid = uuid.uuid4().hex[:8]
            session_id = f"session_{timestamp}_{random_uuid}"
            print(f"🆔 自动生成session_id: {session_id}")
        
        # 使用FormData.query查询
        existing_form = FormData.query.filter_by(session_id=session_id).first()
        
        if existing_form:
            # 更新现有记录
            print("📝 更新现有记录")
            for key, value in form_data.items():
                # 禁止客户端覆盖创建/更新时间等受控字段
                if key in ['created_at', 'updated_at']:
                    continue
                if hasattr(existing_form, key):
                    # 特殊处理日期字段
                    if key in ['approval_date', 'test_date', 'report_date']:
                        if isinstance(value, str) and value:
                            try:
                                value = datetime.strptime(value, '%Y-%m-%d').date()
                            except ValueError:
                                continue  # 跳过无效日期
                        elif not value:
                            continue  # 跳过空值，保持原有值
                    setattr(existing_form, key, value)
            
            # 更新系统参数
            version_params = system_config.get_version_params()
            lab_params = system_config.get_laboratory_params()
            
            existing_form.version_1 = version_params.get('version_1', 4)
            existing_form.version_2 = version_params.get('version_2', 8)
            existing_form.version_3 = version_params.get('version_3', 12)
            existing_form.version_4 = version_params.get('version_4', 1)
            
            existing_form.temperature = lab_params.get('temperature', '22°C')
            existing_form.ambient_pressure = lab_params.get('ambient_pressure', '1020 mbar')
            existing_form.relative_humidity = lab_params.get('relative_humidity', '50 %')
            
            existing_form.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            print("📝 创建新记录")
            # 处理日期字段
            approval_date = form_data.get('approval_date')
            test_date = form_data.get('test_date')
            report_date = form_data.get('report_date')
            
            # 如果前端传递的是字符串，转换为date对象
            if isinstance(approval_date, str) and approval_date:
                try:
                    approval_date = datetime.strptime(approval_date, '%Y-%m-%d').date()
                except ValueError:
                    approval_date = None
            else:
                approval_date = None
                
            if isinstance(test_date, str) and test_date:
                try:
                    test_date = datetime.strptime(test_date, '%Y-%m-%d').date()
                except ValueError:
                    test_date = None
            else:
                test_date = None
                
            if isinstance(report_date, str) and report_date:
                try:
                    report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
                except ValueError:
                    report_date = None
            else:
                report_date = None
            
            # 获取系统参数
            version_params = system_config.get_version_params()
            lab_params = system_config.get_laboratory_params()
            
            new_form = FormData(
                session_id=session_id,
                # IF_Template.docx 相关字段
                approval_no=form_data.get('approval_no', ''),
                information_folder_no=form_data.get('information_folder_no', ''),
                safety_class=form_data.get('safety_class', ''),
                pane_desc=form_data.get('pane_desc', ''),
                glass_layers=form_data.get('glass_layers', ''),
                interlayer_layers=form_data.get('interlayer_layers', ''),
                windscreen_thick=form_data.get('windscreen_thick', ''),
                interlayer_thick=form_data.get('interlayer_thick', ''),
                glass_treatment=form_data.get('glass_treatment', ''),
                interlayer_type=form_data.get('interlayer_type', ''),
                coating_type=form_data.get('coating_type', ''),
                coating_thick=form_data.get('coating_thick', ''),
                material_nature=form_data.get('material_nature', ''),
                coating_color=form_data.get('coating_color', ''),
                # 新增字段 - 玻璃颜色和夹层相关
                glass_color_choice=form_data.get('glass_color_choice', 'tinted_struck'),
                interlayer_total=form_data.get('interlayer_total', False),
                interlayer_partial=form_data.get('interlayer_partial', False),
                interlayer_colourless=form_data.get('interlayer_colourless', False),
                # 新增字段 - 导体和不透明相关
                conductors_choice=form_data.get('conductors_choice', 'yes_struck'),
                opaque_obscure_choice=form_data.get('opaque_obscure_choice', 'yes_struck'),
                remarks=form_data.get('remarks', ''),
                report_no=form_data.get('report_no', ''),
                company_id=form_data.get('company_id'),
                company_name=form_data.get('company_name', ''),
                company_address=form_data.get('company_address', ''),
                trade_names=form_data.get('trade_names', ''),
                trade_marks=form_data.get('trade_marks', []),
                equipment=form_data.get('equipment', []),
                vehicles=form_data.get('vehicles', []),
                # 新增日期字段
                approval_date=approval_date,
                test_date=test_date,
                report_date=report_date,
                # 系统参数 - 版本号
                version_1=version_params.get('version_1', 4),
                version_2=version_params.get('version_2', 8),
                version_3=version_params.get('version_3', 12),
                version_4=version_params.get('version_4', 1),
                # 系统参数 - 实验室环境参数
                temperature=lab_params.get('temperature', '22°C'),
                ambient_pressure=lab_params.get('ambient_pressure', '1020 mbar'),
                relative_humidity=lab_params.get('relative_humidity', '50 %')
            )
            db.session.add(new_form)
        
        db.session.commit()
        print("✅ 数据保存成功")
        
        return jsonify({
            "success": True,
            "message": "表单数据保存成功",
            "data": {
                "saved_at": datetime.utcnow().isoformat(),
                "version": "1.0",
                "session_id": session_id,  # 返回session_id，包括新生成的正式ID
            }
        })
        
    except Exception as e:
        print(f"❌ 保存表单数据失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": f"保存表单数据失败: {str(e)}"}), 500

@mvp_bp.route('/get-form-data/<session_id>', methods=['GET'])
def get_form_data(session_id):
    """获取表单数据"""
    try:
        form_data = FormData.query.filter_by(session_id=session_id).first()
        
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        return jsonify({
            "success": True,
            "data": {
                "session_id": form_data.session_id,
                
                # IF_Template.docx 相关字段
                "approval_no": form_data.approval_no,
                "information_folder_no": form_data.information_folder_no,
                "safety_class": form_data.safety_class,
                "pane_desc": form_data.pane_desc,
                "glass_layers": form_data.glass_layers,
                "interlayer_layers": form_data.interlayer_layers,
                "windscreen_thick": form_data.windscreen_thick,
                "interlayer_thick": form_data.interlayer_thick,
                "glass_treatment": form_data.glass_treatment,
                "interlayer_type": form_data.interlayer_type,
                "coating_type": form_data.coating_type,
                "coating_thick": form_data.coating_thick,
                "material_nature": form_data.material_nature,
                "coating_color": form_data.coating_color,
                "remarks": form_data.remarks,
                "report_no": form_data.report_no,
                "company_id": form_data.company_id,
                "company_name": form_data.company_name,
                "company_address": form_data.company_address,
                "trade_names": form_data.trade_names,
                "trade_marks": form_data.trade_marks or [],
                "vehicles": form_data.vehicles or [],
                # 新增日期字段
                "approval_date": form_data.approval_date.isoformat() if form_data.approval_date else None,
                "test_date": form_data.test_date.isoformat() if form_data.test_date else None,
                "report_date": form_data.report_date.isoformat() if form_data.report_date else None,
                "status": form_data.status,
                "created_at": form_data.created_at.isoformat(),
                "updated_at": form_data.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"❌ 获取表单数据失败: {str(e)}")
        return jsonify({"error": f"获取表单数据失败: {str(e)}"}), 500




@mvp_bp.route('/generate-documents', methods=['POST'])
def generate_all_documents():
    """生成所有类型的文档"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        output_format = data.get('output_format', 'docx')  # docx 或 pdf
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取表单数据
        form_data = FormData.query.filter_by(session_id=session_id).first()
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        # 准备生成数据
        generation_data = _prepare_generation_data(form_data)
        
        # 处理Approval_No生成文件名
        safe_approval_no = _make_safe_approval_no(form_data)
        
        # 确保输出目录存在
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用工厂类获取所有文档类型配置
        factory = DocumentGeneratorFactory()
        all_document_types = factory.get_all_document_types()
        
        # 生成所有类型的文档
        generated_files = []
        failed_documents = []
        
        for doc_info in all_document_types:
            result = _generate_single_document(
                doc_info, generation_data, output_dir, safe_approval_no, output_format
            )
            
            if result['success']:
                generated_files.append({
                    "type": doc_info['name'],
                    "filename": result['filename'],
                    "file_path": result['file_path'],
                    "download_url": result['download_url']
                })
            else:
                failed_documents.append({"type": doc_info['name'], "error": result['error']})
        
        # 返回生成结果
        if generated_files:
            # 创建ZIP文件
            zip_filename = f"documents_{safe_approval_no}_{output_format}.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_info in generated_files:
                        if os.path.exists(file_info['file_path']):
                            # 在ZIP中使用原始文件名
                            zipf.write(file_info['file_path'], file_info['filename'])
                
                return jsonify({
                    "success": True,
                    "message": f"成功生成 {len(generated_files)} 个文档并打包为ZIP",
                    "data": {
                        "filename": zip_filename,
                        "file_path": zip_path,
                        "download_url": f"/api/mvp/download/{zip_filename}",
                        "generated_files": generated_files,
                        "failed_documents": failed_documents,
                        "total_requested": len(all_document_types),
                        "total_success": len(generated_files),
                        "total_failed": len(failed_documents)
                    }
                })
            except Exception as zip_error:
                print(f"❌ 创建ZIP文件失败: {str(zip_error)}")
                return jsonify({
                    "success": False,
                    "error": f"创建ZIP文件失败: {str(zip_error)}",
                    "data": {
                        "generated_files": generated_files,
                        "failed_documents": failed_documents,
                        "total_requested": len(all_document_types),
                        "total_success": len(generated_files),
                        "total_failed": len(failed_documents)
                    }
                }), 500
        else:
            return jsonify({
                "success": False,
                "error": "所有文档生成失败",
                "data": {
                    "failed_documents": failed_documents,
                    "total_requested": len(all_document_types),
                    "total_failed": len(failed_documents)
                }
            }), 500
        
    except Exception as e:
        print(f"❌ 生成所有文档失败: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"生成所有文档失败: {str(e)}"}), 500

# ===================== 上传文件接口（整合到 /mvp 下） =====================

@mvp_bp.route('/upload-file', methods=['POST'])
def upload_file():
    """通用文件上传接口

    前端约定：
    - category: 文件分类，目前支持 'company'
    - subcategory: 子分类，'marks' | 'picture' | 'signature'
    - file: 表单文件字段名
    返回可通过 GET /uploads/<path> 直接访问的 URL
    """
    try:
        # 校验文件
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "未找到上传的文件字段(file)"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "未选择文件"}), 400

        # 读取分类参数
        category = request.form.get('category', 'company')
        subcategory = request.form.get('subcategory', '').lower()  # marks/picture/signature

        # 仅支持公司相关图片上传
        if category != 'company':
            return jsonify({"success": False, "error": "不支持的分类"}), 400

        if subcategory not in {'marks', 'picture', 'signature'}:
            return jsonify({"success": False, "error": "无效的子分类"}), 400

        # 校验图片类型
        if not allowed_image_file(file.filename):
            return jsonify({"success": False, "error": "不支持的图片类型"}), 400

        # 生成安全文件名
        original_name = file.filename
        filename = secure_filename(original_name)

        # 添加时间戳与UUID，避免重名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{subcategory}_{timestamp}_{unique_id}_{filename}"

        # 保存路径：uploads/company/<subcategory>/
        base_dir = current_app.config['UPLOAD_FOLDER']
        save_dir = os.path.join(base_dir, 'company', subcategory)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        # 保存文件
        file.save(file_path)

        # 生成对外可访问的 URL（由 main.py 的 /uploads/<path> 提供）
        public_path = f"company/{subcategory}/{filename}"
        public_url = f"/uploads/{public_path}"

        # 补充文件信息
        size = os.path.getsize(file_path)
        mime_type = 'image/' + filename.rsplit('.', 1)[1].lower()

        return jsonify({
            "success": True,
            "message": "文件上传成功",
            "data": {
                "url": public_url,
                "filename": filename,
                "original_name": original_name,
                "category": category,
                "subcategory": subcategory,
                "size": size,
                "mime_type": mime_type
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"上传失败: {str(e)}"}), 500

@mvp_bp.route('/generate-if', methods=['POST'])
def generate_if():
    """生成IF文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        output_format = data.get('output_format') or data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('if', session_id, output_format)
        
    except Exception as e:
        print(f"🔥 IF文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"IF文档生成接口异常: {str(e)}"}), 500
# ========== 新增：多类型测试文档生成接口 ==========

@mvp_bp.route('/generate-cert', methods=['POST'])
def generate_cert():
    """生成CERT文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('cert', session_id, format_type)
        
    except Exception as e:
        print(f"🔥 CERT文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"CERT文档生成接口异常: {str(e)}"}), 500


@mvp_bp.route('/generate-other', methods=['POST'])
def generate_other():
    """生成OTHER文档"""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        return _generate_single_document_by_type('other', session_id, format_type)
        
    except Exception as e:
        print(f"🔥 OTHER文档生成接口异常: {str(e)}")
        import traceback
        print(f"🔍 错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"OTHER文档生成接口异常: {str(e)}"}), 500


@mvp_bp.route('/generate-tr', methods=['POST'])
def generate_tr():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备TR测试报告数据（使用通用生成数据，确保包含equipment等最新公司信息）
        if form_data:
            tr_data = _prepare_generation_data(form_data)
        else:
            # 使用示例数据
            tr_data = create_tr_sample_data()

        # 调试输出：TR即将使用的设备信息
        try:
            eq = tr_data.get('equipment', []) if isinstance(tr_data, dict) else []
            eq_preview = eq[:3] if isinstance(eq, list) else []
            print(f"[DEBUG] TR generate endpoint equipment count={len(eq) if isinstance(eq, list) else 0}, preview={eq_preview}")
        except Exception:
            pass
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        
        # 使用安全的approval_no生成文件名
        if form_data:
            safe_approval_no = _make_safe_approval_no(form_data, 'TR-2024-001')
        else:
            safe_approval_no = 'TR-2024-001'
            
        filename = f"TR-{safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成TR测试报告
        result = generate_tr_document(tr_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "TR测试报告生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        return jsonify({"error": f"TR测试报告生成失败: {str(e)}"}), 500


@mvp_bp.route('/generate-review-control-sheet', methods=['POST'])
def generate_review_control_sheet():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备RCS审查控制表数据
        rcs_data = {}
        if form_data:
            rcs_data = {
                # 必需的变量
                'report_no': form_data.report_no or 'RCS-REPORT-2024-001',
                'approval_no': form_data.approval_no or 'RCS-APPROVAL-2024-001',
                'company_name': form_data.company_name or '示例企业名称',
                'windscreen_thick': form_data.windscreen_thick or '5.0mm',
            }
        else:
            # 使用示例数据
            rcs_data = create_rcs_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        approval_no = form_data.approval_no if form_data else 'RCS-2024-001'
        # 使用安全文件名，避免特殊字符导致的文件系统错误
        safe_approval_no = _make_safe_approval_no(form_data, 'RCS-2024-001')
        filename = f"Review Control Sheet V7 {safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成RCS审查控制表
        result = generate_rcs_document(rcs_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "RCS审查控制表生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"RCS审查控制表生成失败: {str(e)}"}), 500


@mvp_bp.route('/generate-tm', methods=['POST'])
def generate_tm():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        format_type = data.get('format', 'docx')  # 支持docx和pdf格式
        form_data = FormData.query.filter_by(session_id=session_id).first() if session_id else None
        
        # 准备TM测试记录数据
        tm_data = {}
        if form_data:
            # 获取公司简称
            company_contraction = ''
            if form_data.company_id:
                from ..models.company import Company
                company = Company.query.get(form_data.company_id)
                if company:
                    company_contraction = company.company_contraction or ''
            
            # 只保留模板中实际存在的变量
            tm_data = {
                'test_date': form_data.test_date,
                'windscreen_thick': form_data.windscreen_thick,
                'glass_layers': form_data.glass_layers,
                'interlayer_layers': form_data.interlayer_layers,
                'interlayer_thick': form_data.interlayer_thick,
                'glass_treatment': form_data.glass_treatment,
                'interlayer_type': form_data.interlayer_type,
                'coating_type': form_data.coating_type,
                'coating_thick': form_data.coating_thick,
                'material_nature': form_data.material_nature,
                'coating_color': form_data.coating_color,
                'interlayer_total': form_data.interlayer_total,
                'conductors_choice': form_data.conductors_choice,
                'opaque_obscure_choice': form_data.opaque_obscure_choice,
                'glass_color_choice': form_data.glass_color_choice,
                'company_contraction': company_contraction
            }
        else:
            # 使用示例数据
            tm_data = create_tm_sample_data()
        
        # 生成输出路径
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        file_ext = '.pdf' if format_type == 'pdf' else '.docx'
        
        # 使用安全的approval_no生成文件名
        if form_data:
            safe_approval_no = _make_safe_approval_no(form_data, 'TM-2024-001')
        else:
            safe_approval_no = 'TM-2024-001'
            
        filename = f"TM-{safe_approval_no}{file_ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 生成TM测试记录
        result = generate_tm_document(tm_data, output_path, format_type)
        
        if result["success"]:
            payload = {
                "filename": filename,
                "file_path": output_path,
                "download_url": f"/api/mvp/download/{filename}"
            }
            return jsonify({"success": True, "message": "TM测试记录生成成功", "data": payload})
        else:
            return jsonify({"error": result["message"]}), 500
            
    except Exception as e:
        return jsonify({"error": f"TM测试记录生成失败: {str(e)}"}), 500



def _generate_single_document_by_type(doc_type, session_id, output_format='docx'):
    """通用的单文档生成函数"""
    try:
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取表单数据
        form_data = FormData.query.filter_by(session_id=session_id).first()
        if not form_data:
            return jsonify({"error": "未找到表单数据"}), 404
        
        # 准备生成数据
        generation_data = _prepare_generation_data(form_data)
        
        # 处理Approval_No生成文件名
        safe_approval_no = _make_safe_approval_no(form_data)
        
        # 确保输出目录存在
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files')
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用工厂类获取文档配置
        factory = DocumentGeneratorFactory()
        doc_config = factory.get_generator(doc_type)
        
        if not doc_config:
            return jsonify({"error": f"{doc_type.upper()}文档生成器配置不存在"}), 500
        
        # 生成文档
        result = _generate_single_document(
            doc_config, generation_data, output_dir, safe_approval_no, output_format
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": f"{doc_config['name']} {output_format.upper()}文档生成成功",
                "data": {
                    "filename": result['filename'],
                    "file_path": result['file_path'],
                    "download_url": result['download_url']
                }
            })
        else:
            return jsonify({"error": result['error']}), 500
        
    except Exception as e:
        print(f"❌ 生成{doc_type.upper()}文档失败: {str(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"生成{doc_type.upper()}文档失败: {str(e)}"}), 500

@mvp_bp.route('/download/<filename>', methods=['GET'])
def download_generated_document(filename):
    """下载生成的文档"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({"error": "无效的文件名"}), 400
        
        # 构建文件路径
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files', filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({"error": "文件不存在"}), 404
        
        # 检查文件是否为普通文件
        if not os.path.isfile(file_path):
            return jsonify({"error": "无效的文件"}), 400
        
        # 使用 send_file 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        print(f"❌ 下载文件失败: {str(e)}")
        return jsonify({"error": f"下载失败: {str(e)}"}), 500
        
@mvp_bp.route('/ai-extract', methods=['POST'])
def ai_extract_document():
    """AI文档信息提取"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "未找到上传的文件"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "未选择文件"
            }), 400
        
        # 检查文件类型
        allowed_extensions = {'.doc', '.docx', '.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                "success": False,
                "error": f"不支持的文件类型: {file_ext}，仅支持: {', '.join(allowed_extensions)}"
            }), 400
        
        # 保存上传的文件到临时目录
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'temp')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        temp_filename = f"{uuid.uuid4()}_{file.filename}"
        temp_file_path = os.path.join(upload_dir, temp_filename)
        
        try:
            file.save(temp_file_path)
            
            # 调用提取服务
            extraction_result = ai_extraction_service.extract_from_document(temp_file_path)
            
            if extraction_result["success"]:
                return jsonify({
                    "success": True,
                    "message": "提取成功",
                    "data": extraction_result["data"]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": extraction_result.get("error", "提取失败")
                }), 500
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        current_app.logger.error(f"提取失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"提取失败: {str(e)}"
        }), 500 