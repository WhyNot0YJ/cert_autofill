from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime
from ..models import Document, DocumentUpload, FormData
from ..services.ai_extract import ai_extraction_service
from ..services.extract import extract_fields
from ..services.generate import generate_document
from ..main import db
from sqlalchemy.orm import sessionmaker
from ..models.base import Base

mvp_bp = Blueprint('mvp', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@mvp_bp.route('/upload-documents', methods=['POST'])
def upload_documents():
    """上传申请书和检测报告"""
    try:
        # 检查文件
        if 'application_file' not in request.files or 'report_file' not in request.files:
            return jsonify({"error": "请上传申请书和检测报告文件"}), 400
        
        application_file = request.files['application_file']
        report_file = request.files['report_file']
        
        if application_file.filename == '' or report_file.filename == '':
            return jsonify({"error": "请选择文件"}), 400
        
        if not (allowed_file(application_file.filename) and allowed_file(report_file.filename)):
            return jsonify({"error": "不支持的文件格式"}), 400
        
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 保存申请书文件
        application_filename = secure_filename(application_file.filename)
        application_stored_name = f"{session_id}_application_{application_filename}"
        application_path = os.path.join(current_app.config['UPLOAD_FOLDER'], application_stored_name)
        application_file.save(application_path)
        
        # 保存检测报告文件
        report_filename = secure_filename(report_file.filename)
        report_stored_name = f"{session_id}_report_{report_filename}"
        report_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report_stored_name)
        report_file.save(report_path)
        
        # 创建文档记录
        application_doc = Document(
            title=f"申请书 - {application_filename}",
            document_type='application'
        )
        db.session.add(application_doc)
        db.session.flush()
        
        report_doc = Document(
            title=f"检测报告 - {report_filename}",
            document_type='report'
        )
        db.session.add(report_doc)
        db.session.flush()
        
        # 创建上传记录
        application_upload = DocumentUpload(
            document_id=application_doc.id,
            original_filename=application_filename,
            stored_filename=application_stored_name,
            file_path=application_path,
            file_size=os.path.getsize(application_path),
            file_type=application_filename.rsplit('.', 1)[1].lower()
        )
        db.session.add(application_upload)
        
        report_upload = DocumentUpload(
            document_id=report_doc.id,
            original_filename=report_filename,
            stored_filename=report_stored_name,
            file_path=report_path,
            file_size=os.path.getsize(report_path),
            file_type=report_filename.rsplit('.', 1)[1].lower()
        )
        db.session.add(report_upload)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "文件上传成功",
            "data": {
                "application_doc_id": application_doc.id,
                "report_doc_id": report_doc.id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"文件上传失败: {str(e)}"}), 500

@mvp_bp.route('/extract-info', methods=['POST'])
def extract_info():
    """使用AI提取文档信息"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取上传的文档
        application_upload = DocumentUpload.query.filter(
            DocumentUpload.stored_filename.like(f"{session_id}_application_%")
        ).first()
        
        report_upload = DocumentUpload.query.filter(
            DocumentUpload.stored_filename.like(f"{session_id}_report_%")
        ).first()
        
        if not application_upload or not report_upload:
            return jsonify({"error": "未找到上传的文档"}), 404
        
        # 提取文档文本
        try:
            # 尝试从文件路径读取文本
            with open(application_upload.file_path, 'r', encoding='utf-8') as f:
                application_text = f.read()
        except:
            # 如果读取失败，使用默认文本
            application_text = "申请书内容无法读取，请手动填写信息"
            
        try:
            with open(report_upload.file_path, 'r', encoding='utf-8') as f:
                report_text = f.read()
        except:
            # 如果读取失败，使用默认文本
            report_text = "检测报告内容无法读取，请手动填写信息"
        
        # 使用AI提取信息（如果API key不可用，使用模拟数据）
        try:
            extraction_result = ai_extraction_service.extract_from_documents(
                application_text, report_text
            )
        except Exception as ai_error:
            # 如果AI提取失败，使用模拟数据
            extraction_result = {
                "success": True,
                "data": {
                    "enterprise_info": {
                        "name": "请填写企业名称",
                        "english_name": "请填写企业英文名",
                        "registration_number": "请填写注册号",
                        "legal_representative": "请填写法定代表人",
                        "contact_person": "请填写联系人",
                        "contact_phone": "请填写联系电话",
                        "contact_email": "请填写联系邮箱",
                        "address": "请填写地址"
                    },
                    "certification_info": {
                        "type": "请填写认证类型",
                        "product_name": "请填写产品名称",
                        "product_model": "请填写产品型号",
                        "scope": "请填写认证范围"
                    },
                    "technical_specs": {
                        "specifications": "请填写技术规格参数"
                    },
                    "test_info": {
                        "standards": "请填写测试标准",
                        "results": "请填写测试结果"
                    },
                    "certificate_info": {
                        "number": "请填写证书编号",
                        "issue_date": "请填写发证日期",
                        "expiry_date": "请填写有效期至",
                        "authority": "请填写发证机构"
                    },
                    "additional_info": {
                        "remarks": "请填写备注信息"
                    }
                },
                "raw_response": "使用模拟数据（AI API不可用）"
            }
        
        # 更新上传记录
        application_upload.ai_extraction_result = extraction_result.get('raw_response', '')
        application_upload.extracted_data = extraction_result.get('data', {})
        application_upload.upload_status = 'completed'
        
        report_upload.ai_extraction_result = extraction_result.get('raw_response', '')
        report_upload.extracted_data = extraction_result.get('data', {})
        report_upload.upload_status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "信息提取完成（使用模拟数据）",
            "data": extraction_result.get('data', {})
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"信息提取失败: {str(e)}"}), 500

@mvp_bp.route('/save-form-data', methods=['POST'])
def save_form_data():
    """保存表单数据"""
    try:
        print("=== 保存表单数据调试信息 ===")
        print(f"请求方法: {request.method}")
        print(f"请求头: {dict(request.headers)}")
        print(f"请求体: {request.get_data(as_text=True)}")
        
        data = request.get_json()
        print(f"解析后的JSON数据: {data}")
        
        session_id = data.get('session_id')
        form_data = data.get('form_data', {})
        
        print(f"session_id: {session_id}")
        print(f"form_data: {form_data}")
        
        # 如果session_id为空，生成一个临时的session_id（用于测试模式）
        if not session_id:
            print("🔄 生成临时会话ID（测试模式）")
            import uuid
            session_id = f"test_session_{uuid.uuid4().hex[:8]}"
            print(f"生成的临时session_id: {session_id}")
        
        # 使用FormData.query查询
        existing_form = FormData.query.filter_by(session_id=session_id).first()
        
        if existing_form:
            # 更新现有记录
            print("📝 更新现有记录")
            for key, value in form_data.items():
                if hasattr(existing_form, key):
                    setattr(existing_form, key, value)
            existing_form.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            print("📝 创建新记录")
            new_form = FormData(
                session_id=session_id,
                title=form_data.get('title', ''),
                # IF_Template_2.docx 相关字段
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
                remarks=form_data.get('remarks', ''),
                company_name=form_data.get('company_name', ''),
                vehicles=form_data.get('vehicles', []),
                status=form_data.get('status', 'draft')
            )
            db.session.add(new_form)
        
        db.session.commit()
        print("✅ 数据保存成功")
        
        return jsonify({
            "success": True,
            "message": "表单数据保存成功",
            "session_id": session_id  # 返回session_id，包括新生成的临时ID
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
                "title": form_data.title,
                # IF_Template_2.docx 相关字段
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
                "vehicles": form_data.vehicles or [],
                "status": form_data.status,
                "created_at": form_data.created_at.isoformat(),
                "updated_at": form_data.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"❌ 获取表单数据失败: {str(e)}")
        return jsonify({"error": f"获取表单数据失败: {str(e)}"}), 500

@mvp_bp.route('/generate-documents', methods=['POST'])
def generate_documents():
    """生成交付文档"""
    try:
        print("=== 生成文档调试信息 ===")
        data = request.get_json()
        session_id = data.get('session_id')
        output_format = data.get('output_format', 'docx')  # docx 或 pdf
        
        print(f"session_id: {session_id}")
        print(f"output_format: {output_format}")
        
        if not session_id:
            return jsonify({"error": "缺少会话ID"}), 400
        
        # 获取表单数据
        form_data = FormData.query.filter_by(session_id=session_id).first()
        
        if not form_data:
            # 如果是测试模式，使用默认数据
            if session_id.startswith('test_session_'):
                print("🔄 使用测试模式默认数据")
                generation_data = {
                    "approval_no": "TEST-2024-001",
                    "information_folder_no": "IF-001",
                    "safety_class": "A",
                    "pane_desc": "测试玻璃板描述",
                    "glass_layers": "5",
                    "interlayer_layers": "1",
                    "windscreen_thick": "5mm",
                    "interlayer_thick": "10mm",
                    "glass_treatment": "涂层处理",
                    "interlayer_type": "PVB",
                    "coating_type": "UV涂层",
                    "coating_thick": "50μm",
                    "material_nature": "钢化玻璃",
                    "coating_color": "透明",
                    "remarks": "这是测试数据，用于验证文档生成功能",
                    "vehicles": [
                        {
                            "veh_mfr": "测试制造商1",
                            "veh_type": "轿车",
                            "veh_cat": "M1",
                            "dev_area": "前风窗",
                            "seg_height": "100mm",
                            "curv_radius": "500mm",
                            "inst_angle": "45°",
                            "seat_angle": "30°",
                            "rpoint_coords": "100,200",
                            "dev_desc": "测试车辆1的开发描述"
                        }
                    ]
                }
            else:
                return jsonify({"error": "未找到表单数据"}), 404
        else:
            # 准备生成数据
            generation_data = {
                # IF_Template_2.docx 相关字段
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
                "vehicles": form_data.vehicles or []
            }
        
        print(f"生成数据: {generation_data}")
        
        # 生成文档
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'pdf':
            # 先生成Word文档，再转换为PDF
            docx_filename = f"IF_Template_{session_id}_{timestamp}.docx"
            docx_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files', docx_filename)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(docx_path), exist_ok=True)
            
            print(f"生成Word文档路径: {docx_path}")
            
            # 生成Word文档 - 使用多模板合并方案
            from ..services.generate import generate_if_template_document
            success = generate_if_template_document(generation_data, docx_path, "IF_Template_Auto")
            
            if success:
                # 转换为PDF
                pdf_filename = f"IF_Template_{session_id}_{timestamp}.pdf"
                pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files', pdf_filename)
                
                print(f"生成PDF文档路径: {pdf_path}")
                
                from ..services.generate import generate_pdf_from_docx
                pdf_success = generate_pdf_from_docx(docx_path, pdf_path)
                
                if pdf_success:
                    return jsonify({
                        "success": True,
                        "message": "PDF文档生成成功",
                        "data": {
                            "filename": pdf_filename,
                            "file_path": pdf_path,
                            "download_url": f"/api/download/{pdf_filename}"
                        }
                    })
                else:
                    return jsonify({"error": "PDF转换失败"}), 500
            else:
                return jsonify({"error": "Word文档生成失败"}), 500
        else:
            # 生成Word文档
            docx_filename = f"IF_Template_{session_id}_{timestamp}.docx"
            docx_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'generated_files', docx_filename)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(docx_path), exist_ok=True)
            
            print(f"生成Word文档路径: {docx_path}")
            
            # 生成Word文档 - 使用多模板合并方案
            from ..services.generate import generate_if_template_document
            success = generate_if_template_document(generation_data, docx_path, "IF_Template_Auto")
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Word文档生成成功",
                    "data": {
                        "filename": docx_filename,
                        "file_path": docx_path,
                        "download_url": f"/api/download/{docx_filename}"
                    }
                })
            else:
                return jsonify({"error": "Word文档生成失败"}), 500
        
    except Exception as e:
        print(f"❌ 生成文档失败: {str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": f"生成文档失败: {str(e)}"}), 500 