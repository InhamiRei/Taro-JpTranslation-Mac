#!/bin/bash

echo "=================================="
echo "🚀 Taro-JpTranslation-Mac 🚀"
echo "=================================="
echo ""

# 检测包管理器
if command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
    echo "📦 使用 Yarn 包管理器"
else
    PKG_MANAGER="npm"
    echo "📦 使用 NPM 包管理器"
fi
echo ""

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    echo ""
    if [ "$PKG_MANAGER" = "yarn" ]; then
        yarn install
    else
        npm install
    fi
    echo ""
fi

echo "🔧 预加载OCR引擎（首次运行会下载模型）..."
echo ""

# 预加载OCR，避免首次翻译时等待
if [ -f "venv/bin/python3" ]; then
    ./venv/bin/python3 translator/preload_ocr.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  OCR引擎初始化失败，但仍将启动应用"
        echo "   首次翻译时可能需要等待下载模型"
        echo ""
    fi
else
    echo "⚠️  虚拟环境不存在，跳过预加载"
    echo ""
fi

echo ""
echo "✅ 启动应用..."
echo ""
echo "快捷键说明："
echo "  Cmd+Shift+C  →  选择监听区域"
echo "  Cmd+T         →  翻译监听区域"
echo "  Cmd+Shift+Q  →  退出程序"
echo ""
echo "=================================="
echo ""

if [ "$PKG_MANAGER" = "yarn" ]; then
    yarn start
else
    npm start
fi
