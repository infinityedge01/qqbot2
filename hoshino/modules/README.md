# ClanBattleReport——公会战报告书

<img align="right" src="https://i.loli.net/2020/10/26/V8oPbpZSUrLkTmK.png" alt="logo" width="96px" />

<p align="left">
<a href='https://github.com/pcrbot/yobot'><img src="https://img.shields.io/badge/yobot-v3.0-brightgreen.svg"/></a>
<a href='https://github.com/Ice-Cirno/HoshinoBot'><img src="https://img.shields.io/badge/HoshinoBot-v2.0-green.svg"/></a>
<a href='https://github.com/A-kirami/ClanBattleReport/blob/master/LICENSE'><img src="https://img.shields.io/github/license/A-kirami/ClanBattleReport"/></a>
<a href='https://github.com/A-kirami/ClanBattleReport/'><img src="https://img.shields.io/github/stars/A-kirami/ClanBattleReport"/></a>
<a href='https://github.com/A-kirami/ClanBattleReport/releases'><img src="https://img.shields.io/github/downloads/A-kirami/ClanBattleReport/total"/></a>
</p>

本项目为使用本地Yobot数据生成公会战报告书的HoshinoBot V2插件

## 目录
- [开始](https://github.com/A-kirami/ClanBattleReport/#开始)
  - [下载](https://github.com/A-kirami/ClanBattleReport/#下载)
  - [安装](https://github.com/A-kirami/ClanBattleReport/#安装)
  - [使用](https://github.com/A-kirami/ClanBattleReport/#使用)
- [贡献](https://github.com/A-kirami/ClanBattleReport/#贡献)
- [相关](https://github.com/A-kirami/ClanBattleReport/#相关)

## 开始

### 下载
请前往[Releases](https://github.com/A-kirami/ClanBattleReport/releases)下载最新版本

### 安装
1. 将``clanbattlereport``文件夹放入``hoshino``的``modules``文件夹
2. 为插件安装依赖：

      ```
      pip install -r requirements.txt
      ```

3. 为``matplotlib``安装中文字体：  
      [Windows系统] 双击字体文件安装  
      [Linux系统] 使用``pip show matplotlib``找到``matplotlib``的安装位置，并将字体文件复制到``matplotlib/mpl_data``的``font目录``下
4. 复制``clanbattlereport.example``到``config``文件夹，重命名为``clanbattlereport.py``，打开后按照注释进行配置
5. 修改``_bot_.py``，在``MODULES_ON``中添加``clanbattlereport``
6. 重启HoshinoBot

### 使用
使用前请确认yobot的API访问已开启（默认开启，如果你关闭了api访问，请重新启用）

**生成离职报告**：生成自己的离职报告书

**生成会战报告**：生成自己的本期会战报告书

**看看报告@某人**：查看他人的会战报告书（需要群管理权限）

## 贡献
- [@mahosho](https://github.com/mahosho)
- [@shewinder](https://github.com/shewinder)
- [@corvo007](https://github.com/corvo007)

## 相关
- [ClanBattleReport-Origin](https://github.com/A-kirami/ClanBattleReport-Origin) - 旧版公会战报告书
- [clanbattle_report](https://github.com/zyujs/clanbattle_report) - 使用Yobot API数据生成离职报告和会战报告的HoshinoBot插件,由用户自行指定API地址,可使用任意远程服务器的Yobot数据生成报告
