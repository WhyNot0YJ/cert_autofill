#!/usr/bin/env python3
"""
基础文档生成器
提供通用的文档生成功能，包括Word和PDF格式支持
"""
import os
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage
import subprocess
import platform
import threading
import time
from typing import Dict, Any, List, Union
from docx.shared import Cm
from flask import current_app


class BaseGenerator:
    """基础文档生成器"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.template_filename = template_name  # 添加这个属性，保持兼容性
        self.display_name = "基础文档"
        self.description = "基础文档生成器"
        # 设置模板目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.template_dir = os.path.join(backend_dir, 'templates')
        # 默认图片尺寸设置
        self.default_image_height = Cm(1.0)
        self.default_image_width = Cm(2.0)
    
    def generate_docx(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """生成DOCX文档"""
        raise NotImplementedError("子类必须实现此方法")
    
    def generate_pdf(self, fields: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """生成PDF文档"""
        raise NotImplementedError("子类必须实现此方法")
    
    def generate_document(self, fields: Dict[str, Any], output_path: str, format_type: str = 'docx') -> Dict[str, Any]:
        """
        统一的文档生成接口
        
        Args:
            fields: 字段数据
            output_path: 输出文件路径
            format_type: 输出格式 ('docx' 或 'pdf')
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        if format_type.lower() == 'pdf':
            return self.generate_pdf(fields, output_path)
        else:
            return self.generate_docx(fields, output_path)
    
    def prepare_context(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备文档上下文数据
        
        Args:
            fields: 原始字段数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        context = fields.copy()
        
        # 格式化日期字段
        context = self._format_dates(context)

        # 标准化通用商标字段
        if 'trade_names' in context or 'trade_marks' in context:
            context['trade_names'] = self.normalize_trade_names(context.get('trade_names', ''))
            context['trade_marks'] = self.normalize_trade_marks(context.get('trade_marks', []))
        
        return context
    
    def _format_dates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化日期字段为文档所需格式 (July 14, 2025)
        
        Args:
            context: 原始上下文数据
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        date_fields = ['approval_date', 'test_date', 'report_date']
        
        for field in date_fields:
            if field in context and context[field]:
                date_value = context[field]
                if isinstance(date_value, str):
                    # 如果是字符串，尝试解析
                    try:
                        date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
                    except ValueError:
                        continue
                elif isinstance(date_value, datetime):
                    date_value = date_value.date()
                
                if isinstance(date_value, date):
                    # 格式化为 "July 14, 2025" 格式
                    formatted_date = date_value.strftime('%B %d, %Y')
                    context[field] = formatted_date
        
        return context
    
    def _convert_url_to_local_path(self, url: str) -> str:
        """
        将URL或路径转换为本地文件路径
        
        Args:
            url: 图片URL或路径
            
        Returns:
            str: 本地文件路径，如果不存在则返回None
        """
        try:
            # 统一从 /uploads/ 截取相对路径，忽略域名和端口差异
            if url.startswith('http'):
                uploads_idx = url.find('/uploads/')
                if uploads_idx != -1:
                    relative_path = url[uploads_idx+1:]
                else:
                    relative_path = None
                # 构建本地路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, relative_path) if relative_path else None
            elif url.startswith('/uploads/'):
                # 处理相对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, url.lstrip('/'))
            elif url.startswith('uploads/'):
                # 已经是相对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, url)
            else:
                # 假设是绝对路径
                local_path = url
            
            # 检查文件是否存在
            if os.path.exists(local_path):
                return local_path
            else:
                # 尝试其他可能的路径格式
                alt_paths = [
                    local_path.replace('\\', '/'),
                    local_path.replace('/', '\\')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                return None
                
        except Exception as e:
            return None
    
    def _get_company_picture(self, fields: Dict[str, Any], placeholder: str = '[公司图片]') -> str:
        """
        获取公司图片路径
        
        Args:
            fields: 字段数据
            placeholder: 占位符文本，默认为'[公司图片]'
            
        Returns:
            str: 公司图片路径或占位符
        """
        try:
            company_id = fields.get('company_id')
            if not company_id:
                return placeholder
            
            # 动态导入避免循环依赖
            from ...models.company import Company
            
            company = Company.query.get(company_id)
            if not company or not company.picture:
                return placeholder
            
            # 转换为本地路径
            local_path = self._convert_url_to_local_path(company.picture)
            return local_path if local_path else placeholder
            
        except Exception as e:
            return placeholder
    
    def _get_company_signature(self, fields: Dict[str, Any], placeholder: str = '[签名图片]') -> str:
        """
        获取公司签名图片路径
        
        Args:
            fields: 字段数据
            placeholder: 占位符文本，默认为'[签名图片]'
            
        Returns:
            str: 签名图片路径或占位符
        """
        try:
            company_id = fields.get('company_id')
            if not company_id:
                return placeholder
            
            # 动态导入避免循环依赖
            from ...models.company import Company
            
            company = Company.query.get(company_id)
            if not company or not company.signature:
                return placeholder
            
            # 转换为本地路径
            local_path = self._convert_url_to_local_path(company.signature)
            return local_path if local_path else placeholder
            
        except Exception as e:
            return placeholder
    
    def _process_image_urls_to_paths(self, image_urls: Union[str, List[str]]) -> List[str]:
        """
        处理图片URL列表，转换为本地路径列表
        
        Args:
            image_urls: 图片URL字符串或URL列表
            
        Returns:
            List[str]: 本地路径列表
        """
        if isinstance(image_urls, str):
            image_urls = [image_urls]
        
        processed_paths = []
        for url in image_urls:
            local_path = self._convert_url_to_local_path(url)
            if local_path:
                processed_paths.append(local_path)
        
        return processed_paths
    
    def _process_inline_images(self, context: Dict[str, Any], doc: DocxTemplate) -> Dict[str, Any]:
        """
        处理内联图片，将图片路径转换为InlineImage对象
        子类应该重写此方法来处理特定的图片字段
        
        Args:
            context: 上下文数据
            doc: DocxTemplate 对象
            
        Returns:
            Dict[str, Any]: 处理后的上下文数据
        """
        processed = context.copy()

        # 通用处理：将 trade_marks （若存在）渲染为 InlineImage 数组
        try:
            if 'trade_marks' in processed and isinstance(processed['trade_marks'], list):
                processed['trade_marks'] = self._create_inline_image_array(
                    doc,
                    processed['trade_marks'],
                    'trade_marks',
                    height=self._get_image_height_for_field('trade_marks'),
                    width=self._get_image_width_for_field('trade_marks')
                )
        except Exception:
            pass

        return processed

    @staticmethod
    def normalize_trade_names(value: Any) -> str:
        """将 trade_names 统一为分号分隔的字符串。"""
        try:
            if isinstance(value, list):
                return '; '.join([str(x) for x in value if x])
            if isinstance(value, str):
                return value
            return ''
        except Exception:
            return ''

    @staticmethod
    def normalize_trade_marks(value: Any) -> List[str]:
        """将 trade_marks 统一为字符串数组。"""
        try:
            if isinstance(value, list):
                return [x for x in value if x]
            if isinstance(value, str):
                return [value] if value else []
            return []
        except Exception:
            return []
    
    def _create_single_inline_image(self, doc: DocxTemplate, image_path: str, field_name: str, height: Cm = None, width: Cm = None) -> Union[InlineImage, str]:
        """
        创建单个InlineImage对象
        
        Args:
            doc: DocxTemplate 对象
            image_path: 图片路径
            field_name: 字段名称（用于错误信息）
            height: 图片高度，如果为None则自动适配
            width: 图片宽度，如果为None则自动适配
            
        Returns:
            Union[InlineImage, str]: InlineImage对象或占位符文本
        """
        try:
            # 处理图片路径
            local_path = self._process_image_path(image_path)
            if not local_path or not os.path.exists(local_path):
                return f'[{field_name.replace("_", " ").title()}]'
            
            # 创建InlineImage对象 - 只传入非None的尺寸参数
            kwargs = {}
            if height is not None:
                kwargs['height'] = height
            if width is not None:
                kwargs['width'] = width
            
            inline_image = InlineImage(doc, local_path, **kwargs)
            return inline_image
            
        except Exception as e:
            return f'[{field_name.replace("_", " ").title()}]'
    
    def _create_inline_image_array(self, doc: DocxTemplate, image_paths: List[str], field_name: str, height: Cm = None, width: Cm = None) -> List[Union[InlineImage, str]]:
        """
        创建InlineImage对象数组
        
        Args:
            doc: DocxTemplate 对象
            image_paths: 图片路径列表
            field_name: 字段名称（用于错误信息）
            height: 图片高度，如果为None则自动适配
            width: 图片宽度，如果为None则自动适配
            
        Returns:
            List[Union[InlineImage, str]]: InlineImage对象或占位符文本的列表
        """
        try:
            images = []
            for i, image_path in enumerate(image_paths):
                # 处理图片路径
                local_path = self._process_image_path(image_path)
                if not local_path or not os.path.exists(local_path):
                    images.append(f'[{field_name.replace("_", " ").title()}]')
                    continue
                
                # 创建InlineImage对象 - 只传入非None的尺寸参数
                try:
                    kwargs = {}
                    if height is not None:
                        kwargs['height'] = height
                    if width is not None:
                        kwargs['width'] = width
                    
                    inline_image = InlineImage(doc, local_path, **kwargs)
                    images.append(inline_image)
                        
                except Exception as e:
                    images.append(f'[{field_name.replace("_", " ").title()}]')
            
            return images
            
        except Exception as e:
            return [f'[{field_name.replace("_", " ").title()}]']
    
    def _process_image_path(self, image_path: str) -> str:
        """
        处理图片路径，转换为本地文件路径
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: 本地文件路径，如果处理失败则返回None
        """
        try:
            if not image_path:
                return None
            
            # 处理HTTP URL
            server_url = current_app.config.get('SERVER_URL', 'http://localhost')
            if image_path.startswith(f'{server_url}/uploads/'):
                # 提取相对路径
                relative_path = image_path.replace(f'{server_url}/', '')
                # 构建本地路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, relative_path)
                
                # 检查文件是否存在
                if os.path.exists(local_path):
                    return local_path
                
                # 尝试其他可能的路径格式
                alt_paths = [
                    local_path.replace('\\', '/'),  # 尝试正斜杠
                    local_path.replace('/', '\\'),  # 尝试反斜杠
                    os.path.join(backend_dir, 'uploads', relative_path.split('/')[-2], relative_path.split('/')[-1])  # 简化路径
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                return None
            
            # 处理相对路径
            elif image_path.startswith('/uploads/'):
                # 转换为绝对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, image_path.lstrip('/'))
                
                if os.path.exists(local_path):
                    return local_path
                
                # 尝试其他格式
                alt_paths = [
                    local_path.replace('\\', '/'),
                    local_path.replace('/', '\\')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                return None
            
            elif image_path.startswith('uploads/'):
                # 已经是相对路径
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                local_path = os.path.join(backend_dir, image_path)
                
                if os.path.exists(local_path):
                    return local_path
                
                # 尝试其他格式
                alt_paths = [
                    local_path.replace('\\', '/'),
                    local_path.replace('/', '\\')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                return None
            
            else:
                # 假设是绝对路径
                if os.path.exists(image_path):
                    return image_path
                
                # 尝试其他格式
                alt_paths = [
                    image_path.replace('\\', '/'),
                    image_path.replace('/', '\\')
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        return alt_path
                
                return None
                
        except Exception as e:
            return None
    
    def _get_image_height_for_field(self, field_name: str) -> Cm:
        """
        根据字段名称获取图片高度
        
        Args:
            field_name: 字段名称
            
        Returns:
            Cm: 图片高度
        """
        # 子类可以重写此方法来自定义不同字段的图片尺寸
        return self.default_image_height
    
    def _get_image_width_for_field(self, field_name: str) -> Cm:
        """
        根据字段名称获取图片宽度
        
        Args:
            field_name: 字段名称
            
        Returns:
            Cm: 图片宽度，如果不需要固定宽度则返回None
        """
        # 子类可以重写此方法来自定义不同字段的图片尺寸
        return None
    
    def _convert_docx_to_pdf(self, docx_path: str, pdf_path: str, update_fields: bool = False) -> bool:
        """
        将DOCX文件转换为PDF
        
        Args:
            docx_path: DOCX文件路径
            pdf_path: PDF输出路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(docx_path):
                print(f"❌ DOCX文件不存在: {docx_path}")
                return False
            
            # 获取系统信息
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: 使用 Microsoft Word COM 自动化刷新域并导出 PDF
                try:
                    import win32com.client as win32
                    import pythoncom
                except Exception as e:
                    print(f"❌ 未安装 pywin32 或无法导入（Linux/Docker环境）：{e}")
                    return False

                # 序列化 Word 导出，避免并发导致 COM 断开/RPC 错误
                if not hasattr(self.__class__, "_word_export_lock"):
                    self.__class__._word_export_lock = threading.Lock()

                def _export_once() -> bool:
                    word = None
                    try:
                        pythoncom.CoInitialize()
                        # DispatchEx 更适合多线程场景
                        word = win32.DispatchEx('Word.Application')
                        word.Visible = False
                        doc = word.Documents.Open(os.path.abspath(docx_path))
                        # 可选：更新全部域（正文与页眉/页脚）
                        if update_fields:
                            try:
                                doc.Fields.Update()
                                for section in doc.Sections:
                                    for i in (1, 2, 3):
                                        try:
                                            section.Headers(i).Range.Fields.Update()
                                        except Exception:
                                            pass
                                        try:
                                            section.Footers(i).Range.Fields.Update()
                                        except Exception:
                                            pass
                            except Exception:
                                pass

                        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                        wdExportFormatPDF = 17
                        doc.ExportAsFixedFormat(os.path.abspath(pdf_path), wdExportFormatPDF)
                        doc.Close(False)
                        print(f"✅ Word 导出 PDF 成功: {pdf_path}")
                        return True
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

                with self.__class__._word_export_lock:
                    # 首次尝试
                    try:
                        return _export_once()
                    except Exception as e:
                        # 典型错误：-2147417848 对象已断开、-2147023174 RPC 不可用 → 重试一次
                        print(f"⚠️ Word 导出异常，准备重试：{e}")
                        time.sleep(0.5)
                        try:
                            return _export_once()
                        except Exception as e2:
                            print(f"❌ 使用 Word 导出 PDF 失败（重试后）：{e2}")
                            return False
            
            elif system in ("darwin", "linux"):
                # 仅支持 Microsoft Word（Windows）
                print("❌ 当前配置仅支持在 Windows 上使用 Microsoft Word 导出 PDF。请在 Windows 环境运行后端服务。")
                return False
                    
        except subprocess.TimeoutExpired:
            print("❌ PDF转换超时")
            return False
        except Exception as e:
            print(f"❌ PDF转换失败: {e}")
            return False
    
    def _find_libreoffice_windows(self) -> str:
        """
        在Windows系统上查找LibreOffice安装路径
        
        Returns:
            str: LibreOffice可执行文件路径，如果未找到则返回None
        """
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            r"C:\LibreOffice\program\soffice.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
