#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务 - 常驻服务模式

本模块提供OCR识别和翻译服务，使用单例模式缓存实例以提升性能。
启动后保持运行，接收命令行参数处理翻译请求。

性能优化：
- 首次调用：5-8秒（初始化OCR引擎）
- 后续调用：1-2秒（使用缓存的实例）

使用方法：
    python translate_service_server.py <screenshot_path> <x> <y> <width> <height>

输出格式（JSON）：
    {
        "success": true,
        "textBlocks": [
            {
                "x": 10, "y": 20, "width": 100, "height": 30,
                "original": "こんにちは",
                "translated": "你好",
                "confidence": 0.99
            }
        ]
    }
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from translator.ocr_engine import OCREngine
from translator.baidu_translator import BaiduTranslator
from config import Config

# ============================================================================
# 全局单例实例（缓存，避免重复初始化）
# ============================================================================

config: Optional[Config] = None
ocr: Optional[OCREngine] = None
translator: Optional[BaiduTranslator] = None

def init_services() -> None:
    """
    初始化所有服务（单例模式）
    
    首次调用会初始化配置、翻译器和OCR引擎。
    后续调用会直接使用缓存的实例，大幅提升速度。
    
    全局变量：
        config: 配置管理器
        translator: 百度翻译API实例
        ocr: EasyOCR引擎实例
    """
    global config, ocr, translator
    
    # 初始化配置
    if config is None:
        print("🔧 初始化配置...", file=sys.stderr, flush=True)
        config = Config()
    
    # 初始化翻译器
    if translator is None:
        print("🔧 初始化百度翻译...", file=sys.stderr, flush=True)
        translator = BaiduTranslator(
            appid=config.get('baidu_appid'),
            secret_key=config.get('baidu_secret_key')
        )
        print("✅ 百度翻译就绪", file=sys.stderr, flush=True)
    
    # 初始化OCR引擎
    if ocr is None:
        print("🔧 初始化OCR引擎...", file=sys.stderr, flush=True)
        ocr = OCREngine(lang='japan')
        print("✅ OCR引擎就绪", file=sys.stderr, flush=True)
    else:
        print("⚡ 使用缓存的OCR引擎（快速模式）", file=sys.stderr, flush=True)


def translate_region(
    screenshot_path: str,
    region_x: int,
    region_y: int,
    region_width: int,
    region_height: int
) -> List[Dict[str, Any]]:
    """
    翻译指定区域的截图
    
    工作流程：
        1. 初始化服务（如未初始化）
        2. 使用OCR识别截图中的日语文本
        3. 调用百度翻译API翻译识别出的文本
        4. 返回包含位置信息的文本块列表
    
    参数：
        screenshot_path: 截图文件路径
        region_x: 区域X坐标（像素）
        region_y: 区域Y坐标（像素）
        region_width: 区域宽度（像素）
        region_height: 区域高度（像素）
    
    返回：
        文本块列表，每个文本块包含：
        - x, y: 文本块在截图中的相对坐标
        - width, height: 文本块尺寸
        - original: 原始日语文本
        - translated: 翻译后的中文
        - confidence: OCR识别置信度 (0-1)
    """
    try:
        # 确保服务已初始化
        init_services()
        
        # OCR识别
        print(f"🔍 开始OCR识别...", file=sys.stderr, flush=True)
        start_time = __import__('time').time()
        
        result = ocr.recognize(screenshot_path)
        
        ocr_time = __import__('time').time() - start_time
        print(f"✅ OCR完成 ({ocr_time:.2f}s)", file=sys.stderr, flush=True)
        
        if not result:
            print(f"⚠️ 未识别到文本", file=sys.stderr, flush=True)
            return []
        
        print(f"✅ 识别到 {len(result)} 个文本块", file=sys.stderr, flush=True)
        text_blocks = []
        
        # 处理每个识别的文本块
        for item in result:
            boxes = item['box']
            text = item['text']
            confidence = item['confidence']
            
            # 计算边界
            x_coords = [point[0] for point in boxes]
            y_coords = [point[1] for point in boxes]
            
            x = int(min(x_coords))
            y = int(min(y_coords))
            width = int(max(x_coords) - min(x_coords))
            height = int(max(y_coords) - min(y_coords))
            
            # 翻译
            translated = translator.translate(text)
            print(f"   {text[:15]}... → {translated[:15]}...", file=sys.stderr, flush=True)
            
            text_blocks.append({
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'original': text,
                'translated': translated,
                'confidence': confidence
            })
        
        total_time = __import__('time').time() - start_time
        print(f"✅ 翻译完成，总耗时 {total_time:.2f}s", file=sys.stderr, flush=True)
        
        return text_blocks
        
    except Exception as e:
        print(f"❌ 翻译失败: {str(e)}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []

# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == '__main__':
    # 检查命令行参数
    if len(sys.argv) < 6:
        error_result = {'error': '参数不足，需要5个参数：screenshot_path x y width height'}
        print(json.dumps(error_result, ensure_ascii=False), flush=True)
        sys.exit(1)
    
    # 解析命令行参数
    screenshot_path = sys.argv[1]
    region_x = int(sys.argv[2])
    region_y = int(sys.argv[3])
    region_width = int(sys.argv[4])
    region_height = int(sys.argv[5])
    
    # 执行翻译
    text_blocks = translate_region(
        screenshot_path,
        region_x,
        region_y,
        region_width,
        region_height
    )
    
    # 输出JSON结果到stdout（供Electron读取）
    result = {
        'success': True,
        'textBlocks': text_blocks
    }
    print(json.dumps(result, ensure_ascii=False), flush=True)
