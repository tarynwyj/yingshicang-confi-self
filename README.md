# yingshicang-confi-self

用于研究影视仓/TVBox 配置格式的最小合法模板。仓库不包含第三方影视站点、解析接口、未审核 Spider/JAR 或来历不明的直播频道。

## 导入地址

主配置：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

多仓入口：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

直播列表：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/live.m3u
```

## 添加自有频道

编辑 `live.m3u`，按下面格式添加拥有播放权或已获授权的地址：

```m3u
#EXTINF:-1 group-title="自有频道",频道名称
https://example.com/authorized-stream.m3u8
```

## Jellyfin、Emby 与 Alist

优先使用影视仓客户端自带的媒体服务器入口添加 Jellyfin/Emby。需要通过 TVBox 配置接入时，应先在自己的网络中部署兼容接口，再把 `config.json` 的 `sites` 指向该接口。

不要在公开仓库中保存用户名、密码、API Token、Cookie 或带长期签名参数的地址。Alist 等服务应使用只读、最小权限账号，并通过 HTTPS 或私有网络访问。示例和核对清单见 `SOURCES.md`。

## 工具与自动检查

- `scripts/check_sources.py`：检查 JSON、M3U 结构；加 `--network` 可测试公开 HTTP(S) 地址。
- `scripts/encrypt_config.py`：生成 Base64 文本；Base64 不是加密，不能保护秘密。
- `.github/workflows/update-config.yml`：每天验证格式。只有设置仓库变量 `ENABLE_NETWORK_CHECK=true` 时才进行公网连通性检查。

本工作流只读，不下载、镜像或自动提交第三方播放列表。
