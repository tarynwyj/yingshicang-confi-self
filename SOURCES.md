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

`multi.json` 保留历史 11 个入口（包括自有直播配置）。地址保持原样，仅把自有配置的固定旧提交链接改回主分支，并明确“无点播”。不根据一次检测删除或替换第三方域名，也不自动下载扩展。

截至 2026-10-01 的检查发现：一些入口返回普通 JSON，一些返回非标准内容，另有 DNS 失败、超时和 HTML 页面。状态会变化；JSON 条目数不代表能播放的站点数。实际最新状态请查看每次运行的健康报告。

## 自有媒体、JAR、编码

自有媒体服务器尚缺地址与兼容接口；不存在可用的默认账号或占位服务器。第三方 JAR 不在本仓库存储、运行。Base64/AES 工具是格式实验，不保证影视仓兼容，不用于公开保存凭据。

## 检测与自动任务

`check_sources.py` 只读源文件，只写独立健康报告；没有自动删源模式。
`sync_sources.py` 下载并验证上游，保护旧列表。
工作流每天北京时间 11:20 计划执行，重新生成列表并仅提交限定输出文件；报告异常不删除用户来源。
完整使用说明与缓存、设备验证边界见 README。
