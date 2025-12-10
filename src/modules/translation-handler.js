/**
 * 翻译处理模块
 * 负责截图、OCR识别和翻译的核心逻辑
 *
 * 性能优化：使用常驻Python进程，避免每次翻译都重新初始化
 */

const { desktopCapturer, screen } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const sharp = require("sharp");

// ============================================================================
// Python常驻服务管理
// ============================================================================

/** @type {ChildProcess|null} 常驻的Python翻译服务进程 */
let pythonDaemon = null;

/** @type {Array<{resolve: Function, reject: Function}>} 等待响应的请求队列 */
let requestQueue = [];

/** @type {string} 缓存的stdout输出 */
let stdoutBuffer = "";

/**
 * 启动常驻Python翻译服务
 */
function startPythonDaemon() {
  if (pythonDaemon) {
    console.log("⚡ Python服务已在运行");
    return;
  }

  const pythonScript = path.join(
    __dirname,
    "../../translator/translate_service_server.py"
  );
  const projectRoot = path.join(__dirname, "../..");
  const venvPython = path.join(projectRoot, "venv/bin/python3");
  const pythonCmd = fs.existsSync(venvPython) ? venvPython : "python3";

  console.log("🚀 启动常驻Python翻译服务...");

  // 使用 --daemon 参数启动常驻模式
  pythonDaemon = spawn(pythonCmd, [pythonScript, "--daemon"], {
    cwd: projectRoot,
  });

  // 监听stdout（翻译结果）
  pythonDaemon.stdout.on("data", (data) => {
    stdoutBuffer += data.toString();

    // 处理完整的JSON行
    let lines = stdoutBuffer.split("\n");
    stdoutBuffer = lines.pop() || ""; // 保留不完整的最后一行

    lines.forEach((line) => {
      line = line.trim();
      if (!line) return;

      try {
        const result = JSON.parse(line);
        const request = requestQueue.shift();
        if (request) {
          request.resolve(result);
        }
      } catch (e) {
        console.error("❌ 解析Python响应失败:", line);
      }
    });
  });

  // 监听stderr（日志输出）
  pythonDaemon.stderr.on("data", (data) => {
    const output = data.toString().trim();
    if (output) {
      console.log(`📋 Python输出: ${output}`);
    }
  });

  // 监听进程错误
  pythonDaemon.on("error", (error) => {
    console.error("❌ Python进程错误:", error);
    // 清空队列，拒绝所有等待的请求
    while (requestQueue.length > 0) {
      const request = requestQueue.shift();
      request.reject(new Error("Python进程错误"));
    }
  });

  // 监听进程退出
  pythonDaemon.on("close", (code) => {
    console.log(`⚠️ Python进程已退出，退出码: ${code}`);
    pythonDaemon = null;
    // 清空队列
    while (requestQueue.length > 0) {
      const request = requestQueue.shift();
      request.reject(new Error("Python进程已退出"));
    }
  });
}

/**
 * 停止常驻Python服务
 */
function stopPythonDaemon() {
  if (pythonDaemon) {
    console.log("🛑 停止Python服务...");
    pythonDaemon.kill();
    pythonDaemon = null;
    requestQueue = [];
    stdoutBuffer = "";
  }
}

/**
 * 向Python服务发送翻译请求
 * @param {string} screenshotPath - 截图路径
 * @param {Object} region - 区域信息
 * @returns {Promise<Object>} 翻译结果
 */
function sendTranslateRequest(screenshotPath, region) {
  return new Promise((resolve, reject) => {
    // 确保Python服务已启动
    if (!pythonDaemon) {
      startPythonDaemon();
      // 等待一小段时间让服务启动
      setTimeout(() => {
        sendTranslateRequestInternal(screenshotPath, region, resolve, reject);
      }, 100);
    } else {
      sendTranslateRequestInternal(screenshotPath, region, resolve, reject);
    }
  });
}

/**
 * 内部函数：发送请求到Python服务
 */
function sendTranslateRequestInternal(screenshotPath, region, resolve, reject) {
  try {
    // 构建请求JSON
    const request = {
      screenshot_path: screenshotPath,
      x: region.x,
      y: region.y,
      width: region.width,
      height: region.height,
    };

    // 加入请求队列
    requestQueue.push({ resolve, reject });

    // 发送到Python进程的stdin
    pythonDaemon.stdin.write(JSON.stringify(request) + "\n");
  } catch (error) {
    reject(error);
  }
}

// 模块加载时启动Python服务
startPythonDaemon();

/**
 * 截取指定区域的屏幕截图
 * @param {Object} region - 区域信息 {x, y, width, height}
 * @returns {Promise<string>} 截图文件路径
 */
async function captureRegion(region) {
  const { x, y, width, height } = region;

  try {
    // 找出区域所在的显示器
    const displays = screen.getAllDisplays();
    let targetDisplay = null;

    for (const display of displays) {
      const { x: dx, y: dy, width: dw, height: dh } = display.bounds;
      // 检查区域中心点是否在此显示器内
      const centerX = x + width / 2;
      const centerY = y + height / 2;

      if (
        centerX >= dx &&
        centerX < dx + dw &&
        centerY >= dy &&
        centerY < dy + dh
      ) {
        targetDisplay = display;
        break;
      }
    }

    if (!targetDisplay) {
      targetDisplay = screen.getPrimaryDisplay();
    }

    // 获取屏幕截图
    const sources = await desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: {
        width: targetDisplay.bounds.width,
        height: targetDisplay.bounds.height,
      },
    });

    if (sources.length === 0) {
      throw new Error("无法获取屏幕截图");
    }

    // 找到目标显示器对应的截图源
    let targetSource = sources[0];

    // desktopCapturer 返回的 sources 顺序可能和 displays 不同
    // 如果有多个屏幕，需要根据显示器ID匹配
    if (sources.length > 1) {
      // sources 的 name 通常包含 "Screen 1", "Screen 2" 等
      // 这里简化处理：主显示器用第一个，副显示器用第二个
      const isPrimaryDisplay =
        targetDisplay.id === screen.getPrimaryDisplay().id;
      targetSource = isPrimaryDisplay ? sources[0] : sources[1] || sources[0];
    }

    const screenshot = targetSource.thumbnail;
    const buffer = screenshot.toPNG();

    // 将全局坐标转换为显示器相对坐标
    const relativeX = x - targetDisplay.bounds.x;
    const relativeY = y - targetDisplay.bounds.y;

    // 裁剪指定区域
    const croppedBuffer = await sharp(buffer)
      .extract({ left: relativeX, top: relativeY, width, height })
      .toBuffer();

    // 保存到临时文件
    const tempPath = path.join(
      require("os").tmpdir(),
      `screenshot_${Date.now()}.png`
    );
    fs.writeFileSync(tempPath, croppedBuffer);

    return tempPath;
  } catch (error) {
    console.error("截图失败:", error);
    throw error;
  }
}

/**
 * 调用Python翻译服务（使用常驻进程）
 * @param {string} screenshotPath - 截图文件路径
 * @param {Object} region - 区域信息
 * @returns {Promise<Object>} 翻译结果 {success, textBlocks, error}
 */
async function callPythonTranslate(screenshotPath, region) {
  try {
    // 使用常驻服务进行翻译
    const result = await sendTranslateRequest(screenshotPath, region);

    // 删除临时截图文件
    try {
      fs.unlinkSync(screenshotPath);
    } catch (e) {
      // 忽略删除错误
    }

    return result;
  } catch (error) {
    // 删除临时截图文件
    try {
      fs.unlinkSync(screenshotPath);
    } catch (e) {
      // 忽略删除错误
    }
    throw error;
  }
}

module.exports = {
  captureRegion,
  callPythonTranslate,
  stopPythonDaemon,
};
