# 📺 我的影视仓配置

平时自己用影视仓时，整理了一些电影、电视剧和电视直播的配置地址，顺手放在 GitHub 上，方便自己更新，也分享给有需要的人。

**不需要下载整个仓库，复制下面的配置地址，在支持的影视仓 / TVBox 客户端里导入就行。**

## 📌 配置地址

### 🎬 电影、电视剧（推荐先试）

整理了 11 个点播来源，放在 `multi-vod.json`，适合平时主要看电影、电视剧的朋友。都是 2026-11-22 实测能打开、依赖文件能下载的仓。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
```

### 📦 完整合集

`multi.json` 里包含 24 个仓库入口，保留了之前收集的老仓库，也加入了一些新来源。想自己多试几个仓库，可以选这个。失效的老入口（肥猫、饭太硬旧域名、欧歌4K、王二小网页入口）已经清掉。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi.json
```

### 📡 电视直播

只想看电视直播的话，用 `config.json` 就够了。里面有 6 个直播列表，包括央视卫视、国内及香港频道，也有一个测试用的列表。部分频道对网络有要求，不保证全部能播。

```text
https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/config.json
```

### 🚄 国内直连版（不用 GitHub 代理）

`multi-cn.json` 是给国内网络、直连 `raw.githubusercontent.com` 不通、GitHub 加速站也不稳的朋友准备的。共 **22 个入口，全部走 jsDelivr 或来源自有域名**，不经过任何 GitHub 代理站。

顺序是**实测加载速度**（拉配置 + 拉依赖文件的总耗时，2026-11-22 测），前面最快：前 6 条都在 0.5 秒内，`摸鱼`、`王二小`、`嗷呜` 最快。末尾的 `幸福年年`（依赖 8 秒）和 `宝盒`（依赖 45 秒）能用但慢，排在最后当备用。

因为 jsDelivr 会拒绝 `.jar` 文件，这个版本只收两类源：依赖文件是 `.txt` 的（Qist、高天流云、TVBox-Hub），以及本身架在国内/第三方域名上的（摸鱼、clun、王二小、香雅情等）。站数写在各条名字里，只是配置里登记的站点数量，不等于都能播。

```text
https://cdn.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/multi-cn.json
```

jsDelivr 对分支有缓存（几小时到半天），刚更新完可能还是旧内容；要立刻拿最新版，把 `@main` 换成最近一次提交的哈希，例如 `@d252616`。

`cdn.jsdelivr.net` 打不开时，换同样内容的备用节点：

```text
https://gcore.jsdelivr.net/gh/tarynwyj/yingshicang-confi-self@main/multi-cn.json
https://jsd.onmicrosoft.cn/gh/tarynwyj/yingshicang-confi-self@main/multi-cn.json
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
https://ghproxy.net/https://raw.githubusercontent.com/tarynwyj/yingshicang-confi-self/main/multi-vod.json
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

[来源及检测记录](SOURCES.md) · [更新与维护说明](MAINTENANCE.md)
