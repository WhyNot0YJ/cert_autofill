import os
import json
import requests
from typing import Dict, Any, Optional
import logging
import zipfile
import platform
import xml.etree.ElementTree as ET

# =============== 新架构：预处理 + 策略（DIFY / 规则引擎） ===============
from enum import Enum


class ExtractionMode(str, Enum):
    """提取模式：DIFY 或 规则引擎（正则）。"""
    DIFY = "dify"
    RULES = "rules"


class BasePreprocessor:
    """输入文档预处理接口：统一做解压、格式归一化、去水印、OCR等。

    目前为占位实现（不做任何处理，直接返回原路径）。
    后续可以在这里扩展：
    - PDF/图片 清理与压缩
    - DOC/DOCX 正文抽取与修复
    - 多页合并/拆分
    - 字体缺失修复
    """

    def preprocess(self, file_path: str) -> str:
        return file_path


class BaseExtractionStrategy:
    """提取策略基类。"""

    def extract(self, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError


class RuleEngineExtractionStrategy(BaseExtractionStrategy):
    """规则引擎（正则）提取策略 - 架构占位。

    后续这里将实现：
    - 针对常见模板的关键字段正则匹配
    - 多语言/多模板的规则集合与优先级
    - 命中置信度与冲突合并策略
    目前保持占位，不改变现有功能。
    """

    def extract(self, file_path: str) -> Dict[str, Any]:
        raise NotImplementedError("Rule-engine extraction is not implemented yet.")

logger = logging.getLogger(__name__)


class DefaultPreprocessor(BasePreprocessor):
    """默认预处理器：
    - 若为 .docx 文件：读取正文文本，过滤隐藏内容（w:vanish），输出到日志，并生成旁路 .txt 供排查；不修改原文件。
    - 其它类型：直接返回。
    """

    def preprocess(self, file_path: str) -> str:
        try:
            _, ext = os.path.splitext(file_path.lower())
            # 若为 .doc，尝试自动转换为 .docx 再处理
            if ext == '.doc' and os.path.isfile(file_path):
                print(f"[Preprocess] Detected .doc, try convert to .docx: {file_path}", flush=True)
                # 仅使用 Windows Word COM 转换
                converted = self._convert_doc_to_docx_win(file_path)
                if converted and os.path.isfile(converted):
                    print(f"[Preprocess] Converted to DOCX: {converted}", flush=True)
                    file_path = converted
                    ext = '.docx'
                else:
                    print("[Preprocess] Convert failed, skip hidden filtering for .doc", flush=True)

            if ext == '.docx' and os.path.isfile(file_path):
                print(f"[Preprocess] Enter DOCX preprocessing: {file_path}", flush=True)
                # 1) 抽取可见文本（过滤 w:vanish），仅用于日志
                text = self._extract_docx_text_without_hidden(file_path)
                print(f"[Preprocess] Extracted DOCX text (hidden filtered), length={len(text)}", flush=True)
                print("[Preprocess] Text Content BEGIN\n" + text + "\n[Preprocess] Text Content END", flush=True)
                # 2) 生成去除隐藏内容后的临时 docx，供下游提取使用
                cleaned_path = self._create_clean_docx_without_hidden(file_path)
                if cleaned_path:
                    print(f"[Preprocess] Cleaned DOCX generated: {cleaned_path}", flush=True)
                    return cleaned_path
                else:
                    print("[Preprocess] Cleaned DOCX generation failed; fallback to original", flush=True)
            else:
                print(f"[Preprocess] Skip preprocessing (ext={ext})", flush=True)
        except Exception as e:
            print(f"[Preprocess] Skip due to error: {e}", flush=True)
        return file_path

    def _extract_docx_text_without_hidden(self, file_path: str) -> str:
        # 直接解析 docx (zip) 的 word/document.xml，过滤带 w:vanish 的 run
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                with zf.open('word/document.xml') as f:
                    tree = ET.parse(f)
            root = tree.getroot()
            texts: list[str] = []
            # 遍历段落
            for p in root.findall('.//w:p', ns):
                parts: list[str] = []
                for r in p.findall('w:r', ns):
                    # 检查隐藏属性 w:rPr/w:vanish
                    rpr = r.find('w:rPr', ns)
                    if rpr is not None and rpr.find('w:vanish', ns) is not None:
                        continue  # 跳过隐藏文字
                    # 收集 run 中的所有 w:t 文本
                    for t in r.findall('w:t', ns):
                        parts.append(t.text or '')
                if parts:
                    texts.append(''.join(parts))
            return '\n'.join(texts)
        except KeyError:
            # 没有正文部件时回退
            return ''
        except Exception as e:
            print(f"[Preprocess] DOCX parse failed: {e}", flush=True)
            return ''

    def _create_clean_docx_without_hidden(self, file_path: str) -> str:
        """返回一个新的 .docx 路径：其中隐藏 run (w:vanish) 已被移除。"""
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        try:
            with zipfile.ZipFile(file_path, 'r') as zin:
                # 读取并修改 document.xml
                with zin.open('word/document.xml') as f:
                    tree = ET.parse(f)
                root = tree.getroot()

                # 删除带 vanish 的 run
                for p in root.findall('.//w:p', ns):
                    runs = list(p.findall('w:r', ns))
                    for r in runs:
                        rpr = r.find('w:rPr', ns)
                        if rpr is not None and rpr.find('w:vanish', ns) is not None:
                            p.remove(r)

                # 写入临时文件
                dir_name = os.path.dirname(file_path)
                base = os.path.splitext(os.path.basename(file_path))[0]
                cleaned_path = os.path.join(dir_name, f"{base}.clean.docx")
                with zipfile.ZipFile(cleaned_path, 'w') as zout:
                    for item in zin.infolist():
                        if item.filename == 'word/document.xml':
                            xml_bytes = ET.tostring(root, encoding='utf-8')
                            zi = zipfile.ZipInfo(item.filename)
                            zi.compress_type = zipfile.ZIP_DEFLATED
                            zout.writestr(zi, xml_bytes)
                        else:
                            zout.writestr(item, zin.read(item.filename))
                return cleaned_path
        except KeyError:
            return ''

    # 移除 LibreOffice 转换逻辑，改为仅使用 Windows Word COM

    def _convert_doc_to_docx_win(self, file_path: str) -> str:
        """使用 Windows 下的 Word COM 将 .doc 转为 .docx。返回新文件路径或空字符串。"""
        try:
            if platform.system().lower() != 'windows':
                return ''
            # 延迟导入，避免非 Windows 环境报错
            try:
                import win32com.client  # type: ignore
                import pythoncom  # type: ignore
            except Exception as ie:
                print(f"[Preprocess] win32com not available (Linux/Docker environment): {ie}", flush=True)
                return ''

            pythoncom.CoInitialize()
            word = None
            try:
                word = win32com.client.Dispatch('Word.Application')
                word.Visible = False
                doc = word.Documents.Open(file_path)
                dir_name = os.path.dirname(file_path)
                base = os.path.splitext(os.path.basename(file_path))[0]
                target = os.path.join(dir_name, f"{base}.converted.docx")
                # 16 = wdFormatXMLDocument
                wdFormatXMLDocument = 16
                doc.SaveAs2(target, FileFormat=wdFormatXMLDocument)
                doc.Close(False)
                print(f"[Preprocess] Word COM saved: {target}", flush=True)
                return target if os.path.exists(target) else ''
            except Exception as ce:
                print(f"[Preprocess] Word COM convert failed: {ce}", flush=True)
                return ''
            finally:
                try:
                    if word is not None:
                        word.Quit()
                except Exception:
                    pass
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        except Exception as e:
            print(f"[Preprocess] .doc to .docx convert (COM) error: {e}", flush=True)
            return ''
        except Exception as e:
            print(f"[Preprocess] Create cleaned DOCX failed: {e}", flush=True)
            return ''

class DocumentExtractionService:
    """文档信息提取服务

    - 新增：预处理器 + 策略模式（DIFY / 规则）
    - 默认行为保持与原来一致：仍使用 DIFY 进行提取
    """

    def __init__(self, mode: ExtractionMode = ExtractionMode.DIFY, preprocessor: Optional[BasePreprocessor] = None):
        # 预处理器
        self.preprocessor = preprocessor or DefaultPreprocessor()

        # 策略选择（默认 DIFY 保持原功能）
        self.mode = mode
        self.strategy: BaseExtractionStrategy
        if self.mode == ExtractionMode.RULES:
            # 规则引擎策略（当前未实现，后续填充）
            self.strategy = RuleEngineExtractionStrategy()
        else:
            # DIFY 策略使用现有实现
            self.strategy = _DifyExtractionStrategy()

    def extract_from_document(self, file_path: str) -> Dict[str, Any]:
        """从单个文档中提取结构化信息（包含预处理与策略调用）。"""
        try:
            # 1) 统一预处理
            processed_path = self.preprocessor.preprocess(file_path)

            # 2) 调用策略提取
            response = self.strategy.extract(processed_path)

            # 3) 解析响应（保持与旧版相同的下游接口）
            extracted_data = self._parse_dify_response(response)

            return {
                "success": True,
                "data": extracted_data,
                "raw_response": response
            }

        except Exception as e:
            logger.error(f"提取失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    # 兼容旧接口的解析函数（沿用原逻辑）
    def _parse_dify_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return response['result']
        except Exception as e:
            logger.error(f"解析Dify响应失败: {str(e)}")
            return self._get_default_structure()

    def _get_default_structure(self) -> Dict[str, Any]:
        return {
            "approval_no": "",
            "info_folder_no": "",
            "safety_class": "",
            "pane_desc": "",
            "trade_names": "",
            "company_name": "",
            "company_address": "",
            "glass_layers": "",
            "interlayer_layers": "",
            "windscreen_thick": "",
            "interlayer_thick": "",
            "glass_treatment": "",
            "interlayer_type": "",
            "coating_type": "",
            "coating_thick": "",
            "material_nature": "",
            "glass_color_choice": "",
            "coating_color": "",
            "interlayer_total": False,
            "interlayer_partial": False,
            "interlayer_colourless": False,
            "conductors_choice": [],
            "opaque_obscure_choice": [],
            "remarks": "",
            "vehicles": []
        }

    # =============== DIFY 策略实现（封装原有逻辑，保持行为不变） ===============


class _DifyExtractionStrategy(BaseExtractionStrategy):
    def __init__(self):
        self.api_key = os.environ.get('DIFY_API_KEY', 'app-aOHstplRYJhO3uadmVwKnf8E')
        self.api_base = os.environ.get('DIFY_API_BASE', 'https://api.dify.ai/v1')

    def extract(self, file_path: str) -> Dict[str, Any]:
        if not self.api_key:
            raise Exception("Dify API密钥未配置")
        # 1) 上传文件以获取 file_id
        file_id = self._upload_file_to_dify(file_path)
        if not file_id:
            raise Exception("文件上传到Dify失败，未获取到file_id")

        # 2) 调用工作流运行接口（JSON请求）
        url = f"{self.api_base}/workflows/run"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "inputs": {
                "file": {
                    "type": "document",
                    "transfer_method": "local_file",
                    "upload_file_id": file_id
                }
            },
            "response_mode": "blocking",
            "user": "web-user"
        }

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        if resp.status_code != 200:
            logger.error(f"Dify 工作流调用失败({resp.status_code})，payload={payload}，响应={resp.text}")
            raise Exception(f"Dify 工作流调用失败: {resp.status_code} - {resp.text}")
        data = resp.json()

        # 规范化返回，确保下游解析时含有 'result'
        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], dict):
                outputs = data['data'].get('outputs')
                if isinstance(outputs, dict) and 'result' in outputs:
                    return { 'result': outputs['result'] }
                if isinstance(outputs, dict):
                    return { 'result': outputs }
            if 'result' in data:
                return { 'result': data['result'] }

        # 未命中已知结构
        raise Exception("Dify 工作流返回结构不包含期望的 result 字段")

    def _upload_file_to_dify(self, file_path: str) -> str:
        url = f"{self.api_base}/files/upload"
        headers = { 'Authorization': f'Bearer {self.api_key}' }
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        mime = 'application/octet-stream'
        if ext == '.pdf':
            mime = 'application/pdf'
        elif ext == '.docx':
            mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext == '.doc':
            mime = 'application/msword'

        with open(file_path, 'rb') as f:
            files = { 'file': (filename, f, mime) }
            data = { 'type': 'document', 'user': 'web-user' }
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        if resp.status_code not in (200, 201):
            raise Exception(f"Dify 文件上传失败: {resp.status_code} - {resp.text}")
        body = resp.json()
        if isinstance(body, dict):
            if 'data' in body and isinstance(body['data'], dict) and 'id' in body['data']:
                return body['data']['id']
            if 'id' in body:
                return body['id']
        raise Exception("Dify 文件上传响应中未找到 file_id")
    
    # 解析与默认结构由外层服务提供
        

# 创建全局实例
document_extraction_service = DocumentExtractionService()

