# Auto_Checkin_GlaDOS
GlaDOS自动签到脚本
本脚本采用selelium模块，自动获取邮箱最新一封邮件并转化为字符串，然后提取验证码，在windows中设置定时任务可每天隐式运行。
需要在运行环境下添加Chromedriver.exe，具体版本根据Chrome的版本下载对应的Chromedriver.exe，并将其放在python解释器同一个目录下。
chromrdriver.exe下载地址：https://sites.google.com/chromium.org/driver/home

在EMAIL中填入邮箱,PASSWORD中填入密码。默认是QQ邮箱，如果是126或者别的修改一下后面的pop3服务器即可（不同邮箱的服务器可自行百度）。
