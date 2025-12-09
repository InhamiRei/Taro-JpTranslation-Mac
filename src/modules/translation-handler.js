/**
 * 翻译处理模块
 * 负责截图、OCR识别和翻译的核心逻辑
 */

const { desktopCapturer, screen } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const sharp = require("sharp");

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
 * 调用Python翻译服务
 * @param {string} screenshotPath - 截图文件路径
 * @param {Object} region - 区域信息
 * @returns {Promise<Object>} 翻译结果 {success, textBlocks, error}
 */
async function callPythonTranslate(screenshotPath, region) {
  return new Promise((resolve, reject) => {
    // Python脚本路径
    const pythonScript = path.join(
      __dirname,
      "../../translator/translate_service_server.py"
    );

    // 使用虚拟环境的Python
    const projectRoot = path.join(__dirname, "../..");
    const venvPython = path.join(projectRoot, "venv/bin/python3");
    const pythonCmd = fs.existsSync(venvPython) ? venvPython : "python3";

    // 启动Python进程
    const python = spawn(pythonCmd, [
      pythonScript,
      screenshotPath,
      region.x.toString(),
      region.y.toString(),
      region.width.toString(),
      region.height.toString(),
    ]);

    let stdout = "";
    let stderr = "";

    python.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    python.stderr.on("data", (data) => {
      const output = data.toString().trim();
      // 只在包含错误关键词时才标记为错误
      if (
        output.includes("Error") ||
        output.includes("错误") ||
        output.includes("失败")
      ) {
        console.error(`❌ Python错误: ${output}`);
      } else {
        console.log(`📋 Python输出: ${output}`);
      }
      stderr += data.toString();
    });

    python.on("close", (code) => {
      // 删除临时截图文件
      try {
        fs.unlinkSync(screenshotPath);
      } catch (e) {
        // 忽略删除错误
      }

      if (code !== 0) {
        reject(new Error(`Python进程退出码: ${code}\n${stderr}`));
        return;
      }

      // 解析JSON结果
      try {
        const result = JSON.parse(stdout);
        resolve(result);
      } catch (e) {
        reject(new Error(`解析JSON失败: ${e.message}\n${stdout}`));
      }
    });
  });
}

module.exports = {
  captureRegion,
  callPythonTranslate,
};
