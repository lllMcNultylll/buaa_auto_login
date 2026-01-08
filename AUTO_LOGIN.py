#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北航校园网自动登录脚本
功能：
1. 定时检测网络连接状态
2. 自动连接 WiFi：BUAA-WIFI
3. 自动通过校园网登录认证
4. 动态获取 ac_id 参数
5. 日志记录功能
6. 配置文件支持
"""

import requests
import socket
import time
import math
import hmac
import hashlib
import getpass
import json
import urllib3
import subprocess
import re
import os
from datetime import datetime

urllib3.disable_warnings()


# ==================== 配置文件 ====================
CONFIG_FILE = "config.json"
# ================================================


def load_config():
    """加载配置文件"""
    config = {
        "username": "",
        "password": "",
        "check_interval": 300,
        "enable_logging": True,
        "log_file": "auto_login.log",
        "test_url": "http://www.baidu.com",
        "wifi_ssid": "BUAA-WiFi"
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")

    return config


class AutoLogin:
    def __init__(self, config=None):
        self.config = config or load_config()
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.check_interval = self.config.get("check_interval", 300)
        self.enable_logging = self.config.get("enable_logging", True)
        self.log_file = self.config.get("log_file", "auto_login.log")
        self.test_url = self.config.get("test_url", "http://www.baidu.com")
        self.wifi_ssid = self.config.get("wifi_ssid", "BUAA-WiFi")

        self.ac_id = None
        self.current_ip = None

        # 初始化日志文件
        if self.enable_logging:
            self._init_log_file()

    def _init_log_file(self):
        """初始化日志文件"""
        try:
            # 如果日志文件不存在，创建并写入头部
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"北航校园网自动登录脚本日志\n")
                    f.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 80 + "\n\n")
        except Exception as e:
            print(f"无法创建日志文件: {e}")

    def log(self, message):
        """输出日志信息并写入日志文件（如果启用）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        # 输出到控制台
        print(log_message)

        # 如果启用日志，写入日志文件
        if self.enable_logging:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"写入日志失败: {e}")

    def check_network(self):
        """检查网络是否连通"""
        try:
            # 尝试连接外网
            response = requests.get(self.test_url, timeout=5)
            if response.status_code == 200:
                self.log(f"网络连接正常 (状态码: {response.status_code})")
                return True
        except requests.exceptions.RequestException:
            pass

        self.log("网络连接断开")
        return False

    def connect_wifi(self):
        """自动连接到 WiFi"""
        self.log(f"尝试连接 WiFi: {self.wifi_ssid}")

        try:
            # 使用 Windows 命令连接 WiFi
            # 先检查是否已连接到目标 WiFi
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore'
            )

            if self.wifi_ssid in result.stdout:
                self.log(f"已连接到 {self.wifi_ssid}")
                return True

            # 连接到指定 WiFi
            result = subprocess.run(
                ['netsh', 'wlan', 'connect', f'name={self.wifi_ssid}'],
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore'
            )

            if result.returncode == 0:
                self.log(f"成功连接到 {self.wifi_ssid}")
                # 等待 WiFi 连接稳定
                time.sleep(3)
                return True
            else:
                self.log(f"连接 WiFi 失败: {result.stderr}")
                return False

        except Exception as e:
            self.log(f"连接 WiFi 时出错: {e}")
            return False

    def get_jsonp(self, url, params):
        """发送 JSONP 请求并解码响应"""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36",
        }
        callback_name = "jQuery112406951885120277062_" + str(int(time.time() * 1000))
        params['callback'] = callback_name
        resp = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
        return json.loads(resp.text[len(callback_name) + 1:-1])

    def get_user_ip_from_html(self):
        """从登录页面 HTML 中动态获取 IP 地址和 ac_id"""
        try:
            session = requests.Session()
            r = session.get('https://gw.buaa.edu.cn/', verify=False, timeout=10)

            # 提取 IP 地址
            ip_match = re.search(r'name="user_ip"\s+id="user_ip"\s+value="([^"]+)"', r.text)
            if ip_match:
                self.current_ip = ip_match.group(1)
                self.log(f"自动获取到 IP 地址: {self.current_ip}")

            # 提取 ac_id
            ac_id_match = re.search(r'name="ac_id"\s+id="ac_id"\s+value="([^"]+)"', r.text)
            if ac_id_match:
                self.ac_id = ac_id_match.group(1)
                self.log(f"自动获取到 ac_id: {self.ac_id}")
            else:
                self.ac_id = "76"  # 默认值
                self.log(f"未能获取 ac_id，使用默认值: {self.ac_id}")

            return self.current_ip, self.ac_id

        except Exception as e:
            self.log(f"从 HTML 获取信息失败: {e}，使用默认值")
            self.ac_id = "76"
            return None, self.ac_id

    def get_ip_token(self, username):
        """获取客户端 IP 和 challenge token"""
        get_challenge_url = "https://gw.buaa.edu.cn/cgi-bin/get_challenge"
        get_challenge_params = {
            "username": username,
            "ip": '0.0.0.0',
            "_": int(time.time() * 1000)
        }
        res = self.get_jsonp(get_challenge_url, get_challenge_params)
        return res["client_ip"], res["challenge"]

    def get_info(self, username, password, ip):
        """构建登录信息"""
        params = {
            'username': username,
            'password': password,
            'ip': ip,
            'acid': str(self.ac_id),
            "enc_ver": 'srun_bx1'
        }
        info = json.dumps(params)
        return info

    # ==================== 加密相关函数 ====================
    def force(self, msg):
        ret = []
        for w in msg:
            ret.append(ord(w))
        return bytes(ret)

    def ordat(self, msg, idx):
        if len(msg) > idx:
            return ord(msg[idx])
        return 0

    def sencode(self, msg, key):
        l = len(msg)
        pwd = []
        for i in range(0, l, 4):
            pwd.append(
                self.ordat(msg, i) | self.ordat(msg, i + 1) << 8 | self.ordat(msg, i + 2) << 16
                | self.ordat(msg, i + 3) << 24)
        if key:
            pwd.append(l)
        return pwd

    def lencode(self, msg, key):
        l = len(msg)
        ll = (l - 1) << 2
        if key:
            m = msg[l - 1]
            if m < ll - 3 or m > ll:
                return
            ll = m
        for i in range(0, l):
            msg[i] = chr(msg[i] & 0xff) + chr(msg[i] >> 8 & 0xff) + chr(
                msg[i] >> 16 & 0xff) + chr(msg[i] >> 24 & 0xff)
        if key:
            return "".join(msg)[0:ll]
        return "".join(msg)

    def get_xencode(self, msg, key):
        if msg == "":
            return ""
        pwd = self.sencode(msg, True)
        pwdk = self.sencode(key, False)
        if len(pwdk) < 4:
            pwdk = pwdk + [0] * (4 - len(pwdk))
        n = len(pwd) - 1
        z = pwd[n]
        y = pwd[0]
        c = 0x86014019 | 0x183639A0
        m = 0
        e = 0
        p = 0
        q = math.floor(6 + 52 / (n + 1))
        d = 0
        while 0 < q:
            d = d + c & (0x8CE0D9BF | 0x731F2640)
            e = d >> 2 & 3
            p = 0
            while p < n:
                y = pwd[p + 1]
                m = z >> 5 ^ y << 2
                m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
                m = m + (pwdk[(p & 3) ^ e] ^ z)
                pwd[p] = pwd[p] + m & (0xEFB8D130 | 0x10472ECF)
                z = pwd[p]
                p = p + 1
            y = pwd[0]
            m = z >> 5 ^ y << 2
            m = m + ((y >> 3 ^ z << 4) ^ (d ^ y))
            m = m + (pwdk[(p & 3) ^ e] ^ z)
            pwd[n] = pwd[n] + m & (0xBB390742 | 0x44C6F8BD)
            z = pwd[n]
            q = q - 1
        return self.lencode(pwd, False)

    _PADCHAR = "="
    _ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

    def _getbyte(self, s, i):
        x = ord(s[i])
        if (x > 255):
            print("INVALID_CHARACTER_ERR: DOM Exception 5")
            exit(0)
        return x

    def get_base64(self, s):
        i = 0
        b10 = 0
        x = []
        imax = len(s) - len(s) % 3
        if len(s) == 0:
            return s
        for i in range(0, imax, 3):
            b10 = (self._getbyte(s, i) << 16) | (self._getbyte(s, i + 1) << 8) | self._getbyte(s, i + 2)
            x.append(self._ALPHA[(b10 >> 18)])
            x.append(self._ALPHA[((b10 >> 12) & 63)])
            x.append(self._ALPHA[((b10 >> 6) & 63)])
            x.append(self._ALPHA[(b10 & 63)])
        i = imax
        if len(s) - imax == 1:
            b10 = self._getbyte(s, i) << 16
            x.append(self._ALPHA[(b10 >> 18)] +
                     self._ALPHA[((b10 >> 12) & 63)] + self._PADCHAR + self._PADCHAR)
        elif len(s) - imax == 2:
            b10 = (self._getbyte(s, i) << 16) | (self._getbyte(s, i + 1) << 8)
            x.append(self._ALPHA[(b10 >> 18)] + self._ALPHA[((b10 >> 12) & 63)] + self._ALPHA[((b10 >> 6) & 63)] + self._PADCHAR)
        return "".join(x)

    def get_md5(self, password, token):
        return hmac.new(token.encode(), password.encode(), hashlib.md5).hexdigest()

    def get_sha1(self, value):
        return hashlib.sha1(value.encode()).hexdigest()
    # ==================================================

    def login(self, retry_count=0):
        """执行登录操作"""
        # 限制重试次数，防止无限递归
        MAX_RETRY = 3
        if retry_count >= MAX_RETRY:
            self.log(f"已达到最大重试次数 ({MAX_RETRY})，停止重试")
            return False

        self.log("开始校园网登录...")

        # 1. 动态获取 ac_id 和 IP
        self.log("步骤 1: 获取登录参数...")
        self.get_user_ip_from_html()

        # 2. 构建登录信息
        self.log("步骤 2: 构建登录信息...")
        # 使用从 HTML 获取的 IP，如果没有则使用默认值
        ip = self.current_ip if self.current_ip else "10.34.0.142"
        info = self.get_info(self.username, self.password, ip)

        # 3. 获取 challenge token（在发送请求前立即获取，避免过期）
        self.log("步骤 3: 获取 challenge token...")
        try:
            token_ip, token = self.get_ip_token(self.username)
            # 如果从 token 获取的 IP 不同，使用 token IP
            if token_ip != ip:
                self.log(f"IP 地址变化: {ip} -> {token_ip}")
                ip = token_ip
                # 重新构建登录信息
                info = self.get_info(self.username, self.password, ip)
            self.log(f"获取到 IP: {ip}, Token: {token[:20]}...")
        except Exception as e:
            self.log(f"获取 token 失败: {e}")
            return False

        # 4. 发送登录请求
        self.log("步骤 4: 发送登录请求...")
        srun_portal_url = "https://gw.buaa.edu.cn/cgi-bin/srun_portal"

        data = {
            "action": "login",
            "username": self.username,
            "password": "{MD5}" + self.get_md5(self.password, token),
            "ac_id": self.ac_id,
            "ip": ip,
            "info": "{SRBX1}" + self.get_base64(self.get_xencode(info, token)),
            "n": "200",
            "type": "1",
            "os": "Windows 10",
            "name": "PC",
            "double_stack": '',
            "_": int(time.time() * 1000)
        }

        # 计算校验和
        chkstr = token + self.username
        chkstr += token + self.get_md5(self.password, token)
        chkstr += token + str(self.ac_id)
        chkstr += token + ip
        chkstr += token + '200'
        chkstr += token + '1'
        chkstr += token + "{SRBX1}" + self.get_base64(self.get_xencode(info, token))
        data['chksum'] = self.get_sha1(chkstr)

        try:
            result = self.get_jsonp(srun_portal_url, data)
            self.log(f"登录响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # 判断登录成功的条件：
            # 1. ecode == 0 且 suc_msg == 'login_ok' (正常登录)
            # 2. ecode == 0 且 suc_msg == 'ip_already_online_error' (已经在线)
            # 3. ecode == 0 且 error 包含 'challenge_expire_error' 或 'sign_error'，但实际可能已登录
            if result.get('ecode') == 0 and result.get('suc_msg') in ['login_ok', 'ip_already_online_error']:
                if result.get('suc_msg') == 'ip_already_online_error':
                    self.log("登录成功！IP 已经在线")
                else:
                    self.log("登录成功！")
                return True
            elif result.get('ecode') == 0 and result.get('error') in ['challenge_expire_error', 'sign_error']:
                # 这些错误可能实际上已经登录成功，验证一下网络是否可用
                self.log(f"收到 {result.get('error')} 错误，验证网络连接...")
                if self.check_network():
                    self.log("网络连接正常，登录实际上已成功")
                    return True
                else:
                    self.log("网络连接失败，尝试重新登录...")
                    return self.login(retry_count + 1)
            else:
                self.log(f"登录失败: {result.get('error_msg', '未知错误')}")
                return False
        except Exception as e:
            self.log(f"登录请求失败: {e}")
            return False

    def run(self):
            """主运行循环"""
            self.log("=" * 60)
            self.log("北航校园网自动登录脚本启动")
            self.log(f"用户名: {self.username}")
            self.log(f"检测间隔: {self.check_interval} 秒 ({self.check_interval//60} 分钟)")
            self.log(f"日志功能: {'启用' if self.enable_logging else '禁用'}")
            if self.enable_logging:
                self.log(f"日志文件: {os.path.abspath(self.log_file)}")
            self.log("=" * 60)
    
            while True:
                try:
                    # 检查网络连接
                    if not self.check_network():
                        self.log("网络断开，开始自动连接...")
    
                        # 连接 WiFi
                        if self.connect_wifi():
                            # 等待网络稳定
                            time.sleep(2)
    
                            # 登录校园网
                            if self.login():
                                self.log("自动登录完成，网络已恢复")
                            else:
                                self.log("登录失败，将在下次检测时重试")
                        else:
                            self.log("WiFi 连接失败，将在下次检测时重试")
                    else:
                        self.log(f"网络正常，{self.check_interval} 秒后再次检测")
    
                    # 等待下一次检测
                    time.sleep(self.check_interval)
    
                except KeyboardInterrupt:
                    self.log("\n" + "=" * 80)
                    self.log("收到中断信号，程序退出")
                    self.log(f"退出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    self.log("=" * 80)
                    break
                except Exception as e:
                    self.log(f"发生错误: {e}")
                    self.log(f"{self.check_interval} 秒后继续检测...")
                    time.sleep(self.check_interval)
def main():
    """主函数"""
    print("=" * 60)
    print("北航校园网自动登录脚本")
    print("=" * 60)

    # 加载配置
    config = load_config()

    # 获取用户名（支持默认值）
    default_username = config.get("username", "")
    username_input = input(f"请输入用户名 (默认: {default_username}): ").strip()
    if username_input:
        config["username"] = username_input

    # 获取密码（支持默认值）
    default_password = config.get("password", "")
    if default_password:
        print(f"请输入密码 (默认: 已配置): ")
        password_input = getpass.getpass("")
        if not password_input:
            password_input = default_password
    else:
        password_input = getpass.getpass("请输入密码: ")

    if not password_input:
        print("密码不能为空！")
        return

    config["password"] = password_input

    # 创建自动登录实例并运行
    auto_login = AutoLogin(config=config)
    auto_login.run()


if __name__ == "__main__":
    main()