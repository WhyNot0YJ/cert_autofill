"""
规则引擎提取策略基类

基于正则表达式的文档信息提取实现，提供通用的文本提取和字段匹配功能
"""

import os
import uuid
from datetime import datetime
from flask import current_app
from ..file_upload_service import FileUploadService
import re
import zipfile
import platform
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from abc import abstractmethod
import logging

from .document_extract import BaseExtractionStrategy

logger = logging.getLogger(__name__)


class RuleEngineExtractionStrategy(BaseExtractionStrategy):
    """规则引擎（正则）提取策略基类 - 基于正则表达式的文档信息提取。

    实现功能：
    - 通用的文档文本提取（支持DOCX、PDF、DOC等格式）
    - 通用的字段值正则匹配逻辑
    - 可扩展的规则引擎框架
    
    子类需要实现：
    - _build_field_patterns(): 定义特定模板的字段提取规则
    - _apply_extraction_rules(): 应用提取规则的具体逻辑
    - _post_process_data(): 后处理提取的数据
    """

    def __init__(self):
        self.field_patterns = self._build_field_patterns()

    def extract(self, file_path: str) -> Dict[str, Any]:
        """从文档中提取结构化信息"""
        try:
            # 1. 提取文档文本
            text = self._extract_text_from_file(file_path)
            if not text:
                raise Exception("无法从文档中提取文本内容")

            # 2. 应用正则规则提取字段
            extracted_data = self._apply_extraction_rules(text)
            
            # 2.1 提取第一页图片（仅DOCX，且不包含页眉/页脚）用于商标识别等
            first_page_images = []
            try:
                if os.path.splitext(file_path.lower())[1] == '.docx':
                    first_page_images = self._extract_first_page_images_from_docx(file_path)
                    # 保存图片到 uploads/company/marks 并返回路径
                    saved_paths = self._save_first_page_images(first_page_images)
                    # 暂存到提取结果，供模板后处理使用
                    extracted_data['_first_page_images'] = saved_paths
            except Exception as _:
                # 图片提取失败不阻断主流程
                extracted_data['_first_page_images'] = []

            # 3. 后处理和验证
            processed_data = self._post_process_data(extracted_data)
            
            return {'result': processed_data}
            
        except Exception as e:
            logger.error(f"规则引擎提取失败: {str(e)}")
            raise Exception(f"规则引擎提取失败: {str(e)}")

    @abstractmethod
    def _build_field_patterns(self) -> Dict[str, Dict[str, Any]]:
        """构建字段提取的正则表达式模式（由子类实现）"""
        pass

    @abstractmethod
    def _apply_extraction_rules(self, text: str) -> Dict[str, Any]:
        """应用正则表达式规则提取字段（由子类实现）"""
        pass

    @abstractmethod
    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """后处理提取的数据（由子类实现）"""
        pass

    # ==================== 通用工具方法 ====================

    def _extract_text_from_file(self, file_path: str) -> str:
        """从文件中提取文本内容"""
        try:
            _, ext = os.path.splitext(file_path.lower())
            
            if ext == '.docx':
                return self._extract_docx_text(file_path)
            elif ext == '.doc':
                # 尝试转换为docx后提取
                converted_path = self._convert_doc_to_docx(file_path)
                if converted_path:
                    return self._extract_docx_text(converted_path)
            elif ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif ext in ['.txt', '.text']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise Exception(f"不支持的文件格式: {ext}")
                
        except Exception as e:
            logger.error(f"文本提取失败: {str(e)}")
            raise Exception(f"文本提取失败: {str(e)}")

    def _extract_docx_text(self, file_path: str) -> str:
        """从DOCX文件中提取文本"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                with zf.open('word/document.xml') as f:
                    tree = ET.parse(f)
            root = tree.getroot()
            
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            texts = []
            
            for p in root.findall('.//w:p', ns):
                parts = []
                for r in p.findall('w:r', ns):
                    for t in r.findall('w:t', ns):
                        if t.text:
                            parts.append(t.text)
                if parts:
                    texts.append(''.join(parts))
            
            return '\n'.join(texts)
            
        except Exception as e:
            logger.error(f"DOCX文本提取失败: {str(e)}")
            raise Exception(f"DOCX文本提取失败: {str(e)}")

    def _extract_pdf_text(self, file_path: str) -> str:
        """从PDF文件中提取文本（需要安装PyPDF2或pdfplumber）"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.warning("PyPDF2未安装，无法提取PDF文本")
            return ""
        except Exception as e:
            logger.error(f"PDF文本提取失败: {str(e)}")
            return ""

    def _convert_doc_to_docx(self, file_path: str) -> str:
        """将DOC文件转换为DOCX（复用现有逻辑）"""
        try:
            if platform.system().lower() != 'windows':
                return ""
            
            import win32com.client
            import pythoncom
            
            pythoncom.CoInitialize()
            word = None
            try:
                word = win32com.client.Dispatch('Word.Application')
                word.Visible = False
                doc = word.Documents.Open(file_path)
                dir_name = os.path.dirname(file_path)
                base = os.path.splitext(os.path.basename(file_path))[0]
                target = os.path.join(dir_name, f"{base}.temp.docx")
                doc.SaveAs2(target, FileFormat=16)  # wdFormatXMLDocument
                doc.Close(False)
                return target if os.path.exists(target) else ""
            finally:
                if word:
                    word.Quit()
                pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"DOC转DOCX失败: {str(e)}")
            return ""

    def _extract_field_value(self, text: str, field_config: Dict[str, Any]) -> str:
        """使用正则表达式提取单个字段值（通用方法）"""
        patterns = field_config.get('patterns', [])
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # 返回第一个匹配的非空值
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0] if match[0] else match[1] if len(match) > 1 else ""
                        if match and match.strip():
                            return match.strip()
            except re.error as e:
                logger.warning(f"正则表达式错误 {pattern}: {str(e)}")
                continue
        
        return ""

    # ==================== 图片提取（第一页） ====================
    def _extract_first_page_images_from_docx(self, file_path: str):
        """从DOCX正文中（不含页眉/页脚）提取第一页内出现的图片。

        基于document.xml中元素顺序，遇到第一页结束标记（w:lastRenderedPageBreak 或 w:br type=page
        或段前分页 w:pageBreakBefore 或节分隔 w:sectPr）即停止收集。
        返回: [{'filename': str, 'bytes': bytes}]
        """
        import zipfile
        from xml.etree import ElementTree as ET

        with zipfile.ZipFile(file_path, 'r') as zf:
            # 解析关系，定位rId -> media路径
            rels_path = 'word/_rels/document.xml.rels'
            rels_map = {}
            if rels_path in zf.namelist():
                with zf.open(rels_path) as rf:
                    rtree = ET.parse(rf)
                rroot = rtree.getroot()
                # 命名空间 http://schemas.openxmlformats.org/package/2006/relationships
                for rel in rroot.findall('.//Relationship', namespaces={'': 'http://schemas.openxmlformats.org/package/2006/relationships'}):
                    r_id = rel.get('Id')
                    target = rel.get('Target')
                    if r_id and target:
                        rels_map[r_id] = target

            # 读取正文并遍历直到第一页结束
            with zf.open('word/document.xml') as f:
                tree = ET.parse(f)
            root = tree.getroot()

            ns = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }

            collected_rids = []
            first_page_done = False

            # 遍历段落，检测分页标记并收集图片
            for p in root.findall('.//w:p', ns):
                # 若遇到段前分页或节分隔，视为翻页
                ppr = p.find('w:pPr', ns)
                if ppr is not None:
                    if ppr.find('w:pageBreakBefore', ns) is not None:
                        first_page_done = True
                    if ppr.find('w:sectPr', ns) is not None:
                        first_page_done = True
                # Word保存时可能插入的渲染分页标记
                if p.find('.//w:lastRenderedPageBreak', ns) is not None:
                    first_page_done = True
                # 显式分页符
                for br in p.findall('.//w:br', ns):
                    if br.get('{%s}type' % ns['w']) == 'page':
                        first_page_done = True

                if first_page_done:
                    break

                # 收集该段落内图片（drawing -> blip@r:embed）
                for blip in p.findall('.//w:drawing//a:blip', ns):
                    r_id = blip.get('{%s}embed' % ns['r'])
                    if r_id:
                        collected_rids.append(r_id)

            # 去重并转成文件路径
            unique_rids = []
            for r_id in collected_rids:
                if r_id not in unique_rids:
                    unique_rids.append(r_id)

            images = []
            for r_id in unique_rids:
                target = rels_map.get(r_id)
                if not target:
                    continue
                # 关系Target通常为 'media/imageX.ext' 或相对路径
                media_path = 'word/' + target if not target.startswith('word/') else target
                if media_path in zf.namelist():
                    with zf.open(media_path) as imgf:
                        images.append({'filename': media_path.split('/')[-1], 'bytes': imgf.read()})
            return images

    def _save_first_page_images(self, images):
        """保存第一页图片到 uploads/company/marks 并返回相对路径列表。

        images: [{'filename': str, 'bytes': bytes}]
        返回: ["/uploads/company/marks/<generated>.ext", ...]
        """
        # 基础上传目录：优先使用 Flask 配置 UPLOAD_FOLDER，回退到 backend/uploads
        try:
            base_dir = current_app.config.get('UPLOAD_FOLDER')  # type: ignore[attr-defined]
        except Exception:
            base_dir = None
        if not base_dir:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            base_dir = os.path.join(backend_dir, 'uploads')

        # 使用已有工具创建 company/marks 目录
        marks_dir = FileUploadService.create_upload_directory(base_dir, 'company', 'marks')

        saved_paths = []

        for index, item in enumerate(images, start=1):
            original = item.get('filename', 'image')
            # 使用通用工具生成安全文件名（带时间戳与UUID）
            filename = FileUploadService.generate_safe_filename(
                original_filename=original,
                prefix='company_marks',
                include_timestamp=True,
                include_uuid=True
            )
            abs_path = os.path.join(marks_dir, filename)
            try:
                with open(abs_path, 'wb') as f:
                    f.write(item.get('bytes', b''))
                # 提供给前端/调用方的相对路径（以后端为根的静态访问路径约定）
                rel_path = os.path.join('/uploads', 'company', 'marks', filename).replace('\\', '/')
                saved_paths.append(rel_path)
            except Exception:
                continue

        return saved_paths

