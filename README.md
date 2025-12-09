# 为什么会有这个项目 🎮

因为我要玩 DMM 的 ミストトレインガールズ～霧の世界の車窓から～（迷雾列车少女），看不懂日文思密达，🦌🦌🦌~

## ✨ 功能特性

- 🎯 **区域选择** - 框选需要翻译的屏幕区域
- 🔍 **OCR 识别** - 使用 EasyOCR 识别日语文本（平假名、片假名、汉字）
- 🌐 **在线翻译** - 百度翻译 API，准确度高
- 💎 **精准覆盖** - 翻译直接覆盖原文位置，字体大小自动匹配
- 🖱️ **可拖动** - 翻译窗口可拖动调整
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
│   ├── ocr_engine.py            # OCR 引擎封装
│   └── baidu_translator.py      # 百度翻译API
│
├── config.py                    # 配置文件
├── requirements.txt             # Python 依赖
├── package.json                 # Node.js 依赖
└── run.sh                       # 启动脚本
```

## 🚀 快速开始

### 1. 安装依赖

#### Node.js 依赖

```bash
yarn install
# 或
npm install
```

#### Python 依赖

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 API 密钥

> ⚠️ **重要**：API 密钥不要提交到 Git！使用环境变量或 config.json（已在.gitignore 中）

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

或手动启动：

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动应用
yarn start
# 或 npm start
```

## ⌨️ 快捷键

| 快捷键                                              | 功能              |
| --------------------------------------------------- | ----------------- |
| `Cmd+Shift+C` (Mac) <br> `Ctrl+Shift+C` (Win/Linux) | 选择监听区域      |
| `Cmd+T` (Mac) <br> `Ctrl+T` (Win/Linux)             | 翻译区域          |
| `Cmd+R` (Mac) <br> `Ctrl+R` (Win/Linux)             | 切换翻译显示/隐藏 |
| `Cmd+Shift+Q` (Mac) <br> `Ctrl+Shift+Q` (Win/Linux) | 退出程序          |

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
- **EasyOCR** - OCR 文字识别
- **Pillow** - 图像处理
- **Requests** - HTTP 请求

## 📊 性能

- **首次翻译**：5-8 秒（初始化 OCR 模型）
- **后续翻译**：1-2 秒（使用缓存实例）
- **OCR 精度**：99%+（日语识别）
- **内存占用**：~300MB

## 📄 许可证

MIT License

---

**Enjoy translating! 🎉**
