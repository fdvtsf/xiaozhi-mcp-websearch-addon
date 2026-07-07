# Xiaozhi MCP WebSearch 自定义集成安装指南

这是低磁盘空间环境推荐的安装方式。

和 Add-on 不同，自定义集成不会触发 Supervisor 的 Docker build，也不会拉取 `docker:*` 构建镜像。它运行在 Home Assistant Core 的 Python 环境里，方式更接近 `ha-mcp-for-xiaozhi`。

## 1. 适用场景

推荐使用自定义集成版，如果你的 HAOS：

- 只剩几百 MB 或更少磁盘空间
- 拉 Docker Hub 镜像经常超时
- 已经能正常运行 `ha-mcp-for-xiaozhi`
- 只需要小智通过 MCP 调用 `web_search` 和 `fetch_url`

## 2. 当前目录

仓库里新增了：

```text
custom_components/
└── xiaozhi_mcp_websearch/
    ├── __init__.py
    ├── config_flow.py
    ├── manifest.json
    ├── websocket_transport.py
    ├── mcp_server.py
    ├── web_search.py
    ├── fetch_url.py
    ├── security.py
    └── ...
```

你只需要把整个 `xiaozhi_mcp_websearch` 文件夹复制到 HA 的：

```text
/config/custom_components/xiaozhi_mcp_websearch
```

## 3. 通过 Samba / Studio Code Server 复制

如果你已经在 HA 里装了 Samba share 或 Studio Code Server：

1. 打开 HA 的 `/config` 目录。
2. 如果没有 `custom_components`，新建这个目录。
3. 把仓库里的：

```text
custom_components/xiaozhi_mcp_websearch
```

复制到：

```text
/config/custom_components/xiaozhi_mcp_websearch
```

最终结构应该是：

```text
/config/custom_components/xiaozhi_mcp_websearch/manifest.json
/config/custom_components/xiaozhi_mcp_websearch/__init__.py
/config/custom_components/xiaozhi_mcp_websearch/config_flow.py
```

注意不要复制成：

```text
/config/custom_components/xiaozhi_mcp_websearch/xiaozhi_mcp_websearch/manifest.json
```

多套一层会导致 HA 找不到集成。

## 4. 重启 Home Assistant

复制完成后，必须重启 Home Assistant Core：

```text
设置 -> 系统 -> 右上角电源按钮 -> 重启 Home Assistant
```

只重载 YAML 通常不够，需要重启 Core。

## 5. 添加集成

重启后进入：

```text
设置 -> 设备与服务 -> 添加集成
```

搜索：

```text
Xiaozhi MCP WebSearch
```

如果搜不到：

- 检查目录是否放对。
- 检查 `manifest.json` 是否在第一层。
- 查看 HA Core 日志有没有 Python 依赖安装失败。
- 再重启一次 Home Assistant Core。

## 6. 配置字段

核心字段：

```text
xiaozhi_ws_endpoint
```

这是小智后台给你的 MCP WebSocket 接入点，例如：

```text
wss://你的接入点地址
```

搜索源推荐：

```text
mock          开发测试
bocha         国内正式推荐
baidu_qianfan 低成本备用
```

## 7. 推荐第一次配置

第一次建议先用 `mock`，确认小智连接链路通了：

```text
xiaozhi_ws_endpoint: 填小智 MCP 接入点
search_provider: mock
max_search_results: 5
fetch_timeout_seconds: 10
max_fetch_chars: 12000
safe_mode: true
```

如果小智能看到 `web_search` / `fetch_url` 工具，说明集成启动和 MCP 连接正常。

## 8. Bocha 正式配置

正式搜索推荐 Bocha：

```text
search_provider: bocha
bocha_api_key: 你的 Bocha API Key
bocha_base_url: https://api.bochaai.com/v1/web-search
```

## 9. 百度千帆备用配置

低成本备用可以使用百度千帆百度搜索：

```text
search_provider: baidu_qianfan
baidu_qianfan_api_key: 你的 AppBuilder API Key
baidu_qianfan_base_url: https://qianfan.baidubce.com/v2/ai_search/web_search
baidu_qianfan_edition: lite
```

## 10. 日志查看

进入：

```text
设置 -> 系统 -> 日志
```

正常启动时应看到类似：

```text
Starting Xiaozhi MCP WebSearch integration
Xiaozhi MCP WebSearch connecting to ***
Connected to Xiaozhi MCP endpoint
```

如果看到：

```text
xiaozhi_ws_endpoint is required
```

说明接入点为空。

如果看到依赖安装失败，一般是 HAOS 访问 PyPI 不通。这个集成依赖比 Add-on 少很多，但仍需要安装：

```text
mcp==1.14.1
beautifulsoup4==4.12.3
```

## 11. 和 Add-on 版的区别

自定义集成版：

- 不需要 Docker build
- 不拉 Docker Hub 基础镜像
- 更省磁盘
- 和 `ha-mcp-for-xiaozhi` 形态一致
- 运行在 HA Core Python 进程中

Add-on 版：

- 独立容器，隔离更好
- 需要 Supervisor build 镜像
- 需要更多磁盘空间
- 网络不通 Docker Hub 时容易安装失败

你当前 HAOS 只剩 100 多 MB，更建议使用自定义集成版。

