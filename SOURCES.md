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

`multi.json` 共 17 个入口：6 个新增点播来源放在前面，历史 11 个入口（包括自有直播配置）全部保留。`multi-vod.json` 为这 6 个新增来源的独立清单。历史第三方地址保持原样，自有直播配置已明确“无点播”。不根据一次检测删除或替换第三方域名。

| 新增点播来源 | 维护仓库 | 本次配置站点数 |
|---|---|---|
| Qist 自用点播 | https://github.com/qist/tvbox | 149 |
| 饭太硬（Qist维护） | https://github.com/qist/tvbox | 47 |
| 潇洒（Qist维护） | https://github.com/qist/tvbox | 103 |
| 高天流云 PG | https://github.com/gaotianliuyun/gao | 135 |
| 高天流云 FTY | https://github.com/gaotianliuyun/gao | 51 |
| Gaoops点播 | https://github.com/mrgaoshuiquan/tvbox-config | 52 |

这些数字是配置条目数，不是实测能播放的数量，来源之间可能重复。本次已验证配置内容、站点必要字段与引用扩展的 HTTP 响应及 ZIP/JAR 文件头；未执行扩展、未验证全部站点搜索和播放。具体时间、配置摘要及扩展检查结果保存在 `source-checks/2026-10-01-vod.json`。每个来源使用本轮实际可访问的地址，代理服务和上游仍可能变化。

未纳入本次点播清单的候选：仅本地/推送示例、站点字段不完整，以及本次无法读取或解析的配置。它们没有被宣传为可用。

截至 2026-10-01 的检查发现：一些入口返回普通 JSON，一些返回非标准内容，另有 DNS 失败、超时和 HTML 页面。状态会变化；JSON 条目数不代表能播放的站点数。实际最新状态请查看每次运行的健康报告。

## 自有媒体、JAR、编码

自有媒体服务器尚缺地址与兼容接口；不存在可用的默认账号或占位服务器。第三方 JAR 不在本仓库存储、运行。Base64/AES 工具是格式实验，不保证影视仓兼容，不用于公开保存凭据。

## 检测与自动任务

`check_sources.py` 只读源文件，只写独立健康报告；校验完整和点播多仓，支持 JSONC；没有自动删源模式。
`sync_sources.py` 下载并验证上游，保护旧列表。
工作流每天北京时间 11:20 计划执行，重新生成列表并仅提交限定输出文件；报告异常不删除用户来源。
完整使用说明与缓存、设备验证边界见 README。
