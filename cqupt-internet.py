import re
import json
import socket
import psutil
import requests

config_web_server = {
    'scheme': 'http',
    'server': '192.168.200.2',
    'port': 80,
    'uri': '/'
}
url_web_server = (f'{config_web_server["scheme"]}://'
                  f'{config_web_server["server"]}:{config_web_server["port"]}{config_web_server["uri"]}')

config_auth_server = {
    'scheme': 'http',
    'server': '192.168.200.2',
    'port': 801,
    'uri': '/eportal/'
}
url_auth_server = (f'{config_auth_server["scheme"]}://'
                   f'{config_auth_server["server"]}:{config_auth_server["port"]}{config_auth_server["uri"]}')

# 预编译正则表达式，解析已登录的账户和运营商
__re_parse_account_isp = re.compile(
    r"uid\s*=\s*['\"](\d+)(?:@([A-Za-z0-9]+))?['\"]",
    re.IGNORECASE
)


def __parse_account_isp(content: str) -> tuple[str, str] | None:
    """从网页中解析已登录的账户和运营商，未解析到则返回None"""
    m = __re_parse_account_isp.search(content)
    if m:
        return m.group(1), m.group(2)
    return None


def __get_ip_mac() -> tuple[str, str]:
    """获取出网卡的IP和Mac地址"""
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

    raise Exception(f'Server `{config_auth_server["server"]}` unreachable.')


def __parse_json(data: str) -> dict:
    """从字符串中解析出json并转换为字典"""
    try:
        _idx_result_start = data.index('{')
        _idx_result_end = data.index('}')
    except ValueError:
        raise Exception(f'Not a JSON string: {data}')
    _result_json = data[_idx_result_start:_idx_result_end + 1]
    return json.loads(_result_json)


def get_status() -> tuple[str, str] | None:
    """获取已登录的账户和运营商，未登录则返回None"""
    response_webpage = requests.get(url_web_server)
    response_webpage.raise_for_status()
    return __parse_account_isp(response_webpage.text)


def login(account: str, password: str, isp: str, platform: str = '0') -> bool:
    """
    登录校园网宽带
    :param account: 统一认证码
    :param password: 密码
    :param isp: 运营商 电信:``telecom`` 移动:``cmcc`` 联通:``unicom``
    :param platform: 登录到的平台 电脑端:``0``/``pc`` 手机端:``1``/``mobile``
    :return: 是否登录成功
    """
    status = get_status()
    if status is not None:
        print(f'You have already logged in as account `{status[0]}` from ISP `{status[1].title()}`.')
        return True
    ip, mac = __get_ip_mac()

    if platform.strip().lower() in ['0', 'pc']:
        platform = '0'
    elif platform.strip().lower() in ['1', 'mobile']:
        platform = '1'
    else:
        print(f'Unknown platform: `{platform}`.')
        return False

    params = {
        'c': 'Portal',
        'a': 'login',
        'callback': 'dr1003',
        'login_method': '1',
        'user_account': f',{platform},{account}@{isp}',
        'user_password': password,
        'wlan_user_ip': ip,
        # 'wlan_user_ipv6': '',
        'wlan_user_mac': mac.replace('-', '').lower()
    }
    response_login = requests.get(url_auth_server, params=params)
    response_login.raise_for_status()
    _result = __parse_json(response_login.text)
    if _result['result'] != '1':
        print(f'Login failed. Detail: {_result}')
        return False
    print(f'Login succeeded. \n'
          f'\tAccount: {account}\n'
          f'\tISP: {isp.title()}\n'
          f'\tPlatform: {"PC" if platform == "0" else "Mobile"}\n'
          f'\tIP: {ip}\n'
          f'\tMAC: {mac}')
    return True


def logout() -> bool:
    """
    退出校园网宽带登录
    :return: 是否成功退出登录
    """
    status = get_status()
    if status is None:
        print(f'You have not logged in yet.')
        return True
    account, isp = status[0], status[1]
    ip, mac = __get_ip_mac()

    params = {
        'c': 'Portal',
        'a': 'unbind_mac',
        'callback': 'dr1002',
        'user_account': f'{account}@{isp}',
        'wlan_user_mac': mac.replace('-', '').lower(),
        'wlan_user_ip': ip
    }
    response_logout = requests.get(url_auth_server, params=params)
    response_logout.raise_for_status()
    _result = __parse_json(response_logout.text)
    if _result['result'] != '1':
        print(f'Logout failed. Detail: {_result}')
        return False
    print(f'Logout succeeded. \n'
          f'\tAccount: {account}\n'
          f'\tISP: {isp.title()}\n'
          f'\tIP: {ip}\n'
          f'\tMAC: {mac}')
    return True
