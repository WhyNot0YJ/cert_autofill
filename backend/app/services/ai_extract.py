import os
import json
import requests
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AIExtractionService:
    """文档信息提取服务 - 集成Dify API"""
    
    def __init__(self):
        # Dify API配置
        self.api_key = os.environ.get('DIFY_API_KEY', 'app-aOHstplRYJhO3uadmVwKnf8E')
        self.api_base = os.environ.get('DIFY_API_BASE', 'https://api.dify.ai/v1')
        
    def extract_from_document(self, file_path: str) -> Dict[str, Any]:
        """
        从单个文档中提取结构化信息
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            Dict[str, Any]: 提取的结构化数据
        """
        try:
            # 调用Dify API进行文档提取
            response = self._call_dify_api(file_path)
            
            # 解析响应
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
    
    def _call_dify_api(self, file_path: str) -> Dict[str, Any]:
        """调用Dify API进行文档提取"""
        if not self.api_key:
            raise Exception("Dify API密钥未配置")
        
        try:
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
            # 固定按工作流要求使用 file 参数（单文件变量）
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
        except Exception as e:
            logger.error(f"Dify API调用失败: {str(e)}")
            # 失败时直接抛出异常，由上层捕获并返回错误
            raise

    def _upload_file_to_dify(self, file_path: str) -> str:
        """上传文件到Dify，返回 file_id"""
        url = f"{self.api_base}/files/upload"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        # 基于扩展名推断 MIME
        mime = 'application/octet-stream'
        if ext == '.pdf':
            mime = 'application/pdf'
        elif ext == '.docx':
            mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext == '.doc':
            mime = 'application/msword'
        
        with open(file_path, 'rb') as f:
            files = { 'file': (filename, f, mime) }
            # Dify 需要指定文件类型（image/document），文档应为 document；同时指定 user 与工作流调用一致
            data = { 'type': 'document', 'user': 'web-user' }
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        if resp.status_code not in (200, 201):
            raise Exception(f"Dify 文件上传失败: {resp.status_code} - {resp.text}")
        body = resp.json()
        # 常见结构: { data: { id: 'file_...' } } 或 { id: 'file_...' }
        if isinstance(body, dict):
            if 'data' in body and isinstance(body['data'], dict) and 'id' in body['data']:
                return body['data']['id']
            if 'id' in body:
                return body['id']
        raise Exception("Dify 文件上传响应中未找到 file_id")
    
    def _parse_dify_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析Dify API响应"""
        try:
            return response['result']
        except Exception as e:
            logger.error(f"解析Dify响应失败: {str(e)}")
            return self._get_default_structure()
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """获取默认数据结构"""
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

# 创建全局实例
ai_extraction_service = AIExtractionService() 