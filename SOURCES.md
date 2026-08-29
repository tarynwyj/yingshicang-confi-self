# 源清单（SOURCES）

> 检索时间：2026-08-29。社区源变动很快，**不保证长期有效**，建议配合 `scripts/check_sources.py` 定期自检。
> 标注 ✅ = 本次已抓取验证可访问；⚠️ = 社区广泛使用但未逐一验证；🚫 = 需自行判断合规。

## 1. IPTV / M3U 直播源

| 源 | 地址 | 状态 | 说明 |
|---|---|---|---|
| fanmingming/live IPv6 | `https://live.fanmingming.com/tv/m3u/ipv6.m3u` | ✅ | 央视/卫视/地方台，需 IPv6，附带台标+EPG |
| fanmingming/live IPv4 | `https://live.fanmingming.com/tv/m3u/ipv4.m3u` | ✅ | 同上，IPv4 |
| iptv-org 全量 | `https://iptv-org.github.io/iptv/index.m3u` | ✅ | 全球公开频道（GitHub: iptv-org/iptv） |
| iptv-org 中国大陆 | `https://iptv-org.github.io/iptv/countries/cn.m3u` | ✅ | 国内频道 |
| iptv-org 香港 | `https://iptv-org.github.io/iptv/countries/hk.m3u` | ✅ | 香港频道 |
| HerbertHe/iptv-sources | `https://github.com/HerbertHe/iptv-sources` | ⚠️ | 自动聚合脚本项目 |
| ssili126/tv | `https://github.com/ssili126/tv` | ⚠️ | 国内直播源合集 |

## 2. Jellyfin / Emby / Alist（自有资源）

| 项目 | 地址 | 说明 |
|---|---|---|
| alist-tvbox | <https://github.com/ygyzy/alist-tvbox> | Alist 转 TVBox 代理，`type:1, api:http://IP:5678/vod` |
| 小雅 xiaoya-tvbox | <https://github.com/haroldli/xiaoya-tvbox> | Alist+Emby 全家桶（Docker） |
| Emby/Jellyfin 本体 | 自建 | 影视仓 App 内置“我的→添加服务器”直接接入，无需改 JSON |

## 3. 多仓入口

| 入口 | 地址 | 说明 |
|---|---|---|
| 本仓库多仓 | `https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json` | 已收录肥猫/饭太硬/欧歌/高天流云/香雅情/南风等公共线路 |
| noimank/tvbox | <https://github.com/noimank/tvbox> | 影视仓多仓源分享（gitlab + gh-proxy 双地址） |
| fish2018/tvbox 私有化工具 | <https://github.com/fish2018/tvbox> | Docker 一键把多仓去重/去失效线路后私有化到自己的 GitHub |

社区多仓中常见的线路名（这些只是名称，实际地址都在各多仓 JSON 内）：肥猫、饭太硬、欧歌、游魂、高天流云、香雅情、南风、小盒子、王二小、FongMi。

## 4. Spider / JAR 扩展

| 项目 | 地址 | 说明 |
|---|---|---|
| TVBoxOS（官方） | <https://github.com/q215613905/TVBoxOS> | TVBox 本体源码 |
| CatVodTVSpider | <https://github.com/liuyunfeng001/CatVodTVSpider1> | 爬虫开发骨架 |
| FongMi/TV | <https://github.com/FongMi/TV> | FongMi 影视源码 |
| takagen99/Box | <https://github.com/takagen99/Box> | Box 源码 |

> 说明：具体某个 jar 是否可用、怎么配，以对应源提供方为准；多仓线路自带的 jar 会在私有化时一并下载。本仓库不内置任何第三方 jar。

## 5. 配置加密 / Base64

| 工具 | 地址 | 说明 |
|---|---|---|
| 本仓库 encrypt_config.py | `scripts/encrypt_config.py` | Base64 + AES-128-ECB 加密 |
| @whyun/tv-tools | <https://github.com/whyun-pages/tv-tools> | 解密/解码 TVBox 载荷的 TS 库，验证了“Base64 前缀 + hex 密文 + AES-128-ECB”机制 |

## 6. 自动检测失效线路

| 项目 | 地址 | 说明 |
|---|---|---|
| 本仓库 check_sources.py | `scripts/check_sources.py` | 检测 config/multi/live.m3u，可自动注释/剔除失效项 |
| Guovin/iptv-api | <https://github.com/Guovin/iptv-api> | 直播源自动采集+聚合+测速+过滤，出 M3U/TXT/API |
| fish2018/tvbox 私有化 | <https://github.com/fish2018/tvbox> | 多仓去重 + 移除失效线路 |

## 7. GitHub Actions 定时更新

| 项目 | 地址 | 说明 |
|---|---|---|
| 本仓库 workflow | `.github/workflows/update-config.yml` | 每天自检+同步上游直播源+自动提交 |
| Guovin/iptv-api 工作流 | 同上 repo 内 | fork 后开启 Actions 即可定时出直播源 |
| cai3804007/TV | <https://github.com/cai3804007/TV> | 同类自动更新配置示例 |
