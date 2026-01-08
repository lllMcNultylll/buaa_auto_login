
>   based on https://github.com/luoboganer
    based on https://coding.net/u/huxiaofan1223/p/jxnu_srun/git
    based on https://blog.csdn.net/qq_41797946/article/details/89417722
    based on https://github.com/zzdyyy/buaa_gateway_login


# Author
lllMcNultylll

# 北航校园网自动登录脚本

自动化登录北京航空航天大学校园网的 Python 脚本，支持自动连接 WiFi、定时检测网络状态、自动重新登录等功能。

## 功能特性

- 自动检测网络连接状态
- 自动连接指定 WiFi（BUAA-WiFi）
- 自动通过校园网认证登录
- 动态获取登录参数（ac_id、IP 地址）
- 支持配置文件管理
- 可选的日志记录功能
- 智能重试机制（最多3次）
- 智能错误处理（自动验证网络状态）

## 系统要求

- Windows 操作系统
- Python 3.6+
- 网络功能正常

## 安装依赖

```bash
pip install requests
```

## 快速开始

### 1. 配置文件

首次运行前，需要创建配置文件 `config.json`：

```json
{
  "username": "your_username",
  "password": "your_password",
  "check_interval": 300,
  "enable_logging": true,
  "log_file": "auto_login.log",
  "test_url": "http://www.baidu.com",
  "wifi_ssid": "BUAA-WiFi"
}
```

可以参考 `config.json.example` 文件作为模板编辑 `config.json`，填入您的用户名和密码。

### 2. 运行脚本

请在脚本工作的目录打开终端，或在终端中进入工作目录 

```shell
cd where/the-script/is 
```

```bash
python AUTO_LOGIN.py
```

运行后会提示输入用户名和密码：
- 用户名：直接回车使用配置文件中的默认值
- 密码：直接回车使用配置文件中的默认值，或输入新密码

若想在后台长期运行本脚本，请自行配置。

### 3. 停止脚本

按 `Ctrl+C` 停止脚本运行。

## 配置说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `username` | string | 校园网账号 | - |
| `password` | string | 校园网密码 | - |
| `check_interval` | int | 网络检测间隔（秒） | 300 |
| `enable_logging` | bool | 是否启用日志功能 | true |
| `log_file` | string | 日志文件名 | auto_login.log |
| `test_url` | string | 用于测试网络连接的 URL | http://www.baidu.com |
| `wifi_ssid` | string | 要自动连接的 WiFi 名称 | BUAA-WiFi |

## 日志功能

脚本支持将运行日志记录到文件中，便于查看历史记录和排查问题。

日志文件示例：

```
================================================================================
北航校园网自动登录脚本日志
启动时间: 2025-01-10 20:37:04
================================================================================

[2025-01-10 20:37:04] ============================================================
[2025-01-10 20:37:04] 北航校园网自动登录脚本启动
[2025-01-10 20:37:04] 用户名: 张广（已接受教育）
[2025-01-10 20:37:04] 检测间隔: 300 秒 (5 分钟)
[2025-01-10 20:37:04] 日志功能: 启用
[2025-01-10 20:37:04] 日志文件: ~\...\auto_login.log
[2025-01-10 20:37:04] ============================================================
[2025-01-10 20:37:04] 网络连接断开
[2025-01-10 20:37:04] 网络断开，开始自动连接...
[2025-01-10 20:37:04] 尝试连接 WiFi: BUAA-WiFi
[2025-01-10 20:37:04] 成功连接到 BUAA-WiFi
[2025-01-10 20:37:09] 开始校园网登录...
[2025-01-10 20:37:09] 步骤 1: 获取登录参数...
[2025-01-10 20:37:09] 自动获取到 IP 地址: XX.XX.XX.XX
[2025-01-10 20:37:09] 自动获取到 ac_id: 76
[2025-01-10 20:37:09] 步骤 2: 获取 challenge token...
[2025-01-10 20:37:10] 获取到 IP: XX.XX.XX.XXX, Token: manmanmanmanmanmanmna...
[2025-01-10 20:37:10] 步骤 3: 构建登录信息...
[2025-01-10 20:37:10] 步骤 4: 发送登录请求...
[2025-01-10 20:37:10] 登录成功！
[2025-01-10 20:37:10] 自动登录完成，网络已恢复
[2025-01-10 20:37:10] 网络正常，300 秒后再次检测
```

## 常见问题

### 1. 提示"网络连接断开"但实际可以上网

可能是测试 URL 设置不当，可以尝试修改 `test_url` 为其他可访问的网站。

### 2. WiFi 连接失败

- 确认 WiFi 名称（SSID）配置正确
- 确认系统已保存该 WiFi 的密码
- 检查 WiFi 是否在范围内

### 3. 登录失败

- 检查用户名和密码是否正确
- 确认校园网账号状态正常
- 查看日志文件获取详细错误信息
- 如果看到 `challenge_expire_error` 或 `sign_error`，脚本会自动验证网络状态并重试

### 4. 如何修改检测间隔

编辑 `config.json` 文件，修改 `check_interval` 参数（单位：秒）。

### 5. 为什么看到登录错误但网络正常？

校园网服务器有时会返回 `challenge_expire_error` 或 `sign_error` 错误，但实际上登录可能已经成功。脚本会自动验证网络连接状态，如果网络可用，就认为登录成功。

## 文件说明

```
buaa_auto_login/
├── AUTO_LOGIN.py           # 主程序文件
├── config.json             # 配置文件（需自行创建）
├── config.json.example     # 配置文件模板
└── README.md               # 本说明文档
```

## 开发说明

本项目基于以下开源项目：
- https://github.com/luoboganer
- https://coding.net/u/huxiaofan1223/p/jxnu_srun/git
- https://blog.csdn.net/qq_41797946/article/details/89417722
- https://github.com/zzdyyy/buaa_gateway_login

**免责声明**：本脚本仅供学习和研究使用，使用本脚本所产生的一切后果由使用者自行承担。