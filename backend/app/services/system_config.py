"""
系统配置服务
用于读取和管理系统参数配置
"""
import json
import os
from typing import Dict, Any, Optional
from flask import current_app


class SystemConfigService:
    """系统配置服务类"""
    
    def __init__(self):
        self._config_cache = None
        self._config_file_path = None
    
    def _get_config_file_path(self) -> str:
        """获取配置文件路径"""
        if self._config_file_path is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self._config_file_path = os.path.join(project_root, 'config', 'system_params.json')
        return self._config_file_path
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self._config_cache is not None:
            return self._config_cache
        
        config_path = self._get_config_file_path()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config_cache = json.load(f)
            return self._config_cache
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return self._get_default_config()
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version": {
                "version_1": 4,
                "version_2": 8,
                "version_3": 12,
                "version_4": 1
            },
            "laboratory": {
                "temperature": {
                    "value": 22,
                    "unit": "°C"
                },
                "ambient_pressure": {
                    "value": 1020,
                    "unit": "mbar"
                },
                "relative_humidity": {
                    "value": 50,
                    "unit": "%"
                }
            }
        }
    
    def get_version_params(self) -> Dict[str, int]:
        """获取版本号参数"""
        config = self._load_config()
        return config.get('version', {})
    
    def get_laboratory_params(self) -> Dict[str, str]:
        """获取实验室参数（拼接好的完整值）"""
        config = self._load_config()
        lab_config = config.get('laboratory', {})
        
        # 拼接值和单位
        result = {}
        for param_name, param_data in lab_config.items():
            if isinstance(param_data, dict) and 'value' in param_data and 'unit' in param_data:
                result[param_name] = f"{param_data['value']}{param_data['unit']}"
            else:
                # 如果已经是字符串，直接使用
                result[param_name] = str(param_data)
        
        return result
    
    def get_all_params(self) -> Dict[str, Any]:
        """获取所有系统参数"""
        return self._load_config()
    
    def reload_config(self):
        """重新加载配置文件（清除缓存）"""
        self._config_cache = None
        return self._load_config()


# 创建全局实例
system_config = SystemConfigService()
