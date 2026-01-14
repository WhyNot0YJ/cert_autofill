"""
文档提取服务包（仅规则引擎）
"""

from .document_extract import (
    DocumentExtractionService,
    document_extraction_service,
    rule_engine_service,
    BasePreprocessor,
    BaseExtractionStrategy
)

from .rule_engine_strategy import RuleEngineExtractionStrategy
from .templates.ordinary_laminated_glass_windscreen_template import OrdinaryLaminatedGlassWindscreenTemplate

__all__ = [
    'DocumentExtractionService',
    'document_extraction_service',
    'rule_engine_service',
    'BasePreprocessor',
    'BaseExtractionStrategy',
    'RuleEngineExtractionStrategy',
    'OrdinaryLaminatedGlassWindscreenTemplate'
]
