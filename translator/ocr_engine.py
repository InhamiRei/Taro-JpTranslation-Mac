# -*- coding: utf-8 -*-
"""
OCR Engine - PaddleOCR for Japanese
"""
import sys
import numpy as np
from PIL import Image

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


class OCREngine:
    """OCR Engine using PaddleOCR"""
    
    def __init__(self, lang='japan', use_textline_orientation=True, confidence_threshold=0.5):
        """Initialize PaddleOCR engine"""
        self.lang = lang
        self.use_textline_orientation = use_textline_orientation
        self.confidence_threshold = confidence_threshold
        self.ocr = None
        self._init_ocr()
    
    def _init_ocr(self):
        """Initialize PaddleOCR"""
        if not PADDLEOCR_AVAILABLE:
            print(f"❌ PaddleOCR未安装", file=sys.stderr)
            print(f"   请运行: pip install paddleocr paddlepaddle", file=sys.stderr)
            return
        
        try:
            print(f"🚀 初始化PaddleOCR引擎", file=sys.stderr)
            print(f"   首次使用会下载模型，请稍候...", file=sys.stderr)
            self.ocr = PaddleOCR(
                lang=self.lang,
                use_textline_orientation=self.use_textline_orientation
            )
            
            print(f"✅ PaddleOCR初始化成功", file=sys.stderr)
        except Exception as e:
            print(f"❌ PaddleOCR初始化失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    def recognize(self, image):
        """Recognize text from image"""
        if self.ocr is None:
            return []
        
        try:
            # 处理输入图像
            if isinstance(image, str):
                print(f"📂 加载图像: {image}", file=sys.stderr)
                image_path = image
                image = Image.open(image)
                print(f"   图像大小: {image.size}", file=sys.stderr)
            else:
                image_path = None
            
            # 转换为numpy数组（PaddleOCR需要）
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            print(f"🔍 使用PaddleOCR识别...", file=sys.stderr)
            
            # PaddleOCR识别（使用新API: predict）
            result = self.ocr.predict(image)
            
            # 新版PaddleOCR返回字典格式
            if not result or not isinstance(result, list) or len(result) == 0:
                print(f"   ⚠️ 未识别到文本", file=sys.stderr)
                return []
            
            # 获取第一个结果（字典格式）
            ocr_result = result[0]
            if not isinstance(ocr_result, dict):
                print(f"   ⚠️ 结果格式错误", file=sys.stderr)
                return []
            
            # 提取识别结果
            rec_texts = ocr_result.get('rec_texts', [])
            rec_scores = ocr_result.get('rec_scores', [])
            rec_polys = ocr_result.get('rec_polys', [])
            
            if not rec_texts:
                print(f"   ⚠️ 未识别到文本", file=sys.stderr)
                return []
            
            # 解析结果
            text_results = []
            filtered_count = 0
            
            for idx, (text, confidence, box) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
                # 置信度过滤
                if confidence < self.confidence_threshold:
                    filtered_count += 1
                    print(f"   [{idx+1}] {text} (置信度: {confidence:.2f}) ⚠️ 已过滤", file=sys.stderr)
                    continue
                
                print(f"   [{idx+1}] {text} (置信度: {confidence:.2f})", file=sys.stderr)
                
                text_results.append({
                    'text': text,
                    'confidence': confidence,
                    'box': box.tolist() if hasattr(box, 'tolist') else box
                })
            
            if filtered_count > 0:
                print(f"   ⚠️ 过滤了 {filtered_count} 个低置信度结果（< {self.confidence_threshold}）", file=sys.stderr)
            
            print(f"   识别到 {len(text_results)} 个文本块", file=sys.stderr)
            
            return text_results
        
        except Exception as e:
            print(f"OCR识别失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []
    
    def has_japanese_text(self, image):
        """Check if image contains Japanese text"""
        results = self.recognize(image)
        if not results:
            return False
        
        # 检查所有识别的文本
        for result in results:
            text = result['text']
            # 检查是否包含日文字符（平假名、片假名、汉字）
            japanese_ranges = [
                (0x3040, 0x309F),  # 平假名
                (0x30A0, 0x30FF),  # 片假名
                (0x4E00, 0x9FFF),  # CJK统一汉字
            ]
            
            for char in text:
                code = ord(char)
                for start, end in japanese_ranges:
                    if start <= code <= end:
                        return True
        
        return False
