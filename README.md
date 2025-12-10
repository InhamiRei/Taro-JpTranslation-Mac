# 为什么会有这个项目 🦌

看不懂日文，看不懂日文，看不懂日文！
我要玩 DMM 的 ミストトレインガールズ～霧の世界の車窓から～（迷雾列车少女）！

## ✨ 功能特性

- 🎯 **区域选择** - 框选需要翻译的屏幕区域
- 🔍 **OCR 识别** - 使用 PaddleOCR 识别日语文本（平假名、片假名、汉字）
- 🌐 **智能翻译** - Qwen 本地大模型翻译（主）+ 百度翻译 API（备用）
- 💎 **精准覆盖** - 翻译直接覆盖原文位置，字体大小自动匹配
- 👁️ **显示切换** - 随时切换显示/隐藏对比原文

## 📁 项目结构

```
jpTranslation/
├── src/                          # Electron 前端代码
│   ├── main.js                   # 主程序入口
│   ├── modules/                  # 功能模块
│   │   ├── window-manager.js     # 窗口管理
│   │   ├── translation-handler.js # 翻译处理
│   │   └── shortcut-handler.js   # 快捷键管理
│   └── views/                    # 窗口HTML
│       ├── region-selector.html  # 区域选择器
│       ├── region-overlay.html   # 区域边框
│       └── translation-window.html # 翻译窗口
│
├── translator/                   # Python 后端代码
│   ├── translate_service_server.py # 翻译服务主程序
│   ├── ocr_engine.py            # PaddleOCR 引擎封装
│   ├── qwen_translator.py       # Qwen 本地翻译（主）
│   └── baidu_translator.py      # 百度翻译API（备用）
│
├── config.py                    # 配置文件
├── requirements.txt             # Python 依赖
├── package.json                 # Node.js 依赖
└── run.sh                       # 启动脚本
```

**方式一：环境变量（推荐）**

```bash
# 设置环境变量
export BAIDU_APPID=你的APPID
export BAIDU_SECRET_KEY=你的密钥

# 或者使用 .env 文件
cp .env.example .env
# 编辑 .env 填入密钥
```

**方式二：config.json**

```bash
# 创建 config.json（不会被提交）
cat > config.json << 'EOF'
{
    "baidu_appid": "你的APPID",
    "baidu_secret_key": "你的密钥"
}
EOF
```

> 百度翻译 API 申请：https://fanyi-api.baidu.com/

### 3. 启动

```bash
./run.sh
```

## ⌨️ 快捷键

| 快捷键        | 功能              |
| ------------- | ----------------- |
| `Cmd+Shift+C` | 选择监听区域      |
| `Cmd+T`       | 翻译区域          |
| `Cmd+R`       | 切换翻译显示/隐藏 |
| `Cmd+Shift+Q` | 退出程序          |

## 💡 使用流程

1. **启动应用** - 运行 `./run.sh`
2. **选择区域** - 按 `Cmd+Shift+C`，拖动鼠标框选日语文本区域
3. **开始翻译** - 按 `Cmd+T`，等待识别和翻译（首次约 5 秒，后续 1-2 秒）
4. **查看结果** - 翻译会覆盖在原文上方，可拖动调整位置
5. **对比学习** - 按 `Cmd+R` 隐藏翻译查看原文，再按一次显示翻译
6. **继续翻译** - 画面变化时，直接按 `Cmd+T` 重新翻译

## 🔧 技术栈

### 前端

- **Electron** - 跨平台桌面应用框架
- **原生 JavaScript** - 无框架，轻量高效

### 后端

- **Python 3.12+**
- **PaddleOCR** - 高性能 OCR 文字识别
- **Ollama + Qwen2.5** - 本地大模型翻译（主翻译引擎）
- **百度翻译 API** - 在线翻译（备用引擎）
- **Pillow** - 图像处理
- **Requests** - HTTP 请求

## 📊 性能

- **首次翻译**：约 15 秒（初始化 PaddleOCR + Qwen 模型）
- **后续翻译**：5-10 秒（OCR 5 秒 + Qwen 翻译 5 秒）
- **OCR 精度**：95%+（PaddleOCR 日语识别）
- **翻译质量**：使用 Qwen2.5-7B 本地模型，理解上下文更准确
- **内存占用**：~1GB（包含 OCR 和 Qwen 模型）

## 📄 许可证

MIT License

---

**Enjoy translating! 🎉**
