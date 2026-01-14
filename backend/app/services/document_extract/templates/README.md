# 文档提取模板

此文件夹包含各种特定类型文档的提取模板策略。

## 架构说明

### 基类：`RuleEngineExtractionStrategy`
位于 `rule_engine_strategy.py`，提供通用功能：
- 文档文本提取（DOCX、PDF、DOC等格式）
- 通用字段值正则匹配逻辑
- 可扩展的规则引擎框架

### 子类模板
每个特定类型的文档都有自己的模板类，继承自基类并实现特定的提取逻辑。

## 现有模板

### 1. OrdinaryLaminatedGlassWindscreenTemplate
**文件**: `ordinary_laminated_glass_windscreen_template.py`

**用途**: 提取普通层压玻璃挡风玻璃信息文件夹（Information Folder）的文档信息

**提取内容**:
- 基本信息：批准号、信息文件夹号、安全等级等
- 制造商信息和商标名称
- 玻璃结构信息：层数、厚度、类型等
- 车辆适用信息：车辆制造商、类型、几何参数等

**实现方法**:
- `_build_field_patterns()`: 定义字段提取的正则表达式规则
- `_apply_extraction_rules()`: 应用规则提取字段
- `_extract_vehicles()`: 提取车辆信息列表
- `_post_process_data()`: 后处理数据（商标名称、选择字段等）

## 如何添加新模板

1. 在 `templates/` 文件夹下创建新的模板文件，如 `your_template.py`
2. 继承 `RuleEngineExtractionStrategy` 基类
3. 实现以下抽象方法：
   - `_build_field_patterns()`: 定义字段提取规则
   - `_apply_extraction_rules()`: 应用提取规则
   - `_post_process_data()`: 后处理提取的数据
4. 在 `templates/__init__.py` 中导出新模板类
5. 在 `document_extract/__init__.py` 中添加导出（如需要）

## 示例代码

```python
from ..rule_engine_strategy import RuleEngineExtractionStrategy

class YourTemplate(RuleEngineExtractionStrategy):
    """您的模板说明"""
    
    def _build_field_patterns(self):
        # 定义字段提取规则
        return {
            'field_name': {
                'patterns': [r'pattern1', r'pattern2'],
                'priority': 1
            }
        }
    
    def _apply_extraction_rules(self, text):
        # 应用提取规则
        extracted = {}
        for field, config in self.field_patterns.items():
            extracted[field] = self._extract_field_value(text, config)
        return extracted
    
    def _post_process_data(self, data):
        # 后处理数据
        return data
```

## 通用工具方法（基类提供）

- `_extract_text_from_file(file_path)`: 从文件提取文本
- `_extract_docx_text(file_path)`: 从DOCX提取文本
- `_extract_pdf_text(file_path)`: 从PDF提取文本
- `_convert_doc_to_docx(file_path)`: DOC转DOCX
- `_extract_field_value(text, field_config)`: 使用正则提取字段值

