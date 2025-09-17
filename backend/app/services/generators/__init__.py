#!/usr/bin/env python3
"""
文档生成器包
提供各种文档类型的生成功能
"""

from .base_generator import BaseGenerator
from .if_generator import IfGenerator, generate_if_document, generate_if_pdf_from_docx
from .cert_generator import CertGenerator, generate_cert_document , create_cert_sample_data
from .rcs_generator import RcsGenerator, generate_rcs_document, create_rcs_sample_data
from .other_generator import OtherGenerator, generate_other_document, create_other_sample_data
from .tr_generator import TrGenerator, generate_tr_document, create_tr_sample_data
from .tm_generator import TmGenerator, generate_tm_document, create_tm_sample_data

__all__ = [
    # 基础生成器
    'BaseGenerator',
    
    # IF文档生成器
    'IfGenerator',
    'generate_if_document',
    'generate_if_pdf_from_docx',
    
    # CERT证书生成器
    'CertGenerator',
    'generate_cert_document',
    'create_cert_sample_data',
    
    # RCS审查控制表生成器
    'RcsGenerator',
    'generate_rcs_document',
    'create_rcs_sample_data',
    
    # OTHER文档生成器
    'OtherGenerator',
    'generate_other_document',
    'create_other_sample_data',
    
    # TR技术报告生成器
    'TrGenerator',
    'generate_tr_document',
    'create_tr_sample_data',
    
    # TM技术备忘录生成器
    'TmGenerator',
    'generate_tm_document',
    'create_tm_sample_data',
    
]
