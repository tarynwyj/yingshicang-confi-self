# 自有资源接入清单

## IPTV / M3U

仅把自有、获授权或许可明确允许使用的频道写入 `live.m3u`。每个频道至少需要：

```m3u
#EXTINF:-1 group-title="自有频道",频道名称
https://example.com/authorized-stream.m3u8
```

公开仓库中不要提交：

- 带用户名和密码的 URL；
- API Token、Cookie、Authorization Header；
- 临时签名或可代表账号权限的播放地址；
- 未确认授权范围的聚合列表。

## Jellyfin / Emby

最稳妥的方式是在影视仓客户端的媒体服务器页面中直接添加服务器。服务器地址应使用 HTTPS 或局域网地址，账号使用只读、最小权限。

如果自有网关确实提供 TVBox 兼容接口，可在 `config.json` 的 `sites` 中添加：

```json
{
  "key": "my-media",
  "name": "我的媒体库",
  "type": 1,
  "api": "https://media.example.com/tvbox/vod",
  "searchable": 1,
  "quickSearch": 0,
  "filterable": 1
}
```

不同网关的接口路径并不统一，应以你所部署软件的文档为准。

## Alist

Alist 本身不是统一的 TVBox `vod` 接口。需要由你控制的兼容网关进行转换，并确保网关不向公网暴露管理凭据。不要直接假定 `/vod` 路径一定存在。

## Spider / JAR

只使用自己构建或已经审计的扩展。提交前记录源代码仓库、版本、提交哈希与文件 SHA-256；不要加载来历不明的远程 JAR。

## Base64

Base64 只改变文本表示，不提供保密性。任何能读取文件的人都能还原原始配置。秘密应保存在客户端、私有网络或专用秘密管理系统中。
