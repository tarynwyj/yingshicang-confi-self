# 影视仓配置与来源维护

本仓库区分 **多仓入口、直播配置、连接测试**。列表存在、内容能下载与实际能播放是三件不同的事。只使用你有权访问的资源；公开可访问不代表获得授权。

## 你要用哪个地址

**优先测试点播，请导入本次筛选的点播多仓（8 个来源）：**

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

代理备用地址（本轮已读取到新清单）：

```text
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

2026-10-01 加入 Qist 自用点播、饭太硬（Qist维护）、潇洒（Qist维护）、高天流云 PG、高天流云 FTY、Gaoops点播。测试范围为配置下载、点播站点结构、扩展地址及文件头；实际搜索和播放待设备验证。证据见 [2026-10-01 来源检查](source-checks/2026-10-01-vod.json)。

2026-10-09 新增 Ray（dxawi）和王二小（维护镜像），分别读取到 48、63 个站点条目；配置与主扩展通过检查，Ray 的相对路径脚本已确认存在。站点条目数不等于实测播放数量。详情见 [2026-10-09 来源检查](source-checks/2026-10-09-vod.json)。

**要保留所有历史仓库并同时使用新增来源，请导入完整多仓（19 个入口）：**

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

同一份完整多仓的代理备用地址：

```text
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

找到你的影视仓版本中支持“多仓/仓库管理”的入口导入，再选择具体仓库。不同版本菜单不同，不能保证普通配置输入框支持多仓。进入“我的直播配置（无点播）”只会得到直播列表，不会自动出现电影电视剧站点。其他历史条目均保留，不因检测失败删除。

| 用途 | 原始地址 |
|---|---|
| 直播配置（没有点播站点） | https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json |
| 单独连接测试配置 | https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config-test.json |
| 聚合直播 M3U（用于直播地址输入） | https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/upstream/all.m3u |

其他文件也可用同路径的 CDN 地址：把前缀替换为 `https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/`。
配置内的自有列表链接沿用 CDN 主分支地址，避免原始域名在部分网络不可达；CDN 和客户端都可能缓存旧内容。没有承诺即时刷新，也不要把固定提交地址当作日常更新入口。

## “配置拉取失败”排查顺序

1. 确认导入的是对应类型的完整网址，而不是 GitHub 网页地址。
2. 用测试配置加载 Apple HLS 测试视频（它是测试视频，不是电视频道）。
3. 测试配置也拉取失败：在同一台设备打开同一网址，检查网络、DNS、系统时间和应用版本；电脑可访问不代表电视可访问。
4. 能拉配置但没有点播：检查是否选中了“我的直播配置（无点播）”，以及是否实际导入了多仓。
5. 能看到频道但播放失败：检查该频道及播放依赖；IPv6、运营商、地区限制、签名过期都会影响结果。不要因此清空仓库。
6. 缓存导致显示旧内容时，在应用内刷新配置；只清理相关配置缓存前先记录自己的设置。

## 自动维护：更新与检测分开

每天 UTC 03:20（北京时间 11:20）及相关文件推送后运行 GitHub Actions；计划任务可能延迟。可在 Actions 中手动运行 `update-and-check`。

- 先运行回归测试、校验主配置、测试配置、多仓和所有本地 M3U。
- 按 `scripts/upstreams.json` 的原有四个上游同步。下载先验证，空列表、错误网页、超时不会覆盖旧文件。
- 新旧列表合并：优先采用新条目，但保留上游消失的历史 URL 和播放参数。不会自动清除失效、过期或地域限制条目；重复 URL 加相同播放参数才去重，因此列表可能逐渐增长。
- 重建域名精选、完整聚合列表。精选只是域名筛选，**不是“官方授权/电信必能播放”的保证**。
- 自动提交仅限六个 `upstream/*.m3u` 输出，不会改写 `multi.json`、`config.json` 或 `live.m3u`。Git 历史保留之前版本；不强推。
- 联网检测默认执行，覆盖完整多仓、点播多仓和配置入口。手动运行时可勾选 check_streams 检查全部频道清单。HTTP 200 的 HTML 被判无效；支持 JSON 注释和尾逗号，其他特殊编码仍标为待验证。不会执行下载的 JAR、脚本，也不会抓取所有视频分片。
- 外部源超时、域名失效、特殊格式和上游下载失败仅生成警告，保留旧数据，正常完成维护；不会因同一批旧源每天触发任务失败邮件。程序崩溃、配置损坏、测试失败、报告损坏、文件写入失败或发布失败仍会使任务失败。报告在该次 Actions 的 `source-reports-运行编号` 附件中保留 30 天。绿色仅表示维护流程正常，不表示每个来源能播放。

报告状态：`content_ok` 仅表示内容结构符合检查范围；`unverified_format` 为非标准格式待人工验证；`invalid` 为内容错误；`unreachable` 为本次网络不可达。同步报告中的 `kept_previous` 表示保护生效，旧文件未被覆盖。

## 本地检查

需要 Python 3.12；维护脚本和测试仅使用标准库。

```text
python -m unittest discover -s tests -v
python scripts/check_sources.py
python scripts/sync_sources.py
python scripts/build_tel.py
python scripts/build_all.py
python scripts/check_sources.py --network
python scripts/check_sources.py --network --streams
```

`--streams` 检查所有去重后的频道清单，可能花数分钟；不验证解码、授权或所有分片。检测报告写入忽略版本控制的 `reports/`，不会包含完整带令牌 URL。

## 自有频道、媒体库及扩展

`live.m3u` 是手工维护文件，目前只有 Apple 测试视频。添加有权使用的真实频道时，保留 M3U 头部，再添加：

```m3u
#EXTINF:-1 group-title="自有频道",频道名称
https://example.com/authorized-stream.m3u8
```

示例地址不能播放，请替换为实际地址。不要将私有播放凭据上传到公开仓库。自有局域网服务不会通过公网检测，需在设备所在网络单独测试。

Jellyfin / Emby / Alist 尚未接入：需要真实地址、应用版本和受支持的接口/插件。不会恢复指向电视自身的 `127.0.0.1` 占位项。请在支持的客户端本地配置凭据，而不是放进公开 JSON。

本仓库不托管或执行第三方 JAR。外部仓库自己的扩展不在本项目的可用性保证范围内。

`encrypt_config.py` 仅保留实验性编码工具。Base64 不是加密；AES-ECB 是旧兼容格式，不适合安全保存秘密，且没有消息认证。工具不打印密钥，使用隐藏输入或环境变量 `YSC_CONFIG_KEY`；AES 需另装 `cryptography`。**未验证你的客户端能导入这些输出**，不要拿加密格式代替排查普通 JSON 连接。

## 历史与回退

本轮修复前基线：`cab190e05eef487a9ffceb250e4d7eafdc1f51c9`。原有 `.bak` 保留作历史参考，不作为当前配置，也不自动加载。回退时按文件选择 Git 历史，不覆盖其他新改动。

具体修复与验证边界见 [MAINTENANCE.md](MAINTENANCE.md)。来源维护地址见 [SOURCES.md](SOURCES.md)。
