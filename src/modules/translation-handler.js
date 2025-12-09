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
    // 获取屏幕截图
    const sources = await desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: {
        width: screen.getPrimaryDisplay().bounds.width,
        height: screen.getPrimaryDisplay().bounds.height,
      },
    });

    if (sources.length === 0) {
      throw new Error("无法获取屏幕截图");
    }

    // 使用第一个屏幕的截图
    const screenshot = sources[0].thumbnail;
    const buffer = screenshot.toPNG();

    // 裁剪指定区域
    const croppedBuffer = await sharp(buffer)
      .extract({ left: x, top: y, width, height })
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

    console.log("🐍 调用Python服务:", pythonCmd);
    console.log("📜 脚本路径:", pythonScript);

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
