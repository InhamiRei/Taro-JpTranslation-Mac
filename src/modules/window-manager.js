/**
 * 窗口管理模块
 * 负责创建和管理所有Electron窗口
 */

const { BrowserWindow, screen } = require("electron");
const path = require("path");

/**
 * 创建区域选择窗口
 * @returns {BrowserWindow} 区域选择窗口实例
 */
function createRegionSelector() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  const selector = new BrowserWindow({
    width,
    height,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  selector.loadFile(path.join(__dirname, "../views/region-selector.html"));
  return selector;
}

/**
 * 创建区域监听边框窗口
 * @param {number} x - X坐标
 * @param {number} y - Y坐标
 * @param {number} width - 宽度
 * @param {number} height - 高度
 * @returns {BrowserWindow} 边框窗口实例
 */
function createRegionOverlay(x, y, width, height) {
  const overlay = new BrowserWindow({
    x: x - 6,
    y: y - 6,
    width: width + 12,
    height: height + 12,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    focusable: false,
    ignoreMouseEvents: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  overlay.setAlwaysOnTop(true, "screen-saver");
  overlay.setVisibleOnAllWorkspaces(true);
  overlay.loadFile(path.join(__dirname, "../views/region-overlay.html"));

  overlay.webContents.on("did-finish-load", () => {
    overlay.webContents.send("init-region", { x, y, width, height });
  });

  return overlay;
}

/**
 * 创建单个翻译窗口
 * @param {Object} textBlock - 文本块信息
 * @param {number} regionX - 区域X坐标
 * @param {number} regionY - 区域Y坐标
 * @returns {BrowserWindow} 翻译窗口实例
 */
function createTranslationWindow(textBlock, regionX, regionY) {
  const { x, y, width, height, original, translated } = textBlock;

  // 计算在屏幕上的绝对位置
  const absoluteX = regionX + x;
  const absoluteY = regionY + y;

  // 根据原文高度计算字体大小（比例约为 height * 0.7）
  const fontSize = Math.max(Math.round(height * 0.7), 12); // 最小12px
  const padding = Math.max(Math.round(height * 0.15), 4); // 内边距

  // 窗口尺寸精确匹配原文
  const windowWidth = width + padding * 2;
  const windowHeight = height + padding;

  // 精准覆盖在原文位置上
  let windowX = absoluteX;
  let windowY = absoluteY;

  // 确保不超出屏幕
  const screenBounds = screen.getPrimaryDisplay().bounds;
  windowX = Math.max(
    10,
    Math.min(windowX, screenBounds.width - windowWidth - 10)
  );
  windowY = Math.max(50, windowY);

  console.log(
    `  📍 文本块 "${original}" (${absoluteX}, ${absoluteY}, ${width}x${height})`
  );
  console.log(
    `     → 翻译窗口 "${translated}" 位置: (${windowX}, ${windowY}, ${windowWidth}x${windowHeight})`
  );

  const win = new BrowserWindow({
    x: windowX,
    y: windowY,
    width: windowWidth,
    height: windowHeight,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    focusable: true, // 允许聚焦，才能拖动
    movable: true, // 允许移动
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.setAlwaysOnTop(true, "pop-up-menu");
  win.setVisibleOnAllWorkspaces(true);
  win.setIgnoreMouseEvents(false);

  win.loadFile(path.join(__dirname, "../views/translation-window.html"));

  win.webContents.on("did-finish-load", () => {
    win.webContents.send("show-translation", {
      original,
      translated,
      fontSize, // 传递计算的字体大小
    });
  });

  return win;
}

module.exports = {
  createRegionSelector,
  createRegionOverlay,
  createTranslationWindow,
};
