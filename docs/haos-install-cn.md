# Xiaozhi MCP WebSearch Add-on 中文安装指南

本文说明如何把 `Xiaozhi MCP WebSearch Add-on` 添加到 Home Assistant，并配置给小智使用。

如果你的 HAOS 只剩 100 多 MB 空间，优先不要使用本文的 Add-on 方式。请改用更轻量的自定义集成版：

[custom-component-install-cn.md](custom-component-install-cn.md)

Add-on 会触发 Supervisor Docker build，需要更多磁盘空间；自定义集成版不需要 Docker build。

## 1. 当前能力说明

这个 Add-on 只负责联网搜索能力：

- `web_search`
- `fetch_url`

它不控制 Home Assistant 设备，不读取 HA 实体，也不调用 HA API。  
设备控制请继续使用 `xiaozhi-mcp-ha` 或 Home Assistant 官方 MCP Server。

推荐搜索源：

- 开发测试：`mock`
- 国内正式：`bocha`
- 低成本备用：`baidu_qianfan`

小智连接方式参考 `c1pher-cn/ha-mcp-for-xiaozhi`：Add-on 主动连接小智 MCP 接入点 WebSocket 地址。

## 2. 准备 Add-on 仓库

当前项目目录是：

```text
xiaozhi-mcp-websearch-addon/
├── repository.json
├── README.md
└── xiaozhi_mcp_websearch/
    ├── config.yaml
    ├── Dockerfile
    ├── run.sh
    ├── requirements.txt
    └── app/
```

Home Assistant 添加自定义 Add-on 仓库时，需要一个 Git 仓库地址。你有两种方式：

## 3. 方式一：上传到 GitHub

在电脑上把 `xiaozhi-mcp-websearch-addon` 初始化为 Git 仓库并推送到 GitHub。

示例：

```bash
cd xiaozhi-mcp-websearch-addon
git init
git add .
git commit -m "Add Xiaozhi MCP WebSearch add-on"
git remote add origin https://github.com/你的用户名/xiaozhi-mcp-websearch-addon.git
git push -u origin main
```

推送完成后，你会得到类似这样的仓库地址：

```text
https://github.com/你的用户名/xiaozhi-mcp-websearch-addon
```

后面在 Home Assistant 里添加这个地址。

## 4. 方式二：局域网 Git 仓库

如果你不想上传 GitHub，也可以在局域网机器上搭建 Git 服务，例如 Gitea、GitLab 或 NAS 自带 Git 服务。

Home Assistant 需要能访问这个仓库地址，例如：

```text
http://192.168.1.10:3000/你的用户名/xiaozhi-mcp-websearch-addon
```

注意：如果你用的是 HAOS，直接把文件复制到 HA 文件系统里通常不能自动变成 Add-on Store 仓库。最稳妥方式仍然是提供一个 Git 仓库 URL。

## 5. 在 Home Assistant 添加 Add-on 仓库

进入 Home Assistant 页面：

```text
设置 -> 加载项 -> 加载项商店
```

然后：

1. 点击右上角三个点菜单。
2. 选择“仓库”。
3. 粘贴你的 Add-on 仓库地址。
4. 点击“添加”。
5. 等待 Home Assistant 刷新加载项列表。

刷新完成后，应该能看到：

```text
Xiaozhi MCP WebSearch
```

## 6. 安装 Add-on

点击 `Xiaozhi MCP WebSearch`，然后点击：

```text
安装
```

Raspberry Pi 4B 运行 64 位 HAOS 时，对应架构是：

```text
aarch64
```

本 Add-on 已在 `config.yaml` 里声明支持：

```yaml
arch:
  - aarch64
  - amd64
```

## 7. 第一次启动建议：mock 模式

第一次不要直接连小智，也不要先填搜索 API。先用 `mock` 验证 Add-on 能启动。

配置示例：

```yaml
mode: mcp_http
host: 0.0.0.0
port: 8765
public_base_url: ""
xiaozhi_ws_endpoint: ""
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: mock
bocha_api_key: ""
bocha_base_url: "https://api.bochaai.com/v1/web-search"
baidu_qianfan_api_key: ""
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
searxng_base_url: ""
brave_api_key: ""
max_search_results: 5
fetch_timeout_seconds: 10
max_fetch_chars: 12000
safe_mode: true
log_level: info
```

保存配置后点击：

```text
启动
```

然后查看日志，确认没有报错。

## 8. 本地 HTTP 测试

如果你处于 `mode: mcp_http`，可以在局域网电脑上测试：

```bash
curl http://HA_IP:8765/health
```

期望返回：

```json
{
  "status": "ok",
  "service": "xiaozhi-mcp-websearch",
  "version": "0.1.0"
}
```

查看工具列表：

```bash
curl http://HA_IP:8765/tools
```

测试 mock 搜索：

```bash
curl -X POST http://HA_IP:8765/tools/web_search \
  -H "Content-Type: application/json" \
  -d '{"query":"Home Assistant MCP Server","count":3}'
```

把 `HA_IP` 换成你的 Home Assistant 地址，例如：

```text
192.168.1.20
```

## 9. 配置国内正式搜索：Bocha

正式使用建议先配置 Bocha。

```yaml
search_provider: bocha
bocha_api_key: "你的_BOCHA_API_KEY"
bocha_base_url: "https://api.bochaai.com/v1/web-search"
```

其他搜索源配置保持不变即可。

注意：API Key 不要写进代码，只填在 Add-on 配置里。

## 10. 配置备用搜索：百度千帆百度搜索

低成本备用可以使用百度千帆百度搜索。

```yaml
search_provider: baidu_qianfan
baidu_qianfan_api_key: "你的_APPBUILDER_API_KEY"
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
```

`lite` 是推荐的低成本配置。也可以使用：

```yaml
baidu_qianfan_edition: standard
```

## 11. 配置小智 WebSocket MCP 连接

当你已经在小智后台拿到 MCP 接入点地址后，把模式改为：

```yaml
mode: xiaozhi_ws
xiaozhi_ws_endpoint: "wss://你的小智MCP接入点地址"
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
```

完整示例，使用 Bocha：

```yaml
mode: xiaozhi_ws
host: 0.0.0.0
port: 8765
public_base_url: ""
xiaozhi_ws_endpoint: "wss://你的小智MCP接入点地址"
xiaozhi_ws_reconnect_seconds: 10
xiaozhi_ws_heartbeat_seconds: 50
search_provider: bocha
bocha_api_key: "你的_BOCHA_API_KEY"
bocha_base_url: "https://api.bochaai.com/v1/web-search"
baidu_qianfan_api_key: ""
baidu_qianfan_base_url: "https://qianfan.baidubce.com/v2/ai_search/web_search"
baidu_qianfan_edition: lite
searxng_base_url: ""
brave_api_key: ""
max_search_results: 5
fetch_timeout_seconds: 10
max_fetch_chars: 12000
safe_mode: true
log_level: info
```

重要说明：

- `xiaozhi_ws_endpoint` 是小智后台提供的 WebSocket 地址。
- 这个 Add-on 是主动连出去，不是让小智连进 HA。
- `/xiaozhi/ws` 不是给小智访问的入口。
- 如果小智后台只允许配置一个 MCP endpoint，那么你需要在 `xiaozhi-mcp-ha` 和本 Add-on 之间二选一，或者后续使用统一 Gateway。

## 12. 检查日志

启动后查看 Add-on 日志。

HTTP 模式正常日志应类似：

```text
Starting Xiaozhi MCP WebSearch with config: ...
Uvicorn running on http://0.0.0.0:8765
```

小智 WebSocket 模式正常日志应类似：

```text
Xiaozhi WebSocket mode enabled; connecting to ***
Connected to Xiaozhi MCP endpoint
```

如果看到：

```text
xiaozhi_ws_endpoint is required when mode=xiaozhi_ws
```

说明你开启了 `xiaozhi_ws`，但没有填写小智 MCP 接入点地址。

## 13. 常见问题

### 13.1 Add-on Store 里看不到加载项

检查：

- 仓库地址是否能被 HA 访问。
- 仓库根目录是否有 `repository.json`。
- Add-on 目录里是否有 `config.yaml`。
- GitHub 仓库是否是公开仓库，或者 HA 是否有权限访问私有仓库。

### 13.2 Raspberry Pi 4B 无法安装

确认你的 HAOS 是 64 位系统。64 位 Raspberry Pi 4B 对应：

```text
aarch64
```

### 13.3 端口访问不到

默认端口是：

```text
8765
```

确认：

- Add-on 已启动。
- `mode` 是 `mcp_http`。
- HA 防火墙或路由没有阻止访问。
- `config.yaml` 中端口映射仍是 `8765/tcp: 8765`。

### 13.4 小智连接不上

检查：

- `mode` 是否为 `xiaozhi_ws`。
- `xiaozhi_ws_endpoint` 是否以 `ws://` 或 `wss://` 开头。
- 小智 MCP 接入点是否仍有效。
- 接入点地址里如果包含 token，不要删掉 query 参数。
- HAOS 是否能访问外网。

### 13.5 搜索返回 API Key 错误

检查当前 `search_provider` 对应的 key：

- `bocha` 使用 `bocha_api_key`
- `baidu_qianfan` 使用 `baidu_qianfan_api_key`
- `brave` 使用 `brave_api_key`

开发测试时可以先切回：

```yaml
search_provider: mock
```

## 14. 推荐上线顺序

建议按这个顺序排查：

1. `mode: mcp_http` + `search_provider: mock`
2. HTTP `/health` 测试通过
3. HTTP `/tools/web_search` mock 测试通过
4. 切换 `search_provider: bocha`
5. HTTP 搜索真实 API 测试通过
6. 切换 `mode: xiaozhi_ws`
7. 填入小智 MCP 接入点
8. 在小智侧测试 `web_search` / `fetch_url`

这样如果出问题，可以快速判断是 Add-on 启动问题、搜索 API 问题，还是小智 WebSocket 连接问题。
