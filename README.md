# 影视仓 / TVBox 配置订阅

个人维护的影视仓（TVBox 系）配置订阅合集：**点播多仓**、**完整多仓**与**直播配置**，适用于部分兼容的影视仓 / TVBox 客户端。

配置内容来自第三方项目，本仓库只做结构校验与自动更新；**实际可用性取决于来源与客户端**。

> 本仓库不是影视仓 / TVBox 客户端，也不提供片源或授权。请只使用你有权访问的资源；公开可访问不代表获得授权。配置经过结构与连接检查，**不保证所有来源都能正常播放**。

## 快速开始

### 1. 选择订阅地址

**点播多仓** · 8 个来源 · 适合主要看电影、电视剧的用户（推荐先试）

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

**完整多仓** · 19 个入口 · 保留全部历史仓库，适合自己切换仓库的用户

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

**直播配置** · 6 个直播列表 · 只含直播，不含电影电视剧点播站点

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

其他入口：

| 用途 | 地址 |
|---|---|
| 连接测试（Apple HLS 测试视频，不是电视频道） | `https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config-test.json` |
| 聚合直播 M3U（用于直播地址输入） | `https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/upstream/all.m3u` |

GitHub 原始地址访问不稳定时，可换用同一文件的 CDN 或代理地址：

```text
https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/multi-vod.json
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

CDN 和客户端都可能缓存旧内容；没有承诺即时刷新，也不要把固定提交地址当作日常更新入口。

> **多仓不等于单仓。** `multi-vod.json` 与 `multi.json` 是 `urls` 多仓结构；粘到普通单仓配置框里通常无法加载。需要在客户端中找到「多仓 / 仓库管理」入口导入，再选择具体仓库。`config.json` 才是单仓直播配置。

### 2. 在客户端导入

1. 打开兼容客户端，进入「配置 / 多仓 / 仓库管理」入口（不同客户端菜单名不同）。
2. 粘贴上表地址（**不是** GitHub 网页地址），保存并加载。
3. 加载成功后选择具体仓库或直播源。能加载配置不代表所有频道都能播放。

### 3. 常见问题

| 现象 | 处理 |
|---|---|
| 配置拉取失败 | 确认地址类型与入口匹配；检查该设备的网络、DNS、系统时间和应用版本；换 CDN / 代理地址再试 |
| 能拉配置但没有电影电视剧 | 确认加载的是哪种配置：`config.json` 没有点播；多仓需要在多仓入口里再选择具体仓库 |
| 频道显示但播放失败 | 可能是 IPv6、运营商或地区限制、签名过期、来源失效；换线路或换来源，不要清空仓库 |
| 内容没有更新 | 客户端或 CDN 缓存；在应用内刷新配置，清理缓存前先记录自己的设置 |

## 说明与边界

- **来源与检测记录**：[SOURCES.md](SOURCES.md) —— 来源清单、维护者与当前外部警告。
- **自动更新与维护**：[MAINTENANCE.md](MAINTENANCE.md) —— 更新流程、检查逻辑与回退。
- **公开仓库安全**：[SECURITY.md](SECURITY.md) —— 凭据、签名播放地址与提交邮箱。
- 自动更新成功、配置结构检查通过，都不等于频道可播放；播放验证只能在设备上完成。
- 不托管或执行第三方 JAR / 扩展；第三方来源的可用性不在本项目保证范围内。
- 历史入口与频道不会因为一次检测失败而被删除；订阅地址保持稳定。
