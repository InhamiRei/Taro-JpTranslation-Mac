#!/bin/bash

echo "=================================="
echo "🚀 Taro-JpTranslation-Mac 🚀"
echo "=================================="
echo ""

# 检查 Python3 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python3: brew install python3"
    exit 1
fi

echo "✅ Python3 版本: $(python3 --version)"
echo ""

# 创建并激活虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建 Python 虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
    echo ""
fi

# 安装 Python 依赖
if [ ! -f "venv/.installed" ]; then
    echo "📦 安装 Python 依赖 (EasyOCR, Pillow 等)..."
    echo "   使用清华镜像源加速下载..."
    echo "   首次安装可能需要几分钟，请耐心等待..."
    echo ""
    ./venv/bin/pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    ./venv/bin/pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "❌ Python 依赖安装失败"
        exit 1
    fi
    touch venv/.installed
    echo ""
    echo "✅ Python 依赖安装完成"
    echo ""
fi

# 检测包管理器
if command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
    echo "📦 使用 Yarn 包管理器"
else
    PKG_MANAGER="npm"
    echo "📦 使用 NPM 包管理器"
fi
echo ""

# 检查是否已安装 Node 依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装 Node 依赖 (Electron, Sharp 等)..."
    echo "   使用淘宝镜像源加速下载..."
    echo ""
    if [ "$PKG_MANAGER" = "yarn" ]; then
        yarn install --registry=https://registry.npmmirror.com
    else
        npm install --registry=https://registry.npmmirror.com
    fi
    if [ $? -ne 0 ]; then
        echo "❌ Node 依赖安装失败"
        exit 1
    fi
    echo ""
    echo "✅ Node 依赖安装完成"
    echo ""
fi

echo "🔧 预加载 OCR 引擎（首次运行会下载模型）..."
echo ""

# 预加载OCR，避免首次翻译时等待
./venv/bin/python3 translator/preload_ocr.py
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  OCR 引擎初始化失败，但仍将启动应用"
    echo "   首次翻译时可能需要等待下载模型"
    echo ""
fi

echo ""
echo "✅ 所有依赖已安装，启动应用..."
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
