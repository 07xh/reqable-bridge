# 云端 Reqable Receiver：管理网页停止整页刷新

适用：使用 FastAPI/Uvicorn + SQLite 的 `reqable-receiver` 服务，HTML 中包含 `<meta http-equiv="refresh" content="4">` 的版本。

## 一键更新（阿里云 Ubuntu 终端）

以下命令仅从此仓库的修复分支下载脚本，不会修改数据库；脚本会自动备份当前服务文件、替换刷新标签，并在运行中的 `reqable-receiver` 服务检测通过后重启：

```bash
curl -fL --retry 3 https://raw.githubusercontent.com/07xh/reqable-bridge/fix/cloud-dashboard-idle-refresh/cloud/fix_dashboard_refresh.py -o /tmp/reqable-fix-refresh.py
sudo python3 /tmp/reqable-fix-refresh.py
```

如果下载时 GitHub 网络不可达，可使用仓库下载文件后上传到服务器，再执行 `sudo python3 <文件路径>`。

如果脚本输出“未找到对应的 server.py”，先执行：

```bash
sudo systemctl cat reqable-receiver
```

从 `ExecStart` 查看正在运行的脚本绝对路径，之后执行：

```bash
sudo python3 /tmp/reqable-fix-refresh.py --file /实际路径/server.py
```

## 验证

1. 更新后打开原来的 Tailscale 管理页并刷新一次。
2. 观察至少 10 秒：浏览器不再每 4 秒自动加载整页。
3. 点击“手动刷新列表”应仍能看到请求。
4. 需要时检查服务：`sudo systemctl status reqable-receiver --no-pager`。

## 变更范围与安全

- 仅删除 4 秒整页刷新的 HTML meta 标签，新增手动刷新入口；**不是**后台实时抓包开关。
- 不修改 SQLite、HAR 接收接口、HAR 详情、HAR 下载、HTTP Basic 认证或 Tailscale 监听。
- 自动在原脚本目录保存 `server.py.bak-<UTC时间>`；若服务重启失败，脚本会回滚并尝试恢复服务。
- 若未找到预期的旧版代码或匹配多个文件，脚本停止，不会猜测修改目标。
- 不会自动更新整个请求列表；有新上报时点“手动刷新列表”即可。

注意：合并 PR/下载补丁与**已经在阿里云部署成功**是不同的状态，实际服务器需执行上面两条命令并验证。
