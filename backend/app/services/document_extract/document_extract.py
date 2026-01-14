import os
import zipfile
import platform
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import logging


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


# 导入策略实现
from .templates.ordinary_laminated_glass_windscreen_template import OrdinaryLaminatedGlassWindscreenTemplate

logger = logging.getLogger(__name__)


class DefaultPreprocessor(BasePreprocessor):
    """默认预处理器：
    - 若为 .docx 文件：读取正文文本，过滤隐藏内容（w:vanish）与删除线内容（w:strike/w:dstrike），输出到日志，并生成旁路 .txt 供排查；不修改原文件。
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
                # 1) 抽取可见文本（过滤 w:vanish 与 w:strike/w:dstrike），仅用于日志
                text = self._extract_docx_text_without_hidden(file_path)
                print(f"[Preprocess] Extracted DOCX text (hidden/strikethrough filtered), length={len(text)}", flush=True)
                print("[Preprocess] Text Content BEGIN\n" + text + "\n[Preprocess] Text Content END", flush=True)
                # 2) 生成去除隐藏与删除线内容后的临时 docx，供下游提取使用
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
        # 直接解析 docx (zip) 的 word/document.xml，过滤带 w:vanish 与 w:strike/w:dstrike 的 run
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
                    # 检查隐藏属性 w:rPr/w:vanish 与删除线 w:strike/w:dstrike
                    rpr = r.find('w:rPr', ns)
                    def _is_true(el: Optional[ET.Element]) -> bool:
                        if el is None:
                            return False
                        val = el.get(f"{{{ns['w']}}}val")
                        return val is None or str(val).lower() not in ('false', '0')

                    if rpr is not None:
                        if (rpr.find('w:vanish', ns) is not None) or _is_true(rpr.find('w:strike', ns)) or _is_true(rpr.find('w:dstrike', ns)):
                            continue  # 跳过隐藏或带删除线文字
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
        """返回一个新的 .docx 路径：其中隐藏 (w:vanish) 与删除线 (w:strike/w:dstrike) 的 run 已被移除。"""
        ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        try:
            with zipfile.ZipFile(file_path, 'r') as zin:
                # 读取并修改 document.xml
                with zin.open('word/document.xml') as f:
                    tree = ET.parse(f)
                root = tree.getroot()

                # 删除带 vanish 或 strike 的 run
                for p in root.findall('.//w:p', ns):
                    runs = list(p.findall('w:r', ns))
                    for r in runs:
                        rpr = r.find('w:rPr', ns)
                        if rpr is not None:
                            def _is_true(el: Optional[ET.Element]) -> bool:
                                if el is None:
                                    return False
                                val = el.get(f"{{{ns['w']}}}val")
                                return val is None or str(val).lower() not in ('false', '0')
                            if (rpr.find('w:vanish', ns) is not None) or _is_true(rpr.find('w:strike', ns)) or _is_true(rpr.find('w:dstrike', ns)):
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
    """文档信息提取服务（仅规则引擎）"""

    def __init__(self, preprocessor: Optional[BasePreprocessor] = None):
        # 预处理器
        self.preprocessor = preprocessor or DefaultPreprocessor()
        # 固定策略：普通层压玻璃挡风玻璃模板
        self._strategy = OrdinaryLaminatedGlassWindscreenTemplate()

    # 兼容旧接口保留，但内部仅返回规则引擎
    def _get_strategy(self) -> BaseExtractionStrategy:
        return self._strategy

    def extract_from_document(self, file_path: str) -> Dict[str, Any]:
        """从单个文档中提取结构化信息（包含预处理与策略调用）。
        
        Args:
            file_path: 文档文件路径
            mode: 提取模式，如果为None则使用默认模式
            
        Returns:
            包含提取结果的字典
        """
        try:
            # 1) 统一预处理
            processed_path = self.preprocessor.preprocess(file_path)

            # 2) 获取策略并调用提取（仅规则引擎）
            strategy = self._get_strategy()
            response = strategy.extract(processed_path)

            # 3) 解析响应
            extracted_data = self._parse_response(response)

            return {
                "success": True,
                "data": extracted_data,
                "raw_response": response,
                "mode": "rules"
            }

        except Exception as e:
            logger.error(f"提取失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    # 解析函数
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return response['result']
        except Exception as e:
            logger.error(f"解析响应失败: {str(e)}")
            return self._get_default_structure()

    def _get_default_structure(self) -> Dict[str, Any]:
        return {
            "approval_no": "",
            "information_folder_no": "",
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
            "glass_color_choice": "colourless",
            "coating_color": "",
            "interlayer_total": False,
            "interlayer_partial": False,
            "interlayer_colourless": False,
            "conductors_choice": "no",
            "opaque_obscure_choice": "no",
            "remarks": "",
            "vehicles": []
        }

    def extract_with_rules(self, file_path: str) -> Dict[str, Any]:
        """使用规则引擎模式提取文档"""
        return self.extract_from_document(file_path)

    # =============== 策略实现已移至独立文件 ===============
        

# 创建全局服务实例（单例）
document_extraction_service = DocumentExtractionService()

# 为了向后兼容，创建别名（指向同一个实例）
rule_engine_service = document_extraction_service

