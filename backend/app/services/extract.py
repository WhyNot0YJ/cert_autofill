import os
import tempfile
from typing import Dict, Any
from docx import Document
import PyPDF2
import io

def extract_fields(file) -> Dict[str, Any]:
    """
    从上传的文档中提取字段信息
    
    Args:
        file: 上传的文件对象
        
    Returns:
        Dict[str, Any]: 提取的字段信息
    """
    filename = file.filename.lower()
    
    if filename.endswith('.docx'):
        return extract_from_docx(file)
    elif filename.endswith('.doc'):
        return extract_from_doc(file)
    elif filename.endswith('.pdf'):
        return extract_from_pdf(file)
    else:
        raise ValueError(f"不支持的文件格式: {filename}")

def extract_from_docx(file) -> Dict[str, Any]:
    """从Word文档中提取字段"""
    try:
        # 保存上传的文件到临时位置
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            file.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # 读取Word文档
        doc = Document(tmp_file_path)
        
        # 提取文本内容
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text.strip())
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        # 解析字段（这里可以根据实际文档格式进行调整）
        fields = parse_document_fields('\n'.join(text_content))
        
        return {
            "success": True,
            "fields": fields,
            "raw_text": text_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_from_doc(file) -> Dict[str, Any]:
    """从旧版Word文档中提取字段"""
    # 对于.doc文件，可以转换为.docx后处理
    # 这里简化处理，返回基本信息
    return {
        "success": True,
        "fields": {
            "document_type": "Word文档(.doc)",
            "filename": file.filename,
            "note": "需要转换为.docx格式进行详细解析"
        },
        "raw_text": ["旧版Word文档，建议转换为.docx格式"]
    }

def extract_from_pdf(file) -> Dict[str, Any]:
    """从PDF文件中提取字段"""
    try:
        # 读取PDF文件
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        
        # 提取文本内容
        text_content = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text.strip():
                text_content.append(text.strip())
        
        # 解析字段
        fields = parse_document_fields('\n'.join(text_content))
        
        return {
            "success": True,
            "fields": fields,
            "raw_text": text_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def parse_document_fields(text: str) -> Dict[str, str]:
    """
    解析文档文本，提取关键字段
    基于cert_autofill项目的字段提取逻辑
    """
    import re
    
    patterns = {
        "approval_no": r"approval no\.?\s*[:：]\s*([^\n\r]+)",
        "information_folder_no": r"information folder number\s*[:：]\s*([^\n\r]+)",
        "safety_class": r"safety-glass pane\s*[:：]\s*([^\n\r]+)",
        "pane_desc": r"description of glass pane\s*[:：]\s*([^\n\r]+)",
        "glass_layers": r"layers of glass\s*[:：]\s*([^\n\r]+)",
        "interlayer_layers": r"layers of interlayer\s*[:：]\s*([^\n\r]+)",
        "windscreen_thick": r"thickness of the windscreen\s*[:：]\s*([^\n\r]+)",
        "interlayer_thick": r"thickness of interlayer\(s\)\s*[:：]\s*([^\n\r]+)",
        "glass_treatment": r"treatment of glass\s*[:：]\s*([^\n\r]+)",
        "interlayer_type": r"type of interlayer\(s\)\s*[:：]\s*([^\n\r]+)",
        "coating_type": r"type of plastics coating\(s\)\s*[:：]\s*([^\n\r]+)",
        "coating_thick": r"thickness of plastic(?:s)? coating\(s\)\s*[:：]\s*([^\n\r]+)",
        "material_nature": r"nature of( the)? material[^:]*[:：]\s*([^:\n\r]+?)(?=\s*(?:colouring|$))",
        "coating_color": r"colouring of plastics coating\(s\)[^:]*[:：]\s*([^:\n\r]+?)(?=\s*(?:colouring|conductors|$))",
        "remarks": r"remark(?:s)?[^:]*[:：]\s*([^:\n\r]+?)(?=\s*(?:$))",
        "veh_mfr": r"vehicle manufacturer[^:]*[:：]\s*([^:\n\r]+?)(?=\s*(?:type of vehicle|vehicle category|$))",
        "veh_type": r"type of vehicle\s*[:：]\s*([^\n\r]+)",
        "veh_cat": r"vehicle category\s*[:：]\s*([^\n\r]+)",
        "dev_area": r"developed area[^:]*[:：]\s*([^\n\r]+)",
        "seg_height": r"height of segment[^:]*[:：]\s*([^\n\r]+)",
        "curv_radius": r"curvature[^:]*[:：]\s*([^\n\r]+)",
        "inst_angle": r"installation angle[^:]*[:：]\s*([^\n\r]+)",
        "seat_angle": r"seat[\s-]?back angle[^:]*[:：]\s*([^\n\r]+)",
        "rpoint_coords": r"r[\s-]?point co[\s-]?ordinates.*?[:：]\s*([A-Z][:：]\s*[^\n\r]+(?:\s+[A-Z][:：]\s*[^\n\r]+)*)",
        "dev_desc": r"description of the commercially available specific device.*\n[ \t]*[:：][ \t]*(.+)",
    }
    
    unit_fields = [
        'windscreen_thick', 'interlayer_thick', 'coating_thick', 'dev_area', 'seg_height', 'curv_radius', 'inst_angle', 'seat_angle', 'rpoint_coords'
    ]
    
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if key == 'veh_mfr' and match:
            value = match.group(1).strip()
        else:
            value = match.group(2).strip() if key == 'material_nature' and match else (match.group(1).strip() if match else "")
        
        if key in unit_fields and key != 'rpoint_coords':
            value = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", value)
        
        # 清理格式
        value = re.sub(r"(\d+)\s*°", r"\1°", value)
        value = re.sub(r"([^\s])\(", r"\1 (", value)
        value = re.sub(r"\(\s*", "(", value)
        value = re.sub(r"\s*\)", ")", value)
        value = re.sub(r":(\S)", r": \1", value)
        
        if key == 'rpoint_coords':
            value = re.sub(r"(\d+)([a-zA-Z]+)(?!°)", r"\1 \2", value)
            value = re.sub(r"([A-Z]):(\d)", r"\1: \2", value)
        
        if key == 'veh_mfr':
            value = re.sub(r' *\n *', '\n', value)
            value = re.sub(r'[ \t]+', ' ', value)
        else:
            value = re.sub(r"\s{2,}", " ", value)
        
        value = re.sub(r"m\s*\^?2", "m²", value, flags=re.IGNORECASE)
        result[key] = value
    
    return result
