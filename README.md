# 📺 我的影视仓配置

平时自己用影视仓时，整理了一些电影、电视剧和电视直播的配置地址，顺手放在 GitHub 上，方便自己更新，也分享给有需要的人。

**不需要下载整个仓库，复制下面的配置地址，在支持的影视仓 / TVBox 客户端里导入就行。**

## 📌 配置地址

### 🎬 电影、电视剧（推荐先试）

整理了 8 个点播来源，放在 `multi-vod.json`，适合平时主要看电影、电视剧的朋友。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

### 📦 完整合集

`multi.json` 里包含 19 个仓库入口，保留了之前收集的老仓库，也加入了一些新来源。想自己多试几个仓库，可以选这个。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

### 📡 电视直播

只想看电视直播的话，用 `config.json` 就够了。里面有 6 个直播列表，包括央视卫视、国内及香港频道，也有一个测试用的列表。部分频道对网络有要求，不保证全部能播。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

另外两个入口，按需使用：

- 连接测试：`https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config-test.json`（里面是 Apple 的 HLS 测试视频，用来确认客户端能不能正常加载配置）
- 聚合直播 M3U：`https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/upstream/all.m3u`（有些客户端需要 M3U 格式的直播地址）

## 🛠️ 怎么导入？

1. 打开你在用的影视仓 / TVBox 客户端，找到「配置」或「多仓 / 仓库管理」入口。
2. 复制上面的地址，粘贴进去，加载。
3. 如果导入的是多仓配置，加载后还要在仓库列表里选一个具体仓库。

**注意：** 前两个地址是多仓合集，需要在支持「多仓」的入口里导入。如果粘到普通单仓配置框里加载不了，不一定是地址坏了。

不同版本的客户端，设置入口可能不太一样。

## 🌐 地址打不开怎么办？

GitHub 的原始地址在部分网络下可能访问不了，可以试试备用地址。

**点播合集 CDN 地址：**

```text
https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/multi-vod.json
```

**点播合集代理地址：**

```text
https://gh-proxy.com/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

其他文件也可以这样替换：把 `https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/` 换成 `https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/`。备用地址也可能受网络或缓存影响。

## ❓ 遇到问题？

**导入成功了，却没有电影电视剧？**

先看看是不是用了直播配置——直播配置里没有点播站点；多仓配置则需要在仓库列表里选一个具体仓库。

**能看到影片，但播放不了？**

可以换一个站点或者线路试试。第三方来源偶尔会失效，也可能受网络、地区或播放方式限制。

**配置一直加载不出来？**

先检查地址有没有复制完整，再确认客户端是否支持这种配置格式，也可以换个备用地址试试。

**怎么还是旧内容？**

在客户端里重新加载一次配置。部分客户端和 CDN 会缓存之前的内容。

## ❤️ 关于这个仓库

这是我个人整理和维护的配置合集，不是影视仓播放器，也不托管影视内容。

第三方来源可能随时变化。我会保留历史配置，不会因为偶尔连接失败就直接删掉。仓库里的自动检查主要用来发现配置和连接问题，不能代替真实播放测试。

请根据自己的客户端和网络情况选择配置，并只访问你有权使用的内容。

想了解来源和维护方式，可以看看：

[来源及检测记录](SOURCES.md) · [更新与维护说明](MAINTENANCE.md) · [安全说明](SECURITY.md)
