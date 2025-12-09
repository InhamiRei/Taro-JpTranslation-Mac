/**
 * 快捷键处理模块
 * 注册和管理全局快捷键
 */

const { globalShortcut, app } = require("electron");

/**
 * 注册所有全局快捷键
 * @param {Object} callbacks - 回调函数集合
 * @param {Function} callbacks.onSelectRegion - 选择区域回调
 * @param {Function} callbacks.onTranslate - 翻译回调
 * @param {Function} callbacks.onToggleVisibility - 切换显示回调
 */
function registerShortcuts(callbacks) {
  const { onSelectRegion, onTranslate, onToggleVisibility } = callbacks;

  // Cmd+Shift+C - 选择区域
  globalShortcut.register("CommandOrControl+Shift+C", () => {
    console.log("⌨️  触发快捷键: Cmd+Shift+C (选择区域)");
    onSelectRegion();
  });

  // Cmd+T - 翻译监听区域
  globalShortcut.register("CommandOrControl+T", () => {
    console.log("⌨️  触发快捷键: Cmd+T (翻译)");
    onTranslate();
  });

  // Cmd+R - 切换翻译显示/隐藏
  globalShortcut.register("CommandOrControl+R", () => {
    console.log("⌨️  触发快捷键: Cmd+R (切换显示)");
    onToggleVisibility();
  });

  // Cmd+Shift+Q - 退出程序
  globalShortcut.register("CommandOrControl+Shift+Q", () => {
    console.log("⌨️  触发快捷键: Cmd+Shift+Q (退出程序)");
    app.quit();
  });

  console.log("✅ 全局快捷键注册成功");
  console.log("快捷键:");
  console.log("  Cmd+Shift+C: 选择监听区域");
  console.log("  Cmd+T: 翻译监听区域");
  console.log("  Cmd+R: 切换翻译显示/隐藏");
  console.log("  Cmd+Shift+Q: 退出程序");
}

/**
 * 注销所有全局快捷键
 */
function unregisterShortcuts() {
  globalShortcut.unregisterAll();
  console.log("✅ 全局快捷键已注销");
}

module.exports = {
  registerShortcuts,
  unregisterShortcuts,
};
