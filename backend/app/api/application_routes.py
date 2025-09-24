from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from ..main import db
from ..models.form_data import FormData

application_bp = Blueprint('application', __name__)


@application_bp.route('/applications', methods=['GET'])
def list_applications():
    """获取申请书列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search')

        query = FormData.query

        # 已移除状态用法：忽略传入的 status 过滤

        if search:
            search_filter = or_(
                FormData.session_id.contains(search),
                FormData.company_name.contains(search),
                FormData.approval_no.contains(search),
                FormData.information_folder_no.contains(search)
            )
            query = query.filter(search_filter)

        items = query.order_by(FormData.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        result = {
            "success": True,
            "data": {
                "applications": [],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": items.total,
                    "pages": items.pages
                }
            }
        }

        for f in items.items:
            result["data"]["applications"].append({
                "id": f.id,
                # 用 session_id 充当 application_number，便于追踪
                "application_number": f.session_id,
                # 推断申请类型：如需更准确可从字段或前端传入
                # 移除认证类型与状态
                "company_name": f.company_name,
                "approval_no": f.approval_no,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.updated_at.isoformat() if f.updated_at else None,
                "submitted_at": None
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"获取申请书列表失败: {str(e)}"}), 500


@application_bp.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id: int):
    """获取单个申请书详情（读取 FormData）"""
    try:
        f = FormData.query.get(application_id)
        if not f:
            return jsonify({"error": "申请书不存在"}), 404

        data = {
            "id": f.id,
            "application_number": f.session_id,
            # 移除认证类型与状态
            "company_name": f.company_name,
            "company_address": f.company_address,
            "approval_no": f.approval_no,
            "information_folder_no": f.information_folder_no,
            "approval_date": f.approval_date.isoformat() if getattr(f, 'approval_date', None) else None,
            "test_date": f.test_date.isoformat() if getattr(f, 'test_date', None) else None,
            "report_date": f.report_date.isoformat() if getattr(f, 'report_date', None) else None,
            "regulation_update_date": f.regulation_update_date.isoformat() if getattr(f, 'regulation_update_date', None) else None,
            "windscreen_thick": f.windscreen_thick,
            "interlayer_thick": f.interlayer_thick,
            "glass_layers": f.glass_layers,
            "interlayer_layers": f.interlayer_layers,
            "interlayer_type": f.interlayer_type,
            "glass_treatment": f.glass_treatment,
            "coating_type": f.coating_type,
            "coating_thick": f.coating_thick,
            "coating_color": f.coating_color,
            "material_nature": f.material_nature,
            "safety_class": f.safety_class,
            "pane_desc": f.pane_desc,
            "vehicles": f.vehicles or [],
            "remarks": f.remarks,
            "trade_names": f.trade_names,
            "trade_marks": f.trade_marks or [],
            "glass_type": getattr(f, 'glass_type', ''),
            # 系统参数 - 版本号（字符串）
            "version_1": getattr(f, 'version_1', '4'),
            "version_2": getattr(f, 'version_2', '8'),
            "version_3": getattr(f, 'version_3', '12'),
            "version_4": getattr(f, 'version_4', '01'),
            # 系统参数 - 实验室环境参数
            "temperature": getattr(f, 'temperature', '22°C'),
            "ambient_pressure": getattr(f, 'ambient_pressure', '1020 mbar'),
            "relative_humidity": getattr(f, 'relative_humidity', '50 %'),
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
            "submitted_at": None,
            "approved_at": None
        }
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"error": f"获取申请书详情失败: {str(e)}"}), 500


@application_bp.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id: int):
    """删除申请书（删除 FormData 记录）"""
    try:
        f = FormData.query.get(application_id)
        if not f:
            return jsonify({"error": "申请书不存在"}), 404
        db.session.delete(f)
        db.session.commit()
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"删除申请书失败: {str(e)}"}), 500

