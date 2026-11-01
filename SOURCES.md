# 来源与验证边界

本文件说明地址的来源，不认证第三方内容、授权或播放可用性。历史“✅可访问”不能当作当前状态；以带时间的 Actions 报告及设备实测为准。

## 自动同步的原有直播列表

| 保存文件 | 上游 |
|---|---|
| upstream/ipv6.m3u | https://live.fanmingming.com/tv/m3u/ipv6.m3u |
| upstream/itv.m3u | https://live.fanmingming.com/tv/m3u/itv.m3u |
| upstream/cn.m3u | https://iptv-org.github.io/iptv/countries/cn.m3u |
| upstream/hk.m3u | https://iptv-org.github.io/iptv/countries/hk.m3u |

程序读取的唯一同步清单是 `scripts/upstreams.json`。旧说明中的 `ipv4.m3u` 不对应原工作流使用的 `itv.m3u`，已纠正。同步失败保留旧文件，上游缺失频道保留为历史条目，不自动删除。

`tel.m3u` 为域名筛选视图，不证明来源官方、授权或运营商兼容；`all.m3u` 聚合所有列表并保留不同播放参数。两者都是生成文件，手工频道应添加到 `live.m3u`。

## 多仓

`multi.json` 共 23 个入口（2026-11-01 追加 4 个单仓；历史 19 个入口全部保留，未删除、未替换）。`multi-vod.json` 为 8 个点播来源的独立清单：10 月 1 日加入 6 个，10 月 9 日加入 Ray 和王二小维护镜像。历史第三方地址保持原样，自有直播配置已明确“无点播”。不根据一次检测删除或替换第三方域名。完整入口清单见下文「完整多仓入口」。

| 新增点播来源 | 维护仓库 | 本次配置站点数 |
|---|---|---|
| Qist 自用点播 | https://github.com/qist/tvbox | 149 |
| 饭太硬（Qist维护） | https://github.com/qist/tvbox | 47 |
| 潇洒（Qist维护） | https://github.com/qist/tvbox | 103 |
| 高天流云 PG | https://github.com/gaotianliuyun/gao | 135 |
| 高天流云 FTY | https://github.com/gaotianliuyun/gao | 51 |
| Gaoops点播 | https://github.com/mrgaoshuiquan/tvbox-config | 52 |
| Ray（dxawi，10月9日加入） | https://github.com/dxawi/0 | 48 |
| 王二小（维护镜像，10月9日加入） | https://github.com/Lightconer/tvbox-ysc-config | 63 |

这些数字是配置条目数，不是实测能播放的数量，来源之间可能重复。本次已验证配置内容、站点必要字段与引用扩展的 HTTP 响应及 ZIP/JAR 文件头；未执行扩展、未验证全部站点搜索和播放。具体时间、配置摘要及扩展检查结果保存在 `source-checks/2026-10-01-vod.json`。每个来源使用本轮实际可访问的地址，代理服务和上游仍可能变化。

未纳入本次点播清单的候选：仅本地/推送示例、站点字段不完整，以及本次无法读取或解析的配置。它们没有被宣传为可用。

截至 2026-10-01 的检查发现：一些入口返回普通 JSON，一些返回非标准内容，另有 DNS 失败、超时和 HTML 页面。状态会变化；JSON 条目数不代表能播放的站点数。实际最新状态请查看每次运行的健康报告。

## 完整多仓入口（23 个，2026-11-01 登记）

此前本文件只登记了 10 月新增的 8 个点播来源，没有列出 `multi.json` 的全部入口（包括肥猫等历史条目）。下表补齐全部 23 个。「观察」列是 2026-11-01 从本机直连探测的**配置级**结果（能否下载、JSON 能否解析、站点条目数），**不是播放验证**，状态会变化。

| # | 入口 | 地址 | 2026-11-01 观察 |
|---|---|---|---|
| 1 | Qist 自用点播 | https://gh-proxy.com/https://raw.githubusercontent.com/qist/tvbox/master/jsm.json | 可读（156 站） |
| 2 | 饭太硬（Qist维护） | https://gh-proxy.com/https://raw.githubusercontent.com/qist/tvbox/master/fty.json | 可读（48 站） |
| 3 | 潇洒（Qist维护） | https://gh-proxy.com/https://raw.githubusercontent.com/qist/tvbox/master/xiaosa/api.json | 可读（110 站） |
| 4 | 高天流云 PG | https://raw.githubusercontent.com/gaotianliuyun/gao/master/0825.json | 可读（135 站） |
| 5 | 高天流云 FTY | https://gh-proxy.com/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0826.json | 可读（51 站） |
| 6 | Gaoops点播 | https://gh-proxy.com/https://raw.githubusercontent.com/mrgaoshuiquan/tvbox-config/main/tvbox.json | 可读（52 站） |
| 7 | 我的直播配置（无点播） | https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/config.json | 直播配置（0 点播站点） |
| 8 | 高天流云-js | https://gh-proxy.com/raw.githubusercontent.com/gaotianliuyun/gao/master/js.json | 可读（298 站） |
| 9 | 高天流云-XYQ | https://gh-proxy.com/raw.githubusercontent.com/gaotianliuyun/gao/master/XYQ.json | 非 JSON（待验证） |
| 10 | 香雅情 | https://gh-proxy.com/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json | 非 JSON（待验证） |
| 11 | 南风 | https://gh-proxy.com/https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json | 非 JSON（待验证） |
| 12 | 小盒子4K | http://xhztv.top/4k.json | 非 JSON（待验证） |
| 13 | FongMi线路 | https://gh-proxy.com/raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json | 可读（33 站） |
| 14 | 肥猫 | http://肥猫.net/tv | 可读（39 站） |
| 15 | 饭太硬 | http://fty.xxooo.cf/tv | 不可达（连接重置） |
| 16 | 欧歌4K | http://tv.nxog.top/m/ | HTTP 403 |
| 17 | 王二小 | http://tvbox.xn--4kq62z5rby2qupq9ub.top/ | 非 JSON（待验证） |
| 18 | Ray（dxawi） | https://raw.githubusercontent.com/dxawi/0/main/0.json | 可读（48 站） |
| 19 | 王二小（维护镜像） | https://raw.githubusercontent.com/Lightconer/tvbox-ysc-config/main/output/wangerxiao.json | 可读（63 站） |
| 20 | 544609136 精简仓（54站） | https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_slim.json | 可读（54 站） |
| 21 | 544609136 完整仓（147站） | https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_full.json | 可读（147 站） |
| 22 | 聚合精选 ofind（222站） | https://ofind.cn/juhe-subhub/tvbox.json | 可读（222 站） |
| 23 | TVBox-Hub 精选（50站） | https://raw.githubusercontent.com/sylvan97/tvbox-hub/main/dist/index.json | 可读（50 站） |

「非 JSON」表示返回内容不是可解析 JSON（历史上分别出现过编码载荷、带注释/未转义换行的 JSON、HTML 页面等情况），需要在客户端实测，**不代表永久失效**。「不可达」与「HTTP 403」是当次网络观察，可能是临时故障、地区限制或上游变更。

## 2026-11-01 新增 4 个单仓

| 名称 | 维护仓库 | 配置地址 | 站点数 | 配置 SHA-256（前 12 位） | spider HTTP |
|---|---|---|---|---|---|
| 544609136 精简仓（54站） | https://github.com/544609136/tvbox | https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_slim.json | 54 | aed1f3a8642e | 200 |
| 544609136 完整仓（147站） | https://github.com/544609136/tvbox | https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_full.json | 147 | 6c8d1415210c | 200 |
| 聚合精选 ofind（222站） | https://github.com/zhuzhuyule/juhe-subhub | https://ofind.cn/juhe-subhub/tvbox.json | 222 | 2398df447359 | 200 |
| TVBox-Hub 精选（50站） | https://github.com/sylvan97/tvbox-hub | https://raw.githubusercontent.com/sylvan97/tvbox-hub/main/dist/index.json | 50 | f83ffa08016f | 200 |

已验证：配置 HTTP 200、JSON 可解析、站点条目齐全、spider 可下载（`ofind` 使用相对路径 `spider_special.jar`，已按配置地址解析后验证）；**未执行扩展、未验证播放**。证据见 [source-checks/2026-11-01-vod.json](source-checks/2026-11-01-vod.json)。这四个都是第三方聚合/精选仓，内容可能与现有入口重复，站点数不等于可播放数量。

## 当前外部来源警告（2026-10-26，运行 40295958617）

下列条目**保持原地址，未改写、未删除**。警告表示本次需要关注，不等于永久失效；状态与错误类别以当次运行的报告为准。

| 来源 | 报告状态 | 本次观察 | 处置 |
|---|---|---|---|
| 南风 | `unverified_format` | 返回整段十六进制字符组成的文本（编码载荷）；未尝试解码，也未执行任何脚本 | 需在客户端验证；不改地址 |
| 小盒子4K | `unverified_format` | 返回带注释的 JSON 文本，但字符串内含未转义换行，严格 JSON 解析失败；客户端可能容忍 | 需在客户端验证；不改地址 |
| 饭太硬 | `unreachable` | 域名 `fty.xxooo.cf` 本次 DNS 解析失败 | 检查域名与网络后重试；暂时不可达 |
| 欧歌4K | `unreachable` | 运行环境返回 HTTP 错误，具体状态码见当次报告 `detail` | 检查上游状态；不改地址 |
| 王二小 | `unreachable` | 12 秒超时 | 重试；暂时不可达 |

同日在本机复跑时，欧歌4K 与王二小均为 12 秒超时，饭太硬仍为 DNS 失败：不同网络路径下错误类别可能不同，以当次报告为准。

## 自有媒体、JAR、编码

自有媒体服务器尚缺地址与兼容接口；不存在可用的默认账号或占位服务器。第三方 JAR 不在本仓库存储、运行。Base64/AES 工具是格式实验，不保证影视仓兼容，不用于保存需要保密的内容。

## 检测与自动任务

`check_sources.py` 只读源文件，只写独立健康报告；校验完整和点播多仓，支持 JSONC；空响应记为 `invalid`，编码载荷与非严格 JSON 分别归类；没有自动删源模式。
`sync_sources.py` 下载并验证上游，保护旧列表。
工作流每天北京时间 11:20 计划执行，重新生成列表并仅提交限定输出文件；报告异常不删除用户来源。每次运行在 Actions 的 Summary 按来源列出类别与建议，完整 JSON 报告保留 30 天。
使用说明见 [README.md](README.md)，维护细节与检查器状态见 [MAINTENANCE.md](MAINTENANCE.md)。

## 检查记录

- [2026-10-01 点播来源检查](source-checks/2026-10-01-vod.json)
- [2026-10-09 点播来源检查](source-checks/2026-10-09-vod.json)
- [2026-11-01 多仓新增来源检查](source-checks/2026-11-01-vod.json)
- 每次运行的结构与联网检查结果，见该次 Actions 运行的 Summary 与 `source-reports-运行编号` 附件（保留 30 天）。

## 2026-10-09 检测补充

新增两个入口均通过 GitHub 云端配置读取、站点结构和主扩展 ZIP/JAR 文件头检查，Ray 的相对路径脚本已确认存在；未执行扩展，实际搜索播放待设备验证。王二小为已有来源的另一维护入口，不视为独立内容库。肥猫维护镜像虽然配置和主扩展可读取，但存在镜像缺失的相对依赖，因此本轮不加入；4K 小盒子候选发生 HTTP 错误，未加入本次点播清单——它与完整多仓中的历史条目“小盒子4K”（`http://xhztv.top/4k.json`）不是同一地址，本次检测为 `unverified_format`，两者不要混淆。证据见 `source-checks/2026-10-09-vod.json`。

外部源异常只生成警告与报告，正常完成维护；程序、配置、测试、报告、磁盘写入或发布故障仍导致任务失败。
