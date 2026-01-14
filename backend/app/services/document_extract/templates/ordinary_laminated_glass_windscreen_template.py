"""
普通层压玻璃挡风玻璃模板提取策略

专门用于提取普通层压玻璃挡风玻璃信息文件夹（Information Folder）的文档信息
"""

import re
import logging
from typing import Dict, Any

from ..rule_engine_strategy import RuleEngineExtractionStrategy

logger = logging.getLogger(__name__)


class OrdinaryLaminatedGlassWindscreenTemplate(RuleEngineExtractionStrategy):
    """普通层压玻璃挡风玻璃模板提取策略
    
    实现功能：
    - 提取挡风玻璃的基本信息（批准号、信息文件夹号、安全等级等）
    - 提取制造商信息和商标名称
    - 提取玻璃结构信息（层数、厚度、类型等）
    - 提取车辆适用信息（车辆制造商、类型、几何参数等）
    - 后处理商标名称、选择字段、夹层颜色等数据
    """

    def _build_field_patterns(self) -> Dict[str, Dict[str, Any]]:
        """构建普通层压玻璃挡风玻璃模板的字段提取规则"""
        # 通用模式创建函数
        def create_patterns(pattern):
            return {'patterns': [pattern], 'priority': 1}
        
        return {
            'approval_no': create_patterns(
                r'Approval\s+No\s*\n\s*([A-Z0-9\*\/\-]+)'  # 匹配英文批准号格式，换行后跟字母数字和特殊字符
            ),
            'information_folder_no': create_patterns(
                r'Information\s+folder\s+number\s*:\s*([0-9]+)'  # 匹配英文信息文件夹号，冒号后跟数字
            ),
            'safety_class': create_patterns(
                r'Class\s+of\s+safety-glass\s+pane\s*:\s*([^:\n]+)'  # 匹配英文安全等级，冒号后跟非冒号换行字符
            ),
            'pane_desc': create_patterns(
                r'Description\s+of\s+glass\s+pane\s*:\s*([^:\n]+)'  # 匹配英文玻璃板描述，冒号后跟非冒号换行字符
            ),
            'trade_names': create_patterns(
                r'Trade\s+name\s*:\s*([^:\n]+(?:\n[^:\n]+)*?)(?=\nName\s+and\s+address\s+of\s+manufacturer)'  # 匹配Trade name和Name and address of manufacturer之间的内容
            ),
            'company_name': create_patterns(
                r'Name\s+and\s+address\s+of\s+manufacturer\s*:?\s*(?:\n\s*[:]*\s*)?([^\n]+)'  # 匹配制造商名称：支持值在下一行且包含逗号
            ),
            'company_address': create_patterns(
                r'Name\s+and\s+address\s+of\s+manufacturer\s*:?\s*(?:\n\s*[:]*\s*)?(?:[^\n]*\n)([\s\S]*?)(?=^(?:Principal\s+characteristics|Secondary\s+characteristics|Number\s+of\s+layers|Remarks)\b|\Z)'  # 跳过首行名称，捕获后续多行地址，直到下一节标题行
            ),
            'glass_layers': create_patterns(
                r'Number\s+of\s+layers\s+of\s+glass\s*:\s*(\d+)'  # 匹配英文玻璃层数，冒号后跟数字
            ),
            'interlayer_layers': create_patterns(
                r'Number\s+of\s+layers\s+of\s+interlayer\s*:\s*(\d+)'  # 匹配英文夹层数，冒号后跟数字
            ),
            'windscreen_thick': create_patterns(
                r'Nominal\s+thickness\s+of\s+the\s+windscreen\s*:\s*([0-9.]+)\s*mm'  # 匹配英文风窗厚度，冒号后跟数字加mm
            ),
            'interlayer_thick': create_patterns(
                r'Nominal\s+thickness\s+of\s+interlayer\(s\)\s*:\s*([0-9.]+)\s*mm'  # 匹配英文夹层厚度，冒号后跟数字加mm
            ),
            'glass_treatment': create_patterns(
                r'Special\s+treatment\s+of\s+glass\s*:\s*([^:\n]+)'  # 匹配英文玻璃处理，冒号后跟非冒号换行字符
            ),
            'interlayer_type': create_patterns(
                r'Nature\s+and\s+type\s+of\s+interlayer\(s\)\s*:\s*([^:\n]+)'  # 匹配英文夹层类型，冒号后跟非冒号换行字符
            ),
            'coating_type': create_patterns(
                r'Nature\s+and\s+type\s+of\s+plastics\s+coating\(s\)\s*:\s*([^:\n]+)'  # 匹配英文涂层类型，冒号后跟非冒号换行字符
            ),
            'coating_thick': create_patterns(
                r'Nominal\s+thickness\s+of\s+plastic\s+coating\(s\)\s*:\s*([^:\n]+)'  # 匹配英文涂层厚度，冒号后跟非冒号换行字符
            ),
            'material_nature': create_patterns(
                r'Nature\s+of\s+the\s+material\s*\([^)]+\)\s*:\s*([^:\n]+)'  # 匹配英文材料性质，括号内容后冒号跟非冒号换行字符
            ),
            'glass_color_choice': create_patterns(
                r'Colouring\s+of\s+glass\s*\([^)]+\)\s*:\s*([^:\n]+)'  # 匹配英文玻璃颜色，括号内容后冒号跟非冒号换行字符
            ),
            'coating_color': create_patterns(
                r'Colouring\s+of\s+plastics\s+coating\(s\)\s*:\s*([^:\n]+)'  # 匹配英文涂层颜色，冒号后跟非冒号换行字符
            ),
            'interlayer_coloring': create_patterns(
                r'Colouring\s+of\s+interlayer\s*\([^)]+\)\s*:\s*([^:\n]+)'  # 匹配英文夹层颜色，括号内容后冒号跟非冒号换行字符
            ),
            'conductors': create_patterns(
                r'Conductors\s+incorporated\s*\([^)]+\)\s*:\s*([^:\n]+)'  # 匹配英文导体信息，括号内容后冒号跟非冒号换行字符
            ),
            'opaque_obscuration': create_patterns(
                r'Opaque\s+obscuration\s+incorporated\s*\([^)]+\)\s*:\s*([^:\n]+)'  # 匹配英文不透明模糊信息，括号内容后冒号跟非冒号换行字符
            ),
            'remarks': create_patterns(
                r'Remarks\s*:\s*([^:\n]+)'  # 匹配英文备注，冒号后跟非冒号换行字符
            )
        }

    def _apply_extraction_rules(self, text: str) -> Dict[str, Any]:
        """应用正则表达式规则提取字段"""
        extracted_data = {}
        
        # 保存原始文本供后处理使用
        extracted_data['_original_text'] = text
        
        # 提取主要字段
        for field_name, field_config in self.field_patterns.items():
            extracted_data[field_name] = self._extract_field_value(text, field_config)
        
        # 提取车辆信息
        vehicles = self._extract_vehicles(text)
        extracted_data['vehicles'] = vehicles
        
        return extracted_data

    def _extract_vehicles(self, text: str) -> list:
        """提取车辆信息列表 - 整段匹配模式"""
        vehicles = []
        
        # 查找车辆信息段落 - 使用整段正则表达式匹配
        vehicle_sections = re.findall(
            r'Vehicle\s+manufacturer\s*:\s*([^:\n]+)'
            r'.*?Type\s+of\s+vehicle\s*:\s*([^:\n]+)'
            r'.*?Vehicle\s+category\s*:\s*([^:\n]+)'
            r'.*?Developed\s+area\s*\(F\)[\s\S]*?([0-9.]+)\s*m2'
            r'.*?Height\s+of\s+segment\s*\(h\)[\s\S]*?([0-9.]+)\s*mm'
            r'.*?Curvature\s*\(r\)[\s\S]*?([0-9.]+)\s*mm'
            r'.*?Installation\s+angle\s*\([^)]+\)[\s\S]*?([0-9.]+)\s*°?'
            r'.*?Seat-back\s+angle\s*\([^)]+\)[\s\S]*?([0-9.]+)\s*°?'
            r'.*?R-point\s+coordinates[\s\S]*?A:\s*([0-9.]+)\s*mm'
            r'[\s\S]*?B:\s*±?([0-9.]+)\s*mm'
            r'[\s\S]*?C:\s*([0-9.]+)\s*mm'
            r'.*?Description\s+of\s+the\s+commercially\s+available\s+specific\s+device[^:]*:\s*([^\n:]+)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        # 处理每个匹配到的车辆段落
        for section in vehicle_sections:
            # 所有字段都是必需的，直接访问即可
            vehicle = {
                'veh_mfr': section[0].strip(),
                'veh_type': section[1].strip(),
                'veh_cat': section[2].strip(),
                'dev_area': section[3].strip(),
                'seg_height': section[4].strip(),
                'curv_radius': section[5].strip(),
                'inst_angle': section[6].strip(),
                'seat_angle': section[7].strip(),
                'rpoint_coords': {
                    'A': section[8].strip(),
                    'B': section[9].strip(),
                    'C': section[10].strip()
                },
                'dev_desc': section[11].strip()
            }
            vehicles.append(vehicle)
        
        return vehicles

    def _post_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """后处理提取的数据"""
        processed = data.copy()

        # 将第一页图片保存后的路径暴露给模板使用（用于提取商标）
        if '_first_page_images' in processed:
            processed['trade_marks'] = processed['_first_page_images']
            processed.pop('_first_page_images', None)

        # 处理商标名称 - 正确分割和清理
        if 'trade_names' in processed:
            trade_names = processed['trade_names']
            # 清理换行符和多余空格
            trade_names = re.sub(r'\s+', ' ', trade_names)
            # 清理多余的分号（连续的分号替换为单个分号）
            trade_names = re.sub(r';+', ';', trade_names)
            # 清理开头和结尾的分号
            trade_names = trade_names.strip('; ')
            
            # 按分号分割商标名称
            if trade_names:
                # 分割并清理每个商标名称
                name_list = [name.strip() for name in trade_names.split(';') if name.strip()]
                # 重新组合为分号+空格分隔的字符串
                processed['trade_names'] = '; '.join(name_list)
            else:
                processed['trade_names'] = ''
        
        # 处理选择字段 - 统一转换为数组格式
        choice_fields = {
            'conductors': ('conductors_choice', ['yes', 'no']),
            'opaque_obscuration': ('opaque_obscure_choice', ['yes', 'no']),
            'glass_color_choice': ('glass_color_choice', ['colourless', 'tinted'])
        }
        
        for source_field, (target_field, options) in choice_fields.items():
            if source_field in processed:
                value = processed[source_field].lower()
                result = []
                
                # 检查每个选项是否在值中
                for option in options:
                    if option in value:
                        result.append(option)
                
                # 如果都不包含，返回空数组
                processed[target_field] = result if result else []
            else:
                processed[target_field] = []
        
        # 处理夹层颜色
        if 'interlayer_coloring' in processed:
            coloring_value = processed['interlayer_coloring'].lower()
            processed['interlayer_total'] = 'total' in coloring_value
            processed['interlayer_partial'] = 'partial' in coloring_value
            processed['interlayer_colourless'] = 'colourless' in coloring_value
    
        
        # 清理不需要的临时字段
        temp_fields = ['conductors', 'opaque_obscuration', 'interlayer_coloring', '_original_text']
        for field in temp_fields:
            processed.pop(field, None)
        
        return processed

