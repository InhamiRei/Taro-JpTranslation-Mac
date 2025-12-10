/**
 * 主程序入口
 * 日语实时翻译工具 - Electron应用
 */

const { app, ipcMain } = require("electron");

// 导入模块
const {
  createRegionSelector,
  createRegionOverlay,
  createTranslationWindow,
} = require("./modules/window-manager");
const {
  captureRegion,
  callPythonTranslate,
  stopPythonDaemon,
} = require("./modules/translation-handler");
const {
  registerShortcuts,
  unregisterShortcuts,
} = require("./modules/shortcut-handler");

// ============================================================================
// 全局状态
// ============================================================================

/** @type {BrowserWindow|null} 区域选择器窗口 */
let regionSelector = null;

/** @type {BrowserWindow|null} 区域边框窗口 */
let regionOverlay = null;

/** @type {BrowserWindow[]} 翻译窗口列表 */
let translationWindows = [];

/** @type {Object|null} 监听区域 {x, y, width, height} */
let monitoredRegion = null;

/** @type {boolean} 翻译窗口是否可见 */
let translationsVisible = true;

// ============================================================================
// 窗口管理函数
// ============================================================================

/**
 * 关闭所有翻译窗口
 */
function closeAllTranslationWindows() {
  translationWindows.forEach((win) => {
    if (win && !win.isDestroyed()) {
      win.close();
    }
  });
  translationWindows = [];
}

/**
 * 创建多个翻译窗口
 * @param {Object} region - 区域信息
 * @param {Array} textBlocks - 文本块数组
 */
function createTranslationWindows(region, textBlocks) {
  closeAllTranslationWindows();

  textBlocks.forEach((block) => {
    const win = createTranslationWindow(block, region.x, region.y);
    translationWindows.push(win);
  });

  // 翻译窗口持久保留，不自动关闭
  // 用户可以按 Cmd+R 切换显示/隐藏
}

// ============================================================================
// IPC 事件处理
// ============================================================================

// 启动区域选择
ipcMain.on("start-region-selection", () => {
  if (regionSelector) regionSelector.close();
  regionSelector = createRegionSelector();
});

// 区域选择完成
ipcMain.on("region-selected", (event, region) => {
  monitoredRegion = region;

  // 关闭选择窗口
  if (regionSelector) {
    regionSelector.close();
    regionSelector = null;
  }

  // 显示监听边框
  if (regionOverlay) regionOverlay.close();
  regionOverlay = createRegionOverlay(
    region.x,
    region.y,
    region.width,
    region.height
  );
});

// 取消区域选择
ipcMain.on("cancel-selection", () => {
  if (regionSelector) {
    regionSelector.close();
    regionSelector = null;
  }
});

// ============================================================================
// 快捷键回调函数
// ============================================================================

/**
 * 选择区域
 */
function handleSelectRegion() {
  if (regionSelector) regionSelector.close();
  regionSelector = createRegionSelector();
}

/**
 * 翻译监听区域
 */
async function handleTranslate() {
  if (!monitoredRegion) return;

  try {
    // 先关闭所有旧翻译窗口，避免OCR识别到旧翻译
    closeAllTranslationWindows();

    // 等待一小段时间让窗口完全关闭
    await new Promise((resolve) => setTimeout(resolve, 50));

    const screenshotPath = await captureRegion(monitoredRegion);
    const result = await callPythonTranslate(screenshotPath, monitoredRegion);

    if (result.success && result.textBlocks) {
      createTranslationWindows(monitoredRegion, result.textBlocks);
    }
  } catch (error) {
    console.error("翻译错误:", error);
  }
}

/**
 * 切换翻译显示/隐藏
 */
function handleToggleVisibility() {
  translationsVisible = !translationsVisible;

  // 切换所有翻译窗口的显示状态
  translationWindows.forEach((win) => {
    if (win && !win.isDestroyed()) {
      if (translationsVisible) {
        win.show();
      } else {
        win.hide();
      }
    }
  });
}

// ============================================================================
// 应用生命周期
// ============================================================================

// 应用就绪
app.whenReady().then(() => {
  console.log("🚀 应用启动成功\n");

  // 注册全局快捷键
  registerShortcuts({
    onSelectRegion: handleSelectRegion,
    onTranslate: handleTranslate,
    onToggleVisibility: handleToggleVisibility,
  });
});

// 所有窗口关闭
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// 程序退出前清理
app.on("will-quit", () => {
  unregisterShortcuts();
  closeAllTranslationWindows();
  if (regionOverlay) regionOverlay.close();
  stopPythonDaemon(); // 停止常驻Python服务
});
