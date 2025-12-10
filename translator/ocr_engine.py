# -*- coding: utf-8 -*-
"""
OCR识别引擎 - 支持EasyOCR和PaddleOCR
优化:
- MPS GPU加速（M系列Mac）
- 图像预处理（二值化、对比度增强）
- 置信度过滤
"""
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import cv2

# 尝试导入EasyOCR（更好的日语支持）
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# 尝试导入PaddleOCR作为备选
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False


class OCREngine:
    """OCR识别引擎"""
    
    def __init__(self, lang='japan', use_gpu=True, confidence_threshold=0.5):
        """
        初始化OCR引擎
        
        Args:
            lang: 语言，japan=日语
            use_gpu: 是否使用GPU加速（M系列Mac使用MPS）
            confidence_threshold: 置信度阈值，低于此值的识别结果将被过滤
        """
        self.lang = lang
        self.use_gpu = use_gpu
        self.confidence_threshold = confidence_threshold
        self.ocr = None
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化OCR"""
        self.ocr = None
        self.ocr_type = None
        
        # 优先使用EasyOCR（日语支持更好）
        if EASYOCR_AVAILABLE:
            try:
                # 注意：EasyOCR在Mac上不支持MPS，只能使用CPU模式
                # 但图像预处理和置信度过滤仍会提升性能
                print(f"🔧 初始化EasyOCR引擎（日语 - CPU模式）", file=sys.stderr)
                print(f"   首次使用会下载模型，请稍候...", file=sys.stderr)
                print(f"   注意：EasyOCR暂不支持Mac GPU加速", file=sys.stderr)
                
                # EasyOCR支持多种语言，'ja'代表日语
                # Mac上gpu参数无效，统一使用False
                self.ocr = easyocr.Reader(['ja'], gpu=False)
                self.ocr_type = 'easyocr'
                
                print(f"✅ EasyOCR初始化成功 (日语模型)", file=sys.stderr)
                return
            except Exception as e:
                print(f"⚠️ EasyOCR初始化失败: {e}", file=sys.stderr)
        
        # 如果EasyOCR不可用，尝试PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                print(f"🔧 使用PaddleOCR（备选）", file=sys.stderr)
                
                self.ocr = PaddleOCR(
                    lang='japan',
                    use_textline_orientation=True
                )
                self.ocr_type = 'paddleocr'
                
                print(f"✅ PaddleOCR初始化成功", file=sys.stderr)
                return
            except Exception as e:
                print(f"⚠️ PaddleOCR初始化失败: {e}", file=sys.stderr)
        
        # 如果都失败了
        print(f"❌ 没有可用的OCR引擎", file=sys.stderr)
        print(f"   请安装: pip install easyocr", file=sys.stderr)
    
    def _preprocess_image(self, image):
        """
        图像预处理：二值化 + 对比度增强
        
        Args:
            image: PIL Image对象
        
        Returns:
            预处理后的PIL Image
        """
        # 转为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 对比度增强
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # 增强50%
        
        # 转为numpy数组进行二值化
        img_array = np.array(image)
        
        # 自适应阈值二值化（对不均匀光照效果更好）
        binary = cv2.adaptiveThreshold(
            img_array,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  # 邻域大小
            2    # 常数
        )
        
        # 转回PIL Image
        return Image.fromarray(binary)
    
    def recognize(self, image, preprocess=True):
        """
        识别图像中的文字
        
        Args:
            image: PIL Image对象、numpy数组或图像文件路径
            preprocess: 是否进行图像预处理
        
        Returns:
            识别结果列表，每项包含: (文本, 置信度, 坐标)
        """
        if self.ocr is None:
            return []
        
        try:
            # 如果是字符串路径，先加载图像
            if isinstance(image, str):
                print(f"📂 加载图像: {image}", file=sys.stderr)
                image_path = image
                image = Image.open(image)
                print(f"   图像大小: {image.size}", file=sys.stderr)
            else:
                image_path = None
            
            # 图像预处理
            if preprocess:
                print(f"🔧 预处理图像（二值化+对比度增强）", file=sys.stderr)
                image = self._preprocess_image(image)
            
            # 根据OCR类型执行识别
            if self.ocr_type == 'easyocr':
                return self._recognize_easyocr(image, image_path)
            elif self.ocr_type == 'paddleocr':
                return self._recognize_paddleocr(image)
            else:
                return []
        
        except Exception as e:
            print(f"OCR识别失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []
    
    def _recognize_easyocr(self, image, image_path=None):
        """使用EasyOCR识别"""
        print(f"🔍 使用EasyOCR识别...", file=sys.stderr)
        
        # 转换为numpy数组
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # EasyOCR识别
        result = self.ocr.readtext(image)
        
        if not result:
            print(f"   未识别到文本", file=sys.stderr)
            return []
        
        print(f"   识别到 {len(result)} 个文本块", file=sys.stderr)
        
        # EasyOCR返回格式: (bbox, text, confidence)
        text_results = []
        filtered_count = 0
        for idx, (bbox, text, confidence) in enumerate(result):
            # 置信度过滤
            if confidence < self.confidence_threshold:
                filtered_count += 1
                print(f"   [{idx+1}] {text} (置信度: {confidence:.2f}) ⚠️ 已过滤", file=sys.stderr)
                continue
            
            # bbox是 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            print(f"   [{idx+1}] {text} (置信度: {confidence:.2f})", file=sys.stderr)
            
            text_results.append({
                'text': text,
                'confidence': confidence,
                'box': bbox
            })
        
        if filtered_count > 0:
            print(f"   ⚠️ 过滤了 {filtered_count} 个低置信度结果（< {self.confidence_threshold}）", file=sys.stderr)
        
        return text_results
    
    def _recognize_paddleocr(self, image):
        """使用PaddleOCR识别"""
        print(f"🔍 使用PaddleOCR识别...", file=sys.stderr)
        
        # 转换为numpy数组
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # PaddleOCR识别
        result = self.ocr.ocr(image)
        
        if not result or not result[0]:
            print(f"   未识别到文本", file=sys.stderr)
            return []
        
        print(f"   识别到 {len(result[0])} 个文本块", file=sys.stderr)
        
        # PaddleOCR返回格式解析
        text_results = []
        for idx, line in enumerate(result[0]):
            if line:
                try:
                    box = line[0]
                    text_info = line[1]
                    
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                        text = text_info[0]
                        confidence = text_info[1]
                    elif isinstance(text_info, str):
                        text = text_info
                        confidence = 1.0
                    else:
                        continue
                    
                    print(f"   [{idx+1}] {text} (置信度: {confidence:.2f})", file=sys.stderr)
                    
                    text_results.append({
                        'text': text,
                        'confidence': confidence,
                        'box': box
                    })
                except Exception as e:
                    print(f"   ⚠️ 解析失败: {e}", file=sys.stderr)
                    continue
        
        return text_results
    
    def recognize_text_only(self, image):
        """
        仅返回识别的文本（拼接成一个字符串）
        
        Args:
            image: PIL Image对象或numpy数组
        
        Returns:
            识别的文本字符串
        """
        results = self.recognize(image)
        if not results:
            return ""
        
        # 拼接所有文本
        texts = [r['text'] for r in results]
        return '\n'.join(texts)
    
    def has_japanese_text(self, image):
        """
        检查图像是否包含日文
        
        Args:
            image: PIL Image对象或numpy数组
        
        Returns:
            布尔值
        """
        text = self.recognize_text_only(image)
        if not text:
            return False
        
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
