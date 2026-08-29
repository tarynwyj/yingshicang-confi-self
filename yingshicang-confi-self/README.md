# yingshicang-confi-self

这是一个最小、合法的影视仓配置模板，不包含第三方影视站点、盗版片源、解析接口或 Spider/JAR。

## 使用地址

在影视仓中导入下面的配置地址：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

配置中的直播源地址：

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/live.m3u
```

## 文件说明

- `config.json`：最小影视仓配置，站点列表为空，并指向本仓库的直播列表。
- `live.m3u`：合法直播源模板；默认不包含任何频道。
- `README.md`：使用说明。

## 添加自己的合法直播源

请只添加你拥有播放权、已经获得授权，或许可明确允许使用的直播流。M3U 示例：

```m3u
#EXTINF:-1 group-title="自有频道",频道名称
https://example.com/authorized-stream.m3u8
```

把示例替换成你有权使用的真实地址后，保存到 `live.m3u` 即可。
