import re
import time
import json
import socket
import psutil
import requests

# 认证服务器信息
config_web_server = {
    'scheme': 'http',
    'server': '192.168.200.2',
    'port': 80,
    'uri': '/'
}
config_auth_server = {
    'scheme': 'http',
    'server': '192.168.200.2',
    'port': 801,
    'uri': '/eportal/'
}
url_web_server = (f'{config_web_server["scheme"]}://'
                  f'{config_web_server["server"]}:{config_web_server["port"]}{config_web_server["uri"]}')
url_auth_server = (f'{config_auth_server["scheme"]}://'
                   f'{config_auth_server["server"]}:{config_auth_server["port"]}{config_auth_server["uri"]}')

# 预编译正则表达式，用于从html解析已登录的账户和运营商
__re_parse_account_isp = re.compile(
    r"uid\s*=\s*['\"](\d+)(?:@([A-Za-z0-9]+))?['\"]",
    re.IGNORECASE
)


class AuthServerUnreachableError(Exception):
    """认证服务器不可达异常"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def __parse_json(response_text: str) -> dict:
    """
    从服务器返回的字符串中解析出json并转换为字典
    :param response_text: 服务器返回的字符串
    :return: 表示服务器返回的结果的字典
    """
    try:
        _idx_result_start = response_text.index('{')
        _idx_result_end = response_text.rindex('}')
        _result_json = response_text[_idx_result_start:_idx_result_end + 1]
        result = json.loads(_result_json)
    except (ValueError, json.decoder.JSONDecodeError):
        raise ValueError(f'Not a JSON string: {response_text}')
    return result


def get_ip_mac() -> tuple[str, str]:
    """
    获取出网卡的IP和Mac地址，如不可达则抛出AuthServerUnreachableError异常
    :return: 出网卡IP，出网卡Mac地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((config_auth_server['server'], config_auth_server['port']))
        local_ip = s.getsockname()[0]  # 出网卡的本地IP
    finally:
        s.close()

    addrs = psutil.net_if_addrs()
    for interface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET and addr.address == local_ip:
                mac = next(a.address for a in addr_list if a.family == psutil.AF_LINK)
                return local_ip, mac

    raise AuthServerUnreachableError(f'Server `{config_auth_server["server"]}` unreachable.')


def get_status() -> dict:
    """
    获取登录状态信息
    :return: 状态信息字典（包括is_logged_in: bool, account: str, isp: str, ip: str, mac: str）
    """
    ip, mac = get_ip_mac()
    response_webpage = requests.get(url_web_server)
    response_webpage.raise_for_status()
    m = __re_parse_account_isp.search(response_webpage.text)
    if m:
        return {
            'is_logged_in': True,
            'account': m.group(1),
            'isp': m.group(2),
            'ip': ip,
            'mac': mac
        }
    return {
        'is_logged_in': False,
        'account': '',
        'isp': '',
        'ip': ip,
        'mac': mac
    }


def login(account: str, password: str, isp: str, platform: str = '0') -> tuple[bool, dict]:
    """
    登录校园网宽带
    :param account: 统一认证码
    :param password: 密码
    :param isp: 运营商 电信:``telecom`` 移动:``cmcc`` 联通:``unicom``
    :param platform: 登录到的平台 电脑端:``0``/``pc`` 手机端:``1``/``mobile``
    :return: 登录操作是否成功，登录结果字典
    """
    isp = isp.strip().lower()
    platform = platform.strip().lower()
    assert isp in ['telecom', 'cmcc', 'unicom'], 'Unknown ISP.'
    assert platform in ['0', 'pc', '1', 'mobile'], 'Unknown platform.'

    if platform == 'pc':
        platform = '0'
    elif platform == 'mobile':
        platform = '1'

    status = get_status()
    if status['is_logged_in']:
        status['msg'] = 'You have already logged in. No need to log in again.'
        return True, status

    params = {
        'c': 'Portal',
        'a': 'login',
        'callback': 'dr1003',
        'login_method': '1',
        'user_account': f',{platform},{account}@{isp}',
        'user_password': password,
        'wlan_user_ip': status['ip'],
        # 'wlan_user_ipv6': '',
        'wlan_user_mac': status['mac'].replace('-', '').lower()
    }
    response_login = requests.get(url_auth_server, params=params)
    response_login.raise_for_status()
    time.sleep(1)

    status = get_status()
    response_login_json = __parse_json(response_login.text)
    if response_login_json['result'] != '1' or (not status['is_logged_in']):
        status['msg'] = f'Login failed. Detail: {response_login.text}'
        return False, status
    status['msg'] = 'Login succeed.'
    return True, status


def logout() -> tuple[bool, dict]:
    """
    退出校园网宽带登录
    :return: 退出操作是否成功，退出结果字典
    """
    status = get_status()
    if not status['is_logged_in']:
        status['msg'] = 'You have not logged in yet. No need to log out.'
        return True, status

    params = {
        'c': 'Portal',
        'a': 'unbind_mac',
        'callback': 'dr1002',
        'user_account': f'{status['account']}@{status['isp']}',
        'wlan_user_mac': status['mac'].replace('-', '').lower(),
        'wlan_user_ip': status['ip']
    }
    response_logout = requests.get(url_auth_server, params=params)
    response_logout.raise_for_status()
    time.sleep(1)

    status = get_status()
    response_logout_json = __parse_json(response_logout.text)
    if response_logout_json['result'] != '1' or status['is_logged_in']:
        status['msg'] = f'Logout failed. Detail: {response_logout.text}'
        return False, status
    status['msg'] = 'Logout succeed.'
    return True, status
