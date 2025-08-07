import os
import json
import requests
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AIExtractionService:
    """AI文档信息提取服务"""
    
    def __init__(self):
        # 配置AI模型API（这里使用OpenAI作为示例，可以根据需要修改）
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4')
        
    def extract_from_documents(self, application_text: str, report_text: str) -> Dict[str, Any]:
        """
        从申请书和检测报告中提取结构化信息
        
        Args:
            application_text: 申请书文本内容
            report_text: 检测报告文本内容
            
        Returns:
            Dict[str, Any]: 提取的结构化数据
        """
        try:
            # 构建提示词
            prompt = self._build_extraction_prompt(application_text, report_text)
            
            # 调用AI模型
            response = self._call_ai_model(prompt)
            
            # 解析响应
            extracted_data = self._parse_ai_response(response)
            
            return {
                "success": True,
                "data": extracted_data,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"AI提取失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    def _build_extraction_prompt(self, application_text: str, report_text: str) -> str:
        """构建AI提取提示词"""
        prompt = f"""
请从以下申请书和检测报告中提取关键信息，并按照指定的JSON格式返回：

申请书内容：
{application_text[:2000]}...

检测报告内容：
{report_text[:2000]}...

请提取以下信息并以JSON格式返回：

{{
    "enterprise_info": {{
        "name": "企业名称",
        "english_name": "企业英文名",
        "registration_number": "注册号",
        "legal_representative": "法定代表人",
        "contact_person": "联系人",
        "contact_phone": "联系电话",
        "contact_email": "联系邮箱",
        "address": "地址"
    }},
    "certification_info": {{
        "type": "认证类型",
        "product_name": "产品名称",
        "product_model": "产品型号",
        "scope": "认证范围"
    }},
    "technical_specs": {{
        "specifications": "技术规格参数"
    }},
    "test_info": {{
        "standards": "测试标准",
        "results": "测试结果"
    }},
    "certificate_info": {{
        "number": "证书编号",
        "issue_date": "发证日期",
        "expiry_date": "有效期至",
        "authority": "发证机构"
    }},
    "additional_info": {{
        "remarks": "备注信息"
    }}
}}

请确保：
1. 只返回JSON格式数据，不要包含其他文字
2. 如果某个字段无法从文档中提取，请填写null
3. 日期格式使用YYYY-MM-DD
4. 所有文本内容保持原始格式，不要修改
"""
        return prompt
    
    def _call_ai_model(self, prompt: str) -> str:
        """调用AI模型API"""
        if not self.api_key:
            # 如果没有配置API密钥，返回模拟数据
            return self._get_mock_response()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的文档信息提取助手，擅长从认证申请书和检测报告中提取结构化信息。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.1,
                'max_tokens': 2000
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"AI模型调用失败: {str(e)}")
            # 返回模拟数据作为备选
            return self._get_mock_response()
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("未找到有效的JSON数据")
                
        except Exception as e:
            logger.error(f"解析AI响应失败: {str(e)}")
            return self._get_default_structure()
    
    def _get_mock_response(self) -> str:
        """获取模拟响应数据（用于测试）"""
        mock_data = {
            "enterprise_info": {
                "name": "广州福耀玻璃有限公司",
                "english_name": "FUYAO GLASS INDUSTRY GROUP CO., LTD.",
                "registration_number": "91440101MA9CQ8KX3R",
                "legal_representative": "曹德旺",
                "contact_person": "张工程师",
                "contact_phone": "020-12345678",
                "contact_email": "contact@fuyao.com",
                "address": "广州市黄埔区科学城科学大道"
            },
            "certification_info": {
                "type": "夹层玻璃前风窗认证",
                "product_name": "4.76mm普通PVB夹层玻璃",
                "product_model": "AY7",
                "scope": "前风窗夹层玻璃认证"
            },
            "technical_specs": {
                "specifications": "厚度: 4.76mm, 夹层类型: PVB, 玻璃类型: 夹层玻璃"
            },
            "test_info": {
                "standards": "GB 9656-2021",
                "results": "通过所有测试项目"
            },
            "certificate_info": {
                "number": "TUV-2024-001",
                "issue_date": "2024-01-15",
                "expiry_date": "2027-01-14",
                "authority": "TÜV NORD"
            },
            "additional_info": {
                "remarks": "认证延期申请"
            }
        }
        return json.dumps(mock_data, ensure_ascii=False)
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """获取默认数据结构"""
        return {
            "enterprise_info": {},
            "certification_info": {},
            "technical_specs": {},
            "test_info": {},
            "certificate_info": {},
            "additional_info": {}
        }

# 创建全局实例
ai_extraction_service = AIExtractionService() 