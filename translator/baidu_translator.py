# -*- coding: utf-8 -*-
"""
百度翻译API封装
"""
import hashlib
import random
import requests


class BaiduTranslator:
    """百度翻译API"""
    
    def __init__(self, appid, secret_key):
        self.appid = appid
        self.secret_key = secret_key
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    
    def translate(self, text, from_lang='jp', to_lang='zh'):
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            from_lang: 源语言（jp=日语）
            to_lang: 目标语言（zh=中文）
        
        Returns:
            翻译结果文本
        """
        if not self.appid or not self.secret_key:
            return "请先配置百度翻译API密钥"
        
        if not text or not text.strip():
            return ""
        
        # 生成签名
        salt = str(random.randint(32768, 65536))
        sign_str = f"{self.appid}{text}{salt}{self.secret_key}"
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        # 构建请求参数
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=5)
            result = response.json()
            
            if 'trans_result' in result:
                translations = [item['dst'] for item in result['trans_result']]
                return '\n'.join(translations)
            elif 'error_code' in result:
                error_msg = self._get_error_message(result['error_code'])
                return f"翻译错误: {error_msg}"
            else:
                return "翻译失败"
        
        except Exception as e:
            return f"翻译异常: {str(e)}"
    
    def _get_error_message(self, error_code):
        """获取错误信息"""
        error_dict = {
            '52001': 'TIMEOUT - 请求超时',
            '52002': 'SYSTEM ERROR - 系统错误',
            '52003': 'UNAUTHORIZED USER - 未授权用户',
            '54000': 'REQUIRED PARAMETER IS NULL - 必填参数为空',
            '54001': 'INVALID SIGN - 签名错误',
            '54003': 'ACCESS FREQUENCY LIMITED - 访问频率受限',
            '54004': 'INSUFFICIENT ACCOUNT BALANCE - 账户余额不足',
            '54005': 'LONG QUERY TOO FREQUENTLY - 长查询请求过于频繁',
            '58000': 'CLIENT_IP_ILLEGAL - 客户端IP非法',
        }
        return error_dict.get(str(error_code), f'未知错误码: {error_code}')
