# -*- coding: utf-8 -*-
"""
配置文件
"""
import os
import json

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """
        加载配置
        
        优先级（从高到低）：
        1. 环境变量（BAIDU_APPID, BAIDU_SECRET_KEY）
        2. config.json 文件
        
        安全提示：
        - 不要在代码中硬编码API密钥
        - 使用 .env 文件或环境变量配置
        """
        default_config = {
            # 百度翻译API配置 - 从环境变量读取
            'baidu_appid': os.getenv('BAIDU_APPID', ''),
            'baidu_secret_key': os.getenv('BAIDU_SECRET_KEY', ''),
            
            # OCR设置
            'ocr_language': 'japan',
        }
        
        # 从config.json读取（可选）
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # config.json可以覆盖环境变量
                    if 'baidu_appid' in loaded_config and loaded_config['baidu_appid']:
                        default_config['baidu_appid'] = loaded_config['baidu_appid']
                    if 'baidu_secret_key' in loaded_config and loaded_config['baidu_secret_key']:
                        default_config['baidu_secret_key'] = loaded_config['baidu_secret_key']
                    # 其他配置项
                    for key in ['ocr_language']:
                        if key in loaded_config:
                            default_config[key] = loaded_config[key]
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 验证必需的配置
        if not default_config['baidu_appid'] or not default_config['baidu_secret_key']:
            print("⚠️  警告: 未设置百度翻译API密钥")
            print("   请设置环境变量: BAIDU_APPID 和 BAIDU_SECRET_KEY")
            print("   或创建 config.json 文件")
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self.config[key] = value
        self.save_config()
