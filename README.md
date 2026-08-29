# yingshicang-confi-self

自用影视仓配置仓库：直播源 + 自有资源(Emby/Jellyfin/Alist) + 多仓聚合 + 失效自检 + 定时更新。

## 快速使用

在影视仓中导入主配置地址：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

在影视仓 **设置 → 多仓/仓库管理** 中导入多仓地址（一键接入社区常用线路）：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

> 导入多仓后，App 会加载 `multi.json` 里列出的第三方线路（肥猫、饭太硬、欧歌、高天流云等）。这些是社区公共源，**不稳定、可能含未授权内容，请自行判断使用**。推荐优先用 `scripts/` 里的工具私有化后再用。

## 文件结构

| 文件 | 说明 |
|---|---|
| `config.json` | 主配置：自有站点 + 直播源列表 |
| `multi.json` | 多仓聚合入口（第三方线路） |
| `live.m3u` | 自选直播频道（本地维护，自动失效检测） |
| `scripts/check_sources.py` | 失效线路自动检测/剔除 |
| `scripts/encrypt_config.py` | 配置 Base64 / AES-128-ECB 加密 |
| `.github/workflows/update-config.yml` | 每天定时自检 + 同步上游直播源 |
| `upstream/` | 自动同步的上游直播列表副本 |

## 直播源（IPTV / M3U）

`config.json` 的 `lives` 已内置以下远程列表（均自动维护，无需手动更新）：

- 央视/卫视 IPv6：`https://live.fanmingming.com/tv/m3u/ipv6.m3u`
- 央视/卫视 IPv4：`https://live.fanmingming.com/tv/m3u/ipv4.m3u`
- 国际频道全量：`https://iptv-org.github.io/iptv/index.m3u`
- 中国大陆频道：`https://iptv-org.github.io/iptv/countries/cn.m3u`
- 香港频道：`https://iptv-org.github.io/iptv/countries/hk.m3u`

自选频道放在 `live.m3u`。注意：

- fanmingming 的央视/卫视多为 **IPv6 源**，需要宽带支持 IPv6（`ipw.cn` 可测）。
- `live.m3u` 内的频道会被 Actions 每天检测，失效的自动加 `#[DEAD]` 注释。

## 自有资源（Jellyfin / Emby / Alist）

**Emby / Jellyfin**：影视仓 App 内置媒体库功能，直接在 App 里 **我的 → 添加服务器** 填 Emby/Jellyfin 地址和账号即可，不需要改配置。`config.json` 里也留了两个占位站点，改成你自己的 IP 端口即可用（若你的 Emby 能提供 TVBox 兼容接口）。

**Alist**：用 [alist-tvbox](https://github.com/ygyzy/alist-tvbox) 在你服务器上起一个代理，然后在 `config.json` 的 sites 里加：

```json
{"key":"alist","name":"Alist","type":1,"api":"http://你的服务器IP:5678/vod","searchable":1,"quickSearch":1,"filterable":1}
```

## 多仓入口

影视仓的“多仓”就是导入一个返回 `{"urls":[{"url":...,"name":...}]}` 的 JSON。仓库内的 `multi.json` 已收录常用公共线路。

如果觉得公共线路太杂/失效太多，推荐用 [fish2018/tvbox](https://github.com/fish2018/tvbox) 的私有化工具（Docker），把多仓去重、去掉失效线路后推到自己的仓库，一劳永逸：

```bash
docker run --rm -e username=你的GitHub名 -e token=你的token \
  -e url='https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json' \
  2011820123/tvbox
```

## Spider / JAR 扩展

影视仓通过站点配置里的 `jar` / `ext` 字段加载爬虫 JAR。常用框架：

- 官方 TVBox：<https://github.com/q215613905/TVBoxOS>
- 爬虫开发骨架：<https://github.com/liuyunfeng001/CatVodTVSpider1>
- FongMi：<https://github.com/FongMi/TV>

具体某个源要不要配 `jar`，看该源提供方的说明。多仓线路自带 jar 的，私有化工具会一并把 jar 下载到你的仓库。本仓库不内置任何第三方 jar。

## 配置加密 / Base64

```bash
# Base64 编码
python3 scripts/encrypt_config.py config.json --mode base64

# AES-128-ECB 加密（App 导入时输入密钥）
python3 scripts/encrypt_config.py config.json --mode aes --key 你的密钥
```

加密后把生成的文件传到本仓库，App 导入 `config.enc` 的地址并输入密钥即可。密钥自己保管好。

## 自动检测失效线路 + 定时更新

- 本地手动检测：`python3 scripts/check_sources.py`（加 `--fix` 自动注释/剔除失效项）
- 云端定时：仓库已带 `.github/workflows/update-config.yml`，每天 11:20（北京时间）自动：
  1. 检测并剔除 `config.json` / `multi.json` / `live.m3u` 中的失效线路；
  2. 同步最新上游直播源到 `upstream/`；
  3. 有变动自动 commit + push。

需要到仓库 Settings → Actions → General 确认 **Workflow permissions** 为 “Read and write permissions”。

## 免责声明

本仓库内容仅供个人技术学习与自用。`multi.json` 中列出的第三方线路来自网络公开分享，稳定性与合规性由第三方维护，与本仓库无关；请勿用于传播、分发未授权内容。正式观看请优先使用已授权/自有的片源与直播源。
