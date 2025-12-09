#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预加载OCR引擎 - 在应用启动时运行
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from translator.ocr_engine import OCREngine
from config import Config

if __name__ == '__main__':
    print("="*60, file=sys.stderr)
    print("🚀 预加载OCR引擎和翻译服务", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    # 加载配置
    config = Config()
    
    # 初始化OCR引擎（会触发模型下载）
    print("\n📦 初始化OCR引擎...", file=sys.stderr)
    ocr = OCREngine(lang='japan')
    
    if ocr.ocr is not None:
        print("✅ OCR引擎准备就绪", file=sys.stderr)
    else:
        print("❌ OCR引擎初始化失败", file=sys.stderr)
        sys.exit(1)
    
    # 测试识别（可选）
    print("\n✅ 预加载完成！", file=sys.stderr)
    print("="*60, file=sys.stderr)
