# RinUI 本地修改记录

本项目使用 vendored 的 RinUI 框架。以下记录了对 RinUI 源码的本地修改，
便于后续升级 RinUI 时对照合并。

---

## 1. ContextMenu 下拉弹出位置与动画

**文件**: `RinUI/components/ContextMenu.qml`

**问题**: ComboBox 下拉菜单弹出时，先原地展开再丝滑滑动到垂直居中位置，
体验不符合标准下拉行为。

**原因**:
- `y: (parent.height - contextMenu.height) / 2` 使弹出菜单垂直居中于父组件
- `enter` Transition 中 height 从 46 动画到 implicitHeight，触发 y 绑定持续重算
- `Behavior on y` 的 NumberAnimation 使 y 变化产生滑动效果

**修改**:
- 第 21 行: `y: (parent.height - contextMenu.height) / 2` → `y: parent.height`
  （弹出菜单紧贴父组件下方，标准下拉行为）
- 第 131 行: 移除 `Behavior on y { NumberAnimation { ... } }`
  （不再对 y 变化做平滑动画）

---

## 2. NavigationBar 返回按钮水平对齐

**文件**: `RinUI/components/Navigation/NavigationBar.qml`

**问题**: FluentWindow 标题栏的 Back 按钮与 NavigationBar 的折叠按钮及导航项
在水平方向不对齐（Back 按钮偏左约 5px）。

**原因**:
- Back 按钮所在的 `title` Row 被 re-parent 到 `titleBarHost`（TitleBar 坐标系，x≈0）
- NavigationBar 主体位于 `contentArea` 内，该区域有 `anchors.leftMargin: Utils.windowDragArea`（5px）
- 两者坐标系差了 `windowDragArea` 的偏移量

**修改**:
- 第 222 行: `anchors.leftMargin: navigationBar.macTitleSafeInset`
  → `anchors.leftMargin: navigationBar.isMacOS ? navigationBar.macTitleSafeInset : Utils.windowDragArea`
  （非 macOS 平台上为 Back 按钮补偿 windowDragArea 偏移，与下方导航项对齐）

---

## 3. NavigationView 登录状态属性传递

**文件**: `RinUI/components/Navigation/NavigationView.qml`

**问题**: 需要在 Main.qml 中管理的登录状态传递给所有页面，实现统一的登录状态管理。

**原因**:
- Main.qml 中有 `property bool loggedin: false` 需要传递给所有页面
- NavigationView 负责创建和管理所有页面，需要作为中间层传递属性
- 页面需要根据登录状态显示不同的内容

**修改**:
- 第 24 行: 添加 `property bool loggedin: false`
  （登录状态属性，从 Main.qml 传入）
- 第 403 行: 在页面创建时传递 loggedin 属性
  ```qml
  let pageInstance = component.createObject(stackView, Object.assign({}, properties, {
      objectName: targetObjectName,
      loggedin: navigationView.loggedin  // 传递登录状态到页面
  }))
  ```

**注意**: 此修改支持登录状态从 Main.qml → NavigationView → 各个页面的完整传递链路。
