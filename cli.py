import os
import time
import toml
import getpass
import argparse
import datetime
import cqupt_internet

__installed_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.toml')


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        prog='cqupt-internet', description=f'A CLI tool for logging in and logging out of CQUPT Internet.'
    )
    subparsers = parser.add_subparsers(dest="action", required=True, help="Available actions.")

    # login操作
    login_parser = subparsers.add_parser("login", help="Login to CQUPT Internet.")
    login_parser.add_argument("-a", "--account", "-u", "--user", help="Account ID.")
    login_parser.add_argument(
        "-p", "--password",
        help="Password. Not recommended to use this parameter in CLI. For security, it is recommended that "
             "entering password interactively without using this parameter."
    )
    login_parser.add_argument("-i", "--isp", choices=['telecom', 'cmcc', 'unicom'],
                              help="Your ISP name. Optional: telecom | cmcc | unicom")
    login_parser.add_argument(
        "-P", "--platform", choices=['0', 'pc', '1', 'mobile'],
        help="The platform that to log in to. Optional: 0/pc | 1/mobile"
    )
    login_parser.add_argument(
        "-c", "--config", help="Using config file instead of cli params. "
                               "Default: ~/.config/cqupt-internet.toml and ./config.toml"
    )
    login_parser.add_argument(
        "-k", "--keep", action='store_true', help="Keep the system logged in to CQUPT Internet."
    )
    login_parser.add_argument(
        "--interval", type=int, default=60, help="Interval seconds when keeping logged status. Default: 60"
    )

    # logout操作
    subparsers.add_parser("logout", help="Logout from CQUPT Internet.")

    # status操作
    subparsers.add_parser("status", help="Show login status.")

    return parser.parse_args()


def __print_info(info: dict, print_msg: bool = False, platform: str = ''):
    """
    按需输出信息
    :param info: 待输出的信息字典
    :param print_msg: 是否输出msg并缩进其余内容
    :param platform: 平台信息，留空则不输出，可选 电脑端:``0``/``pc`` 手机端:``1``/``mobile``
    """
    text = f'{info['msg']}\n' if print_msg else ''
    tab = '\t' if print_msg else ''
    text += f'{tab}Is logged in: {info["is_logged_in"]}\n'
    text += f'{tab}Account: {info["account"]}\n'
    if platform:
        if platform == '0':
            platform = 'PC'
        elif platform == '1':
            platform = 'Mobile'
        else:
            raise ValueError(f'Unknown platform: {platform}')
        text += f'{tab}Platform: {platform}\n'
    text += f'{tab}ISP: {info["isp"].title()}\n'
    text += f'{tab}IP: {info["ip"]}\n'
    text += f'{tab}MAC: {info["mac"]}'
    print(text)


if __name__ == "__main__":
    args = parse_args()

    if args.action == "login":
        # 默认配置
        user_config = {
            'account': None,
            'password': None,
            'isp': None,
            'platform': '0'
        }

        # 读取配置文件
        # 用户指定了配置文件，则读取并覆盖默认配置
        if args.config:
            if os.path.exists(args.config) and os.path.isfile(args.config):
                with open(args.config, 'r', encoding='utf-8') as f:
                    loaded_user_config = toml.load(f)
                user_config.update(loaded_user_config)
            else:
                print(f'Config file `{args.config}` not found.')
                exit(1)
        # 否则尝试读取~/.config/cqupt-internet.toml
        elif (os.path.exists(os.path.expanduser('~/.config/cqupt-internet.toml')) and
              os.path.isfile(os.path.expanduser('~/.config/cqupt-internet.toml'))):
            with open(os.path.expanduser('~/.config/cqupt-internet.toml'), 'r', encoding='utf-8') as f:
                loaded_user_config = toml.load(f)
            user_config.update(loaded_user_config)

        # 否则尝试读取安装目录的./config.toml
        elif os.path.exists(__installed_config_path) and os.path.isfile(__installed_config_path):
            with open(__installed_config_path, 'r', encoding='utf-8') as f:
                loaded_user_config = toml.load(f)
            user_config.update(loaded_user_config)

        # 解析命令行传入的配置，覆盖已有配置
        if args.account:
            user_config['account'] = args.account
        if args.password:
            user_config['password'] = args.password
        if args.isp:
            user_config['isp'] = args.isp
        if args.platform:
            user_config['platform'] = args.platform

        # 检查缺失的参数
        assert user_config['account'], 'Account required.'
        if not user_config['password']:
            user_config['password'] = getpass.getpass('Password: ')
        assert user_config['isp'], 'ISP required.'

        # 登录
        __already_logged_in = cqupt_internet.get_status()['is_logged_in']  # 临时修复已登录时platform显示错误的问题
        if not args.keep:
            _, info_login = cqupt_internet.login(
                account=user_config['account'],
                password=user_config['password'],
                isp=user_config['isp'],
                platform=user_config['platform']
            )
            if __already_logged_in:
                __print_info(info_login, print_msg=True)
            else:
                __print_info(info_login, print_msg=True, platform=user_config['platform'])
        else:
            print(f'Now keeping the system logged in to CQUPT Internet. Interval: {args.interval} seconds.')
            while True:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Checking...')
                _, info_login = cqupt_internet.login(
                    account=user_config['account'],
                    password=user_config['password'],
                    isp=user_config['isp'],
                    platform=user_config['platform']
                )
                if __already_logged_in:
                    __print_info(info_login, print_msg=True)
                else:
                    __print_info(info_login, print_msg=True, platform=user_config['platform'])
                print()
                time.sleep(args.interval)

    elif args.action == "logout":
        _, info_logout = cqupt_internet.logout()
        __print_info(info_logout, print_msg=True)

    elif args.action == "status":
        info_status = cqupt_internet.get_status()
        __print_info(info_status, print_msg=False)

    else:
        print(f'Unknown action: {args.action}')
        exit(1)
