# 资源文件说明

本目录用于存放系统中使用的静态资源文件，包括背景图、Logo、图标等。

## 目录结构

```
assets/
├── bakgrounImage/          # 背景图目录
│   ├── bj_hc.png          # 登录页和锁屏背景图（主要）
│   └── bakgrounImage.jpg  # 备用背景图
├── error/                  # 错误页面图片
│   ├── 401.svg
│   └── 404.svg
├── fonts/                  # 字体文件
│   └── HarmonyOS_Sans_SC_Medium.ttf
├── logo.svg               # 主Logo
├── whiteLogo.svg          # 白色Logo（深色背景使用）
├── logo-mini.png          # 迷你Logo（折叠菜单使用）
├── login-main.svg         # 登录页装饰图
├── login-bg.svg           # 登录页背景SVG
└── weixin.png             # 微信二维码
```

## 如何替换背景图

### 方法一：直接替换文件（推荐）

1. 准备你的背景图片（推荐尺寸：1920x1080 或更高）
2. 将图片重命名为 `bj_hc.png`
3. 替换 `frontend/src/assets/bakgrounImage/bj_hc.png` 文件
4. 刷新浏览器即可看到新背景

### 方法二：修改配置文件

1. 将你的背景图片放到 `frontend/src/assets/bakgrounImage/` 目录
2. 打开 `frontend/src/config/assets.ts` 文件
3. 修改 `backgroundImages` 配置：

```typescript
export const backgroundImages = {
  // 登录页背景图
  loginBg: new URL('../assets/bakgrounImage/你的图片名.png', import.meta.url).href,
  // 锁屏背景图
  lockScreenBg: new URL('../assets/bakgrounImage/你的图片名.png', import.meta.url).href,
};
```

## 如何替换Logo

### 替换主Logo

1. 准备你的Logo文件（支持 SVG、PNG 格式）
2. 将文件重命名为 `logo.svg` 或 `logo.png`
3. 替换 `frontend/src/assets/logo.svg` 文件

### 替换迷你Logo

1. 准备你的迷你Logo（推荐尺寸：64x64 或 128x128）
2. 将文件重命名为 `logo-mini.png`
3. 替换 `frontend/src/assets/logo-mini.png` 文件

### 通过配置文件修改

打开 `frontend/src/config/assets.ts`，修改 `logos` 配置：

```typescript
export const logos = {
  main: new URL('../assets/你的logo.svg', import.meta.url).href,
  white: new URL('../assets/你的白色logo.svg', import.meta.url).href,
  mini: new URL('../assets/你的迷你logo.png', import.meta.url).href,
};
```

## 图片格式建议

- **背景图**：PNG、JPG（推荐 1920x1080 或更高分辨率）
- **Logo**：SVG（矢量图，可无限缩放）或 PNG（透明背景）
- **图标**：SVG 或 PNG

## 注意事项

1. 替换文件后，如果浏览器没有更新，请清除缓存或强制刷新（Ctrl+F5）
2. 图片文件不要太大，建议压缩后使用（背景图建议 < 500KB）
3. Logo 建议使用透明背景的 PNG 或 SVG 格式
4. 所有资源文件的引用都在 `frontend/src/config/assets.ts` 中统一管理

## 统一配置文件

所有资源路径都在 `frontend/src/config/assets.ts` 中统一管理，这样做的好处：

- ✅ 集中管理，易于维护
- ✅ 修改一处，全局生效
- ✅ 支持动态切换主题
- ✅ 便于版本控制和团队协作

## 使用示例

在组件中使用资源：

```vue
<script setup>
import { backgroundImages, logos } from '/@/config/assets';

// 使用背景图
const bgStyle = {
  backgroundImage: `url(${backgroundImages.loginBg})`
};

// 使用Logo
const logoUrl = logos.main;
</script>

<template>
  <div :style="bgStyle">
    <img :src="logoUrl" alt="Logo" />
  </div>
</template>
```
