# 项目概述

这是一个用于北京航空航天大学（BUAA）网络准入认证系统的命令行自动登录工具。项目提供了两种不同的登录实现方式，用于通过命令行方式登录到 `gw.buaa.edu.cn` 网关。

## 项目结构

```
buaa_auto_login/
├── buaa_gateway_login.py  # 完整的 SRUN 系统登录实现（推荐）
├── login.py               # 简化的登录实现
├── login.txt              # 登录页面 HTML 模板
└── IFLOW.md               # 项目说明文档
```

## 主要技术

- **语言**: Python 3
- **HTTP 请求**: requests 库
- **加密算法**: HMAC-MD5, SHA1, Base64, 自定义 XEncode 加密
- **认证协议**: SRUN 3000 网关认证协议

## 核心文件说明

### buaa_gateway_login.py
这是项目的主要登录脚本，实现了完整的 SRUN 网关认证流程：

**主要功能**:
- 动态获取客户端 IP 地址
- 获取认证 challenge token
- 使用 MD5 和 XEncode 算法加密用户凭证
- 生成校验和（chksum）
- 发送登录请求并处理响应

**关键函数**:
- `get_ip_token(username)`: 获取客户端 IP 和 challenge token
- `get_info(username, password, ip)`: 构建登录信息
- `get_md5(password, token)`: MD5 加密密码
- `get_xencode(msg, key)`: 自定义加密算法
- `login(username, password)`: 执行完整的登录流程

**依赖库**:
- requests
- socket
- time
- math
- hmac
- hashlib
- getpass
- json
- urllib3

### login.py
这是一个简化的登录实现，采用更直接的方式提交表单数据：

**主要功能**:
- 从登录页面 HTML 中动态提取 IP 地址
- 简化的 POST 请求登录
- 自动检测登录状态

**特点**:
- 代码更简洁
- 使用正则表达式提取 IP
- 提供详细的登录反馈

### login.txt
包含登录页面的 HTML 源码，用于：
- 分析登录表单结构
- 提取必要的隐藏字段（如 ac_id, user_ip 等）
- 参考 DOM 结构和参数名称

## 运行方法

### 使用 buaa_gateway_login.py（推荐）

```bash
python buaa_gateway_login.py
```

运行后按提示输入：
- 用户名
- 密码（输入时不会显示）

### 使用 login.py

```bash
python login.py
```

运行后按提示输入：
- 账号
- 密码

## 开发约定

### 代码风格
- 使用 Python 标准库和第三方库
- 函数命名使用下划线命名法（snake_case）
- 包含详细的中文注释和文档字符串

### 安全实践
- 使用 `getpass` 模块安全获取密码输入
- 禁用 SSL 证书验证（`urllib3.disable_warnings()`）
- 密码在传输前进行加密处理

### 加密流程
1. 获取 challenge token
2. 使用 HMAC-MD5 加密密码: `{MD5}` + md5(password + token)
3. 使用 XEncode 加密用户信息
4. 生成 SHA1 校验和

## 注意事项

1. **IP 地址**: 每次登录时 IP 地址可能变化，脚本会尝试自动获取
2. **ac_id 参数**: 根据不同的接入点（AP），ac_id 可能需要调整
3. **网络环境**: 确保能够访问 `gw.buaa.edu.cn`
4. **依赖安装**: 运行前确保安装了 requests 库

```bash
pip install requests
```

## 故障排查

如果登录失败，请检查：
1. 用户名和密码是否正确
2. 网络连接是否正常
3. 网关 URL 是否需要更新
4. ac_id 参数是否匹配当前的接入点
5. 使用浏览器开发者工具检查实际的登录请求参数

## 参考资料

- SRUN 网关认证协议文档
- https://github.com/luoboganer
- https://coding.net/u/huxiaofan1223/p/jxnu_srun/git
- https://blog.csdn.net/qq_41797946/article/details/89417722