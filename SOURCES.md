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

`multi.json` 共 24 个入口（2026-11-01 追加入口后经 2026-11-22 清理与扩充：删除 4 个长期失效入口，新增 5 个实测可读的来源）。`multi-vod.json` 为 11 个点播来源的独立清单，面向“先试一个能用的仓”。完整入口清单见下表。

2026-11-22：① 原 15 条 `gh-proxy.com` 代理地址全部返回 HTTP 403（`Access to proxy rules is forbidden on this hostname: gh-proxy.com`，任意目标仓库同样如此，站点首页仍正常打开），该代理已停止转发，配置里的地址统一改走 `ghproxy.net` 代理前缀；② 删除实测长期失效的 4 个入口：肥猫（Cloudflare 521）、饭太硬（旧域名 `fty.xxooo.cf` 无法连接）、欧歌4K（HTTP 403）、王二小（网页入口 HTTP 504，原 `raw` 镜像入口保留）；③ 新增 5 个当日实测可读、spider 可下载的来源。上游 owner/repo/分支/路径不变，只调整代理前缀与条目集合。

判定口径：配置 HTTP 200、JSON 可解析（含注释/尾逗号容忍）、`sites` 条目数、`spider` 可下载；**未执行 JAR、未验证播放**。`ghproxy.net` 首次拉取大文件可能较慢或偶发 5xx，重试即可，不代表来源失效。

另有 `multi-cn.json`（国内直连版，22 个入口，按 `sites` 数排序）：2026-11-22 新增并扩充，供直连 `raw.githubusercontent.com` 不通、且 `ghproxy.net` 也被网络阻断的客户端使用。该清单不经过任何 GitHub 代理，全部走 jsDelivr 或来源自有域名；因 jsDelivr 拒绝 `.jar` 扩展，只收录依赖文件为 `.txt` 或非 GitHub 托管的来源。候选来自 `thevip001/tvbox-agg` 的接口清单与 GitHub 搜索，共探测 79 条地址，19 条通过（配置 200、JSON 可解析、`sites` ≥ 10、`spider` 可下载），与原有 jsDelivr 可用源合并去重后为 22 条；22 条当日复核全部为 `config 200` + `spider 200`。其中 `kstore.space`/`kstore.vip`、`jihulab.com`、`serv00.net`、`xhztv.top`、`iptv365.org` 等为第三方或个人线路，随时可能失效，失效属正常，不等于该接口永久不可用。

| # | 入口 | 地址 | 2026-11-22 观察 |
|---|---|---|---|
| 1 | Qist 自用点播 | https://ghproxy.net/https://raw.githubusercontent.com/qist/tvbox/master/jsm.json | 可读（162 站） |
| 2 | 饭太硬（Qist维护） | https://ghproxy.net/https://raw.githubusercontent.com/qist/tvbox/master/fty.json | 可读（50 站） |
| 3 | 潇洒（Qist维护） | https://ghproxy.net/https://raw.githubusercontent.com/qist/tvbox/master/xiaosa/api.json | 可读（116 站） |
| 4 | 高天流云 PG | https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0825.json | 可读（135 站） |
| 5 | 高天流云 FTY | https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0826.json | 可读（51 站） |
| 6 | Gaoops点播 | https://ghproxy.net/https://raw.githubusercontent.com/mrgaoshuiquan/tvbox-config/main/tvbox.json | 可读（52 站） |
| 7 | 我的直播配置（无点播） | https://ghproxy.net/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json | 直播配置（0 点播站点） |
| 8 | 高天流云-js | https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json | 可读（298 站） |
| 9 | 高天流云-XYQ | https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/XYQ.json | 编码载荷（待验证，47 站，spider 可下载） |
| 10 | 香雅情 | https://ghproxy.net/https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json | 编码载荷（待验证，48 站，spider 可下载） |
| 11 | 南风 | https://ghproxy.net/https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json | 编码载荷（待验证，spider 可下载） |
| 12 | 小盒子4K | http://xhztv.top/4k.json | 非 JSON 文本（待验证，30 KB） |
| 13 | FongMi线路 | https://ghproxy.net/https://raw.githubusercontent.com/gaotianliuyun/gao/master/0827.json | 可读（33 站） |
| 14 | Ray（dxawi） | https://ghproxy.net/https://raw.githubusercontent.com/dxawi/0/main/0.json | 可读（48 站） |
| 15 | 王二小（维护镜像） | https://ghproxy.net/https://raw.githubusercontent.com/Lightconer/tvbox-ysc-config/main/output/wangerxiao.json | 可读（100 站） |
| 16 | 544609136 精简仓（54站） | https://ghproxy.net/https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_slim.json | 可读（54 站） |
| 17 | 544609136 完整仓（147站） | https://ghproxy.net/https://raw.githubusercontent.com/544609136/tvbox/main/cur/vod_full.json | 可读（147 站） |
| 18 | 聚合精选 ofind（222站） | https://ofind.cn/juhe-subhub/tvbox.json | 可读（222 站） |
| 19 | TVBox-Hub 精选（50站） | https://ghproxy.net/https://raw.githubusercontent.com/sylvan97/tvbox-hub/main/dist/index.json | 可读（50 站） |
| 20 | 544609136 合并仓（777站，含网盘/P2P） | https://ghproxy.net/https://raw.githubusercontent.com/544609136/tvbox/main/cur/combo.json | 可读（777 站，spider 约 18 MB） |
| 21 | Qist 综合仓（163站） | https://ghproxy.net/https://raw.githubusercontent.com/qist/tvbox/master/dianshi.json | 可读（163 站） |
| 22 | Qist 0821 整合仓（86站） | https://ghproxy.net/https://raw.githubusercontent.com/qist/tvbox/master/0821.json | 可读（86 站） |
| 23 | Jinenge 内置源（59站） | https://jinenge.us.kg/app/tvbox/tvbox.json | 可读（59 站，自带直播与 jar） |
| 24 | TVBox-Hub 轻量（20站） | https://ghproxy.net/https://raw.githubusercontent.com/sylvan97/tvbox-hub/main/dist/lite.json | 可读（20 站） |

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

外部源异常只生成警告与报告，正常完成维护；程序、配置、测试、报告、磁盘写入或发布故障仍导致任务失败。
