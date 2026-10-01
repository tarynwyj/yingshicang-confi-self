# yingshicang-confi-self

影视仓/TVBox 配置研究仓库。当前主配置包含多个直播列表；其中部分频道会受运营商、地区或播放授权限制。

## 配置拉取失败时先用测试入口

测试配置只加载一条 Apple 官方 HLS 测试视频，可用于区分“配置网址无法打开”和“某个频道源无法播放”：

```text
https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/config-test.json
```

备用测试入口：

```text
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config-test.json
```

如果测试配置也提示“配置拉取失败”，请用电视自带浏览器打开同一网址。浏览器也打不开时，检查电视网络、DNS、代理设置和系统时间；如果浏览器能看到 JSON，但影视仓仍报错，请记录影视仓版本和报错截图。

## 主配置

测试成功后，在影视仓的“配置地址”中使用：

```text
https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/config.json
```

备用入口：

```text
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

GitHub 原始地址：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

原始地址在部分网络上会超时。不同网络的访问结果可能不同。每次只粘贴一条完整网址，不要复制代码块里的说明文字。

## 当前文件

| 文件 | 用途 |
|---|---|
| `config.json` | 主配置，保留原有直播分组；已移除指向 `127.0.0.1` 的占位媒体站点 |
| `config-test.json` | 只有一条测试视频的独立配置 |
| `live.m3u` | 自选频道列表，目前含 Apple HLS 测试视频 |
| `multi.json` | 单独的多仓入口，不应填到主配置地址栏 |
| `upstream/` | 先前生成的直播列表快照，频道本身可能失效或受地域限制 |
| `scripts/check_sources.py` | 只读格式检查，可用 `--network` 手动检查公网地址 |
| `.github/workflows/update-config.yml` | 每天只读验证，不自动删除频道或改写配置 |

影视仓导入配置成功不代表列表中所有频道都能播放。先在“本地直播(我的)”中播放 Apple HLS 测试视频，确认列表读取和 HLS 播放均正常，再测试其他分组。

## 自有媒体服务

Jellyfin、Emby、Alist 的服务器地址应在你的设备上可访问。原配置的 `127.0.0.1` 指向电视自身，并不是你的电脑或 NAS，因此已从公开配置移除。请使用影视仓支持的媒体库入口，或在确认 TVBox 兼容接口后填入实际的局域网/HTTPS 地址。不要把密码或 Token 写入公开仓库。

## 添加自有频道

在 `live.m3u` 中按两行一组添加有权使用的播放地址：

```m3u
#EXTINF:-1 group-title="自有频道",频道名称
https://example.com/authorized-stream.m3u8
```
