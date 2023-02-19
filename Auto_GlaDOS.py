# 用于GlaDOS自动签到获取流量

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from lxml import etree
import time
import poplib

EMAIL = "邮箱"         # input('Email: ')
PASSWORD = "授权码"       # input('Password: ')

url = 'https://glados.rocks/console/checkin'
# 浏览器启动选项
option = webdriver.ChromeOptions()
# 指定为无界面模式
option.add_argument('--headless')
# option.headless=True  或者将上面的语句换成这条亦可
# 创建Chrome驱动程序的实例
browser = webdriver.Chrome(options=option)

browser.get(url)

browser.find_element(By.LINK_TEXT, 'Login').click()
browser.find_element(By.XPATH, '//button[contains(text(),"Login")]').click()
browser.find_element(By.ID, 'email').send_keys(EMAIL)
browser.find_element(By.XPATH, '//button[contains(text(),"send access code to email")]').click()  # 发送验证码
time.sleep(10)

# 输入邮件地址, 口令和POP3服务器地址:
email = EMAIL
password = PASSWORD
pop3_server = 'pop.qq.com'  # input('POP3 server: ')    # pop3服务器，可根据不同邮箱自行修改
result = ""


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def print_info(msg, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s%s: %s' % ('  ' * indent, header, value))
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            print('%spart %s' % ('  ' * indent, n))
            print('%s--------------------' % ('  ' * indent))
            print_info(part, indent + 1)
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                content = content.decode(charset)
            print('%sText: %s' % ('  ' * indent, content + '...'))
            global result
            result = content
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))


def get_content():
    # 连接到POP3服务器:
    server = poplib.POP3(pop3_server)
    # 可以打开或关闭调试信息:
    server.set_debuglevel(1)
    # 可选:打印POP3服务器的欢迎文字:
    # print(server.getwelcome().decode('utf-8'))
    # 身份认证:
    server.user(email)
    server.pass_(password)
    # stat()返回邮件数量和占用空间:
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    # print(mails)
    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    resp, lines, octets = server.retr(index)
    # lines存储了邮件的原始文本的每一行,
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)
    print_info(msg)
    # 可以根据邮件索引号直接从服务器删除邮件:
    # server.dele(index)
    # 关闭连接:
    server.quit()
    return result


if __name__ == '__main__':
    result = get_content()
    # print(result)


def parser_str(str=''):
    html = etree.HTML(result, etree.HTMLParser())
    result2 = html.xpath("//b[@style]//text()")
    return result2[0]


validation_code = parser_str(result)

browser.find_element(By.ID, 'mailcode').send_keys(validation_code)
browser.find_element(By.XPATH, '/html/body/div/div/div/div[2]/div/form/div[3]/span/button').click()  # login
time.sleep(5)
browser.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div[2]/div/div/div[4]/div[4]/div/div').click()
browser.find_element(By.XPATH, '/html/body/div/div/div/div/div[2]/div[2]/div/div[2]/button').click()  # 签到
browser.quit()
