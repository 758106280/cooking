# 移动端应用接入说明

当前移动端采用 Capacitor，将现有 Vue3 前端复用为 Android 和 iOS 应用。Web 端仍使用原来的 Vite 开发和部署方式。

## 本地准备

```bash
cd frontend
npm install
npm run build
```

首次生成原生工程：

```bash
cd frontend
npx cap add android
npx cap add ios
```

之后同步前端代码：

```bash
npm run mobile:sync
```

打开原生工程：

```bash
npm run mobile:android
npm run mobile:ios
```

Android 需要 Android Studio 和 SDK；iOS 需要 macOS、Xcode 和 Apple Developer 签名配置。

## 移动端 API 地址

Web 开发时 `VITE_API_BASE_URL` 留空，接口由 Vite proxy 转发到 `http://localhost:8000`。

移动端构建时可以不指定 API 地址，安装后首次打开会让用户填写。也可以指定一个默认地址：

```bash
VITE_API_BASE_URL=https://api.example.com npm run mobile:sync
```

不填写时，首次打开会显示“配置服务地址”页面，支持例如 `http://192.168.1.100:8000` 的家庭局域网地址。地址保存在设备本地，后续可通过顶部“服务地址”按钮修改。

不要在移动端填写 `localhost`；它指向手机本机，而不是开发电脑或服务器。

家用局域网 HTTP 已打开 Android 明文流量和 iOS 本地网络访问。公网部署仍建议使用 HTTPS。

## 后端配置

移动端 WebView 的 Origin 默认包含 `https://localhost`，开发环境已加入允许列表。生产环境应通过环境变量配置真实来源，并使用 HTTPS：

```env
CORS_ORIGINS=https://localhost,https://app.example.com
SESSION_SAME_SITE=none
SESSION_HTTPS_ONLY=true
```

移动端登录会同时获得设备 Token，并使用 Capacitor Preferences 保存；后续移动端请求自动携带 Bearer Token，避免家庭局域网 HTTP 场景下跨域 Session Cookie 失效。Web 端仍兼容原来的 Session Cookie 登录协议。当前 Token 有效期为 30 天，后续如需多设备管理可再升级为 Refresh Token 和服务端撤销机制。

## 第一版移动端范围

- 首页、菜谱库、搜索和筛选
- 早餐、午餐、晚餐筛选
- 菜谱详情、收藏、偏好和账户
- 烹饪模式及计时
- 移动端底部导航、安全区域和 Android 返回键基础适配
- Web 端管理页面继续保留，不放入移动端底部导航

## 发布前检查

- Android 真机安装和返回键
- iPhone 真机安全区域和键盘
- 无网络、恢复网络和接口超时
- 登录、收藏、偏好保存
- 图片地址使用 HTTPS
- Android 签名 Keystore 和 AAB
- iOS Bundle ID、证书、TestFlight 和隐私说明
