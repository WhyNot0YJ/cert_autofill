#!/usr/bin/env python3
"""
JSON字段处理工具类
统一处理JSON字段的验证和转换逻辑
"""
import json
from typing import Any, List, Dict, Union, Optional


class JSONFieldHandler:
    """JSON字段处理工具类"""
    
    @staticmethod
    def process_json_field(
        data: Dict[str, Any], 
        field_name: str, 
        expected_type: type = list,
        allow_none: bool = True,
        custom_validator: Optional[callable] = None
    ) -> Optional[str]:
        """
        统一处理JSON字段的验证和转换
        
        Args:
            data: 包含字段数据的字典
            field_name: 字段名称
            expected_type: 期望的数据类型（list或dict）
            allow_none: 是否允许None值
            custom_validator: 自定义验证函数
            
        Returns:
            JSON字符串或None
            
        Raises:
            ValueError: 字段验证失败时抛出
        """
        if field_name not in data:
            return None
        
        value = data[field_name]
        
        # 处理None或空字符串
        if value is None or value == '':
            return None if allow_none else json.dumps([] if expected_type == list else {})
        
        # 如果已经是期望的类型，直接转换
        if isinstance(value, expected_type):
            return json.dumps(value, ensure_ascii=False)
        
        # 如果是字符串，尝试解析
        elif isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, expected_type):
                    return value  # 返回原始字符串
                else:
                    raise ValueError(f"{field_name}字段必须是{expected_type.__name__}类型")
            except json.JSONDecodeError:
                raise ValueError(f"{field_name}字段格式错误，必须是有效的JSON格式")
        
        # 其他类型
        else:
            raise ValueError(f"{field_name}字段必须是{expected_type.__name__}或JSON字符串")
    
    @staticmethod
    def process_trade_names(data: Dict[str, Any]) -> Optional[str]:
        """
        处理商标名称字段
        
        Args:
            data: 包含trade_names字段的数据字典
            
        Returns:
            JSON字符串或None
        """
        return JSONFieldHandler.process_json_field(
            data, 'trade_names', list, allow_none=True
        )
    
    @staticmethod
    def process_trade_marks(data: Dict[str, Any]) -> Optional[str]:
        """
        处理商标图片字段
        
        Args:
            data: 包含trade_marks字段的数据字典
            
        Returns:
            JSON字符串或None
        """
        return JSONFieldHandler.process_json_field(
            data, 'trade_marks', list, allow_none=True
        )
    
    @staticmethod
    def process_equipment(data: Dict[str, Any]) -> Optional[str]:
        """
        处理设备信息字段
        
        Args:
            data: 包含equipment字段的数据字典
            
        Returns:
            JSON字符串或None
        """
        def validate_equipment(equipment_list: List[Dict[str, Any]]) -> bool:
            """验证设备信息格式"""
            if not isinstance(equipment_list, list):
                return False
            
            for item in equipment_list:
                if not isinstance(item, dict) or 'no' not in item or 'name' not in item:
                    return False
            return True
        
        try:
            result = JSONFieldHandler.process_json_field(
                data, 'equipment', list, allow_none=True
            )
            
            # 如果结果不为None，验证设备信息格式
            if result:
                equipment_list = json.loads(result)
                if not validate_equipment(equipment_list):
                    raise ValueError("设备信息格式错误，每个设备必须包含no(编号)和name(名称)字段")
            
            return result
        except ValueError as e:
            raise ValueError(f"equipment字段{str(e)}")
    
    @staticmethod
    def process_vehicles(data: Dict[str, Any]) -> Optional[str]:
        """
        处理车辆信息字段
        
        Args:
            data: 包含vehicles字段的数据字典
            
        Returns:
            JSON字符串或None
        """
        return JSONFieldHandler.process_json_field(
            data, 'vehicles', list, allow_none=True
        )
    
    @staticmethod
    def parse_json_field(json_str: Optional[str], default: Any = None) -> Any:
        """
        解析JSON字符串字段
        
        Args:
            json_str: JSON字符串
            default: 默认值
            
        Returns:
            解析后的对象或默认值
        """
        if not json_str:
            return default
        
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default
