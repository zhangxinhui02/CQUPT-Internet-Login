# CQUPT Internet Login

一个CLI工具/守护服务，用于登录/注销/查看/保持登录重邮校园网宽带账号，支持Windows/Linux。也可以作为Python模块使用。

---

## CLI使用方法

可以通过`cqupt-internet -h`和`cqupt-internet login -h`命令了解命令详细参数和简写flag。

### 1. 查看登录状态

```shell
cqupt-internet status
```

### 2. 退出宽带登录

```shell
cqupt-internet logout
```

### 3. 登录宽带

登录命令拥有丰富的可配置参数，这里列出一些常用命令示例。详细参数可以通过`cqupt-internet login -h`命令了解。

```shell
# 在命令行参数中指定登录信息，并在之后输入密码
cqupt-internet login --account <统一认证码> --isp <运营商 telecom | cmcc | unicom> --platform <登录到的平台(默认为pc) pc/0 | mobile/1>
# eg: cqupt-internet login --account 1000000 --isp telecom --platform pc 

# 在命令行参数中指定登录信息和密码（不推荐，会泄露密码到命令行历史记录）
cqupt-internet login --account <统一认证码> --password <密码> --isp <运营商 telecom | cmcc | unicom> --platform <登录到的平台(默认为pc) pc/0 | mobile/1>
# eg: cqupt-internet login --account 1000000 --password xxx --isp telecom --platform pc 

# 在命令行参数中指定登录信息，并保持登录，随后程序会持续运行并轮询登录
cqupt-internet login --account <统一认证码> --isp <运营商 telecom | cmcc | unicom> --platform <登录到的平台(默认为pc) pc/0 | mobile/1> --keep --interval <轮询秒数(默认为60)>
# eg: cqupt-internet login --account 1000000 --isp telecom --platform pc --keep --interval 120
```

也可以通过配置文件指定登录信息，简化命令行操作。程序登录时的登录信息会从四处获取，优先级从高到低是：

- 命令行参数
- 用户在命令行通过`--config`参数指定的配置文件路径
- 用户目录中的配置文件：`~/.config/cqupt-internet.toml`
- 安装目录中的配置文件：`config.toml`

你可以提供其中一个配置文件（格式参考安装目录中的配置文件`config.toml`），之后就可以简化登录流程：

```shell
cqupt-internet login  # 程序自动加载配置文件中的登录信息
```

*对专业用户的使用提示：程序会从后三种方式中选择第一个存在的配置文件并加载，然后用命令行参数覆盖已加载的参数，从而得到最终的登录信息。因此你可以只在配置文件中提供一部分信息（例如统一认证码、运营商和登录平台），而在命令行提供另一部分信息（例如密码）。*

## 安装方法

此项目会自动创建隔离Python环境并在隔离环境中运行。安装此项目的前置条件是操作系统已安装Python，并且Python已安装`venv`模块。

按照你的需求，在下面选择一种安装方式。

### 1. 安装为CLI命令

将此项目安装为你的操作系统的命令，以便在命令行上实现快速登录/注销/查看登录状态。

1. 克隆此仓库到你需要安装的位置。**注意，一旦确定安装位置并安装完毕后，就不能移动项目位置，否则会导致脚本找不到主程序。**

   ```shell
   # 进入要安装到的目录，例如：
   # cd /opt
   # cd C:\Programs
   
   git clone https://github.com/zhangxinhui02/CQUPT-Internet-Login.git
   ```

2. 进入项目目录的`scripts`目录，运行安装脚本。**注意运行脚本时的工作目录必须在`scripts`目录内。**

   对于Linux：
   ```shell
   cd CQUPT-Internet-Login/scripts
   sudo chmod +x install.sh
   sudo ./install.sh
   ```
   
   对于Windows：
   ```powershell
   cd CQUPT-Internet-Login\scripts
   .\install.ps1  # 也可以右键install.ps1脚本，使用PowerShell运行
   ```
   
   注意：Windows安装脚本需要提升到管理员身份以进行安装。如果当前shell不是管理员身份，会弹出UAC窗口并从新的shell开始运行。
   
   安装完毕后，对于Windows，需要重启已有的shell以刷新环境变量，才能使用命令。

3. 现在可以从命令行使用`cqupt-internet`命令了。

### 2. 安装为守护服务，保持系统持续登录

将此项目注册为你的操作系统的服务，轮询登录状态并自动登录，以使你的设备保持登录状态，防止掉线。

1. 注册为服务需要先保证命令已成功安装。参照上述步骤安装`cqupt-internet`命令。

2. 需要事先为服务提供登录所需的信息。进入项目主目录，编辑`config.toml`文件，填入你的宽带登录信息。

   *对专业用户的使用提示：如果你想让程序从用户目录中的配置文件`~/.config/cqupt-internet.toml`加载登录信息，但是程序无法获取，这很可能是因为服务不以你当前的用户身份运行。建议将配置写在项目目录中。*

3. 进入项目目录的`scripts`目录，运行安装脚本。**注意运行脚本时的工作目录必须在`scripts`目录内。**

   对于Linux：
   ```shell
   # 脚本会安装名为cqupt-internet-autologin的systemd服务，设置开机自启动并立即启动服务
   cd CQUPT-Internet-Login/scripts
   sudo chmod +x install-service.sh
   sudo ./install-service.sh  # 轮询秒数默认为60，你也可以传入参数手动指定，例如：sudo ./install-service.sh 120
   ```

   对于Windows：
   ```powershell
   # 脚本会安装名为CQUPT-Internet-Autologin的Windows服务，设置开机自启动并立即启动服务
   cd CQUPT-Internet-Login\scripts
   .\install-service.ps1  # 也可以右键install-service.ps1脚本，使用PowerShell运行。轮询秒数默认为60，你也可以传入参数手动指定，例如：.\install-service.ps1 120
   ```

   注意：Windows安装脚本需要提升到管理员身份以进行安装。如果当前shell不是管理员身份，会弹出UAC窗口并从新的shell开始运行。

   注意：Windows平台上的安装脚本需要`nssm`命令以注册服务。当此命令不存在时，安装脚本会尝试自动部署。[kirillkovalenko/nssm](https://github.com/kirillkovalenko/nssm)

4. 安装完毕。使用以下命令管理服务。

   Linux:
   ```shell
   systemctl status cqupt-internet-autologin  # 查看服务状态
   systemctl start cqupt-internet-autologin  # 启动服务
   systemctl stop cqupt-internet-autologin  # 停止服务
   systemctl restart cqupt-internet-autologin  # 重启服务
   systemctl enable cqupt-internet-autologin  # 设置服务自启动
   systemctl disable cqupt-internet-autologin  # 设置服务不要自启动
   journalctl -xeu cqupt-internet-autologin  # 查看服务日志
   ```
   
   Windows:
   ```powershell
   nssm status CQUPT-Internet-Autologin  # 查看服务状态
   nssm start CQUPT-Internet-Autologin  # 启动服务
   nssm stop CQUPT-Internet-Autologin  # 停止服务
   nssm edit CQUPT-Internet-Autologin  # 在图形界面中编辑服务
   # 在安装目录的service-logs目录中可以查看服务的日志。
   # 由于未知原因，在nssm服务中禁用Python输出缓冲会导致服务启动失败，所以目前日志不会实时写入文件，需要停止一次服务才会写入日志。
   ```

### 3. 在你的Python程序中调用此项目

如果你需要实现一些自动化程序，你可以导入此项目的cqupt_internet.py文件，作为模块来调用其中的功能。

一个例子：

```python
import cqupt_internet

ip, mac = cqupt_internet.get_ip_mac()  # 获取出网卡的IP和MAC
status = cqupt_internet.get_status()  # 获取目前的登录状态
result_login, info_login = cqupt_internet.login(  # 登录到重邮宽带
    account='xxx',
    password='xxx',
    isp='telecom',
    platform='pc'
)
result_logout, info_logout = cqupt_internet.logout()  # 注销宽带登录
```

## 干净卸载

如果你需要干净卸载此项目，需要遵循以下流程：

### 对于Windows

1. 如果安装了服务，通过以下命令卸载服务：

   ```powershell
   nssm stop CQUPT-Internet-Autologin
   nssm remove CQUPT-Internet-Autologin
   ```

2. 在系统`PATH`环境变量中移除指向`<项目安装路径>\bin`目录的部分。

3. 删除项目目录。

### 对于Linux

1. 如果安装了服务，通过以下命令移除服务：

   ```shell
   systemctl disable --now cqupt-internet-autologin
   sudo rm -f /etc/systemd/system/cqupt-internet-autologin.service
   systemctl daemon-reload
   ```

2. 删除命令：

   ```shell
   sudo rm -f /usr/bin/cqupt-internet
   ```

3. 删除项目目录。
