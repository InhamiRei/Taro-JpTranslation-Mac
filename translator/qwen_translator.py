# -*- coding: utf-8 -*-
"""
Qwen Translator - Local translation via Ollama
"""
import sys
import json
from typing import List, Dict, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class QwenTranslator:
    """Qwen翻译器（通过Ollama）"""
    
    def __init__(self, model='qwen2.5:7b'):
        """
        初始化Qwen翻译器
        
        Args:
            model: Ollama模型名称，默认qwen2.5:7b
        """
        self.model = model
        self.available = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """检查Ollama服务是否可用"""
        if not OLLAMA_AVAILABLE:
            print(f"⚠️ Ollama Python库未安装", file=sys.stderr)
            print(f"   请运行: pip install ollama", file=sys.stderr)
            return False
        
        try:
            # 检查模型是否存在
            models_response = ollama.list()
            model_names = [m.model for m in models_response.models]
            
            if self.model in model_names:
                print(f"✅ Qwen翻译器可用 (模型: {self.model})", file=sys.stderr)
                return True
            else:
                print(f"⚠️ 未找到模型: {self.model}", file=sys.stderr)
                print(f"   请运行: ollama pull {self.model}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"⚠️ Ollama不可用: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return False
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        调用Ollama API（使用官方Python库）
        
        Args:
            prompt: 提示词
        
        Returns:
            生成的文本，失败返回None
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            return response['message']['content'].strip()
        except Exception as e:
            print(f"❌ Ollama调用失败: {e}", file=sys.stderr)
            return None
    
    def _clean_translation(self, text: str) -> str:
        """清理翻译结果，只处理明显的后缀解释"""
        # 只处理省略号后跟随的明显解释文本
        # 例如："自动... 解释内容" -> "自动"
        # 但保留原文中正常的省略号
        if '...' in text:
            parts = text.split('...')
            # 如果省略号后面有明显的解释性文字（较长），则截断
            if len(parts) > 1 and len(parts[1]) > 5:
                text = parts[0]
        
        return text.strip()
    
    def translate(self, text: str, fix_ocr=True) -> str:
        """
        翻译单个文本
        
        Args:
            text: 要翻译的日语文本
            fix_ocr: 是否启用OCR错误修正
        
        Returns:
            翻译后的中文
        """
        if not self.available:
            return "Qwen翻译器不可用"
        
        if not text or not text.strip():
            return ""
        
        # 构建提示词
        if fix_ocr:
            prompt = f"""你是专业的日中翻译助手。请完成以下任务：
1. 识别并修正OCR可能产生的错误（如字符识别错误）
2. 将修正后的日语翻译成简体中文
3. 保持原文的语气和敬语

原文：{text}

重要：只输出翻译后的中文结果，不要添加任何括号注释、解释说明或其他额外内容。"""
        else:
            prompt = f"""将以下日语翻译成简体中文，保持原文语气：

{text}

重要：只输出翻译结果，不要添加任何解释或注释。"""
        
        result = self._call_ollama(prompt)
        if result:
            result = self._clean_translation(result)
        return result if result else f"翻译失败: {text}"
    
    def translate_batch(self, texts: List[str], fix_ocr=True) -> List[str]:
        """
        批量翻译（优化性能）
        
        Args:
            texts: 要翻译的日语文本列表
            fix_ocr: 是否启用OCR错误修正
        
        Returns:
            翻译后的中文列表
        """
        if not self.available:
            return ["Qwen翻译器不可用"] * len(texts)
        
        if not texts:
            return []
        
        # 过滤空文本
        non_empty_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not non_empty_texts:
            return [""] * len(texts)
        
        # 构建批量翻译提示词
        numbered_texts = "\n".join([f"{i+1}. {t}" for i, t in non_empty_texts])
        
        if fix_ocr:
            prompt = f"""你是专业的日中翻译助手。请批量处理以下日语文本：
1. 识别并修正OCR可能产生的错误
2. 翻译成简体中文
3. 保持原文语气

原文列表：
{numbered_texts}

重要：请严格按照相同编号输出翻译结果，每行一个翻译，不要添加任何括号注释、解释说明或其他额外内容。
格式示例：
1. 翻译结果1
2. 翻译结果2"""
        else:
            prompt = f"""将以下日语文本翻译成简体中文：

{numbered_texts}

重要：请严格按照相同编号输出翻译结果，每行一个翻译，不要添加任何解释或注释。"""
        
        result = self._call_ollama(prompt)
        
        if not result:
            return [f"翻译失败: {t}" for _, t in non_empty_texts]
        
        # 解析结果
        translations = self._parse_batch_result(result, len(non_empty_texts))
        
        # 将翻译结果映射回原始位置
        final_results = [""] * len(texts)
        for (orig_idx, _), trans in zip(non_empty_texts, translations):
            final_results[orig_idx] = trans
        
        return final_results
    
    def _parse_batch_result(self, result: str, expected_count: int) -> List[str]:
        """解析批量翻译结果"""
        translations = []
        lines = result.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试匹配 "1. 翻译结果" 格式
            if line[0].isdigit() and '. ' in line:
                # 移除编号
                _, trans = line.split('. ', 1)
                trans = self._clean_translation(trans.strip())
                translations.append(trans)
            elif line:
                # 如果没有编号，直接添加
                trans = self._clean_translation(line)
                translations.append(trans)
        
        # 确保返回正确数量的翻译
        if len(translations) < expected_count:
            translations.extend(["翻译结果不完整"] * (expected_count - len(translations)))
        
        return translations[:expected_count]
    
    def fix_and_translate(self, ocr_results: List[Dict]) -> List[Dict]:
        """
        智能OCR修正+翻译
        
        Args:
            ocr_results: OCR识别结果列表，每项包含 {text, confidence, box}
        
        Returns:
            修正并翻译后的结果列表
        """
        if not self.available or not ocr_results:
            return ocr_results
        
        # 提取文本
        texts = [r['text'] for r in ocr_results]
        
        # 批量翻译
        translations = self.translate_batch(texts, fix_ocr=True)
        
        # 合并结果
        for result, translation in zip(ocr_results, translations):
            result['translated'] = translation
        
        return ocr_results
