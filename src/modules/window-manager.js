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
  // 获取鼠标当前所在的显示器
  const cursorPoint = screen.getCursorScreenPoint();
  const currentDisplay = screen.getDisplayNearestPoint(cursorPoint);

  const { x, y, width, height } = currentDisplay.bounds;

  const selector = new BrowserWindow({
    x,
    y,
    width,
    height,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    hasShadow: false,
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
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // 使用 setIgnoreMouseEvents 的特殊选项来保持渲染质量
  overlay.setIgnoreMouseEvents(true, { forward: true });
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

  // 固定字体大小 - 保证显示一致性
  const fontSize = 16; // 固定16px，清晰易读
  const lineHeight = 22; // 固定行高

  // 固定窗口高度
  const windowHeight = 32; // 固定高度，适合单行文本

  // 根据文本长度估算宽度（中文每字符约16px + padding）
  const estimatedWidth = Math.ceil(translated.length * 16 + 24);
  // 设置最小和最大宽度
  const minWidth = 80;
  const maxWidth = 800;
  const windowWidth = Math.max(minWidth, Math.min(estimatedWidth, maxWidth));

  // 覆盖在原文位置上，水平居中对齐，垂直居中对齐
  // X: 翻译窗口相对原文中心对齐
  let windowX = absoluteX + Math.floor(width / 2) - Math.floor(windowWidth / 2);
  // Y: 翻译窗口相对原文中心对齐（避免偏下）
  let windowY =
    absoluteY + Math.floor(height / 2) - Math.floor(windowHeight / 2);

  // 找到文本块所在的显示器
  const displays = screen.getAllDisplays();
  let targetDisplay = screen.getPrimaryDisplay();

  for (const display of displays) {
    const { x: dx, y: dy, width: dw, height: dh } = display.bounds;
    if (
      absoluteX >= dx &&
      absoluteX < dx + dw &&
      absoluteY >= dy &&
      absoluteY < dy + dh
    ) {
      targetDisplay = display;
      break;
    }
  }

  const screenBounds = targetDisplay.bounds;

  // 确保不超出当前显示器范围
  windowX = Math.max(
    screenBounds.x + 10,
    Math.min(windowX, screenBounds.x + screenBounds.width - windowWidth - 10)
  );
  windowY = Math.max(screenBounds.y + 50, windowY);

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
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.setAlwaysOnTop(true, "floating");
  win.setVisibleOnAllWorkspaces(true);

  win.loadFile(path.join(__dirname, "../views/translation-window.html"));

  win.webContents.on("did-finish-load", () => {
    win.webContents.send("show-translation", {
      original,
      translated,
      fontSize,
      lineHeight,
    });
  });

  return win;
}

module.exports = {
  createRegionSelector,
  createRegionOverlay,
  createTranslationWindow,
};
