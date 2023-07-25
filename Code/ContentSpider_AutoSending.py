import re
import time
import random
import traceback
import requests
from selenium import webdriver
import csv
import os
from lxml import etree
import smtplib
import string
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.application import MIMEApplication # 用于添加附件
from datetime import datetime


class Spider_Sender(object):

    '''
    微信公众号文章内容自动爬虫并发送
    '''


    def __init__(self,receiver):

        '''
        初始化最初参数
        '''
        
        # 用于爬虫的信息

        self.date = datetime.now().date()

        self.cookies = ''
        
        # 用于存储文件的信息

        self.headers = {
    
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, \
            like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
        
        self.page_num = 1 # 在这里选择要爬多少页
        
        self.csv_file_name = "content_tracking_" + str(self.date) + ".csv" # 定义CSV文件的名称

        self.csv_file = "Data/content_tracking_" + str(self.date) + ".csv" # 定义CSV文件的相对路径（相对于爬虫总文件夹）

        # 用于发送邮件的信息

        self.host_server = 'smtp.qq.com'  # qq邮箱smtp服务器

        self.sender_qq = 'xxxxxxxxxx' # 发件人邮箱

        self.pwd = 'xxxxxxxxxx' # 发件人邮箱的授权吗

        self.receiver = receiver # 收件人邮箱,并列用逗号隔开

        self.mail_title = str(self.date) + ' 舆情追踪' # 邮件标题

        self.mail_content = "您好，这是日期为 " + str(self.date) + " 的舆情追踪，请您查收" # 邮件正文内容


    def create_driver(self):

        '''
        初始化 webdriver, 利用selenium模拟
        '''

        options = webdriver.ChromeOptions()

        # 禁用gpu加速，防止出一些未知bug
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(options=options)

        # 设置一个隐性等待 5s
        self.driver.implicitly_wait(5)


    def log(self, msg):

        '''
        格式化打印
        '''

        print('------ %s ------' % msg)


    def login(self):

        '''
        登录拿 cookies
        '''

        try:
        
            self.create_driver()

        # 访问微信公众平台
            self.driver.get('https://mp.weixin.qq.com/')

        # 等待网页加载完毕
            time.sleep(3)

        # 扫码登录
            self.log("请拿手机扫码二维码登录公众号")

        # 等待手机扫描
            time.sleep(10)

            self.log("登录成功")

        # 获取cookies 然后保存到变量上，后面要用
            self.cookies = dict([[x['name'], x['value']] for x in self.driver.get_cookies()])

        except Exception as e:
        
            traceback.print_exc()

        finally:

        # 退出 chorme
            self.driver.quit()


    def save_to_csv(self,data_list):

        '''
        存储csv文件至本地
        '''

        # 如果CSV文件已存在，以附加模式打开；否则，以写入模式创建新文件
        mode = 'a' if os.path.exists(self.csv_file) else 'w'

        # 写入数据到CSV文件
        with open(self.csv_file, mode, newline='', encoding='utf-8') as file:

            fieldnames = ['Name', 'Create_Time', 'Title', 'Content', 'URL']

            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # 如果是新文件，则写入表头
            if mode == 'w':

                writer.writeheader()

            # 写入数据行
            for data in data_list:

                writer.writerow(data)


    def parse_url(self, url):   

        '''
        对目标url发送请求，获取响应html
        '''

        # print(url)

        response = requests.get(url, headers=self.headers)

        return response.content.decode()



    def get_content_list(self,html_str):    

        '''
        提取公众号中的文字内容
        '''

        html = etree.HTML(html_str)

        content_list = []

        item = {}

        item["other"] = html.xpath("//*[@id=\"js_content\"]//text()") # 提取文章内容
        
        content_list.append(item)

        return content_list


    def get_article(self, query=''):  

        '''
        登陆个人公众号账户，通过抓包获取token信息，得到公众号原URL链接，否则得到的是乱码，没办法定位url
        '''

        try:

            url = 'https://mp.weixin.qq.com'

        # 设置headers
            headers = {

            "HOST": "mp.weixin.qq.com",

            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"

            }

        # 登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=325031676

        # 从这里获取token信息
            response = requests.get(url=url, cookies=self.cookies)

            token = re.findall(r'token=(\d+)', str(response.url))[0]

            time.sleep(2)

            self.log('正在查询[ %s ]相关公众号' % query)

            search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

        # 搜索微信公众号接口需要传入的参数，

        # 有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
            params = {

            'action': 'search_biz',

            'token': token,

            'random': random.random(),

            'query': query,

            'lang': 'zh_CN',

            'f': 'json',

            'ajax': '1',

            'begin': '0',

            'count': '5'

            }

        # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
            response = requests.get(search_url, cookies=self.cookies, headers=headers, params=params)

            time.sleep(2)

        # 取搜索结果中的第一个公众号
            lists = response.json().get('list')[0]

        # 获取这个公众号的fakeid，后面爬取公众号文章需要此字段
            fakeid = lists.get('fakeid')

            nickname = lists.get('nickname')

        # 微信公众号文章接口地址
            search_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'

        # 搜索文章需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
            params = {

            'action': 'list_ex',

            'token': token,

            'random': random.random(),

            'fakeid': fakeid,

            'lang': 'zh_CN',

            'f': 'json',

            'ajax': '1',

            'begin': '0', # 不同页，此参数变化，变化规则为每页加5

            'count': '5',

            'query': '',

            'type': '9'

            }

            self.log('正在查询公众号[ %s ]相关文章' % nickname)

        # 打开搜索的微信公众号文章列表页

            for j in range(self.page_num):  

                params["begin"] = j*5

                time.sleep(5)


                response = requests.get(search_url, cookies=self.cookies, headers=headers, params=params)

                time.sleep(2)

                for per in response.json().get('app_msg_list', []):
                    
                    print('******************************************************') # 分割线，好看

                    title = per.get('title')
                    print('title --- %s' % title)

                    link = per.get('link')
                    # print('link --- %s' % link)

                    t = time.localtime(per.get('create_time'))

                    create_time = time.strftime("%Y-%m-%d %H:%M:%S",t)  # 发布时间转换

                    print('create_time --- %s' % create_time)

                    html_str = self.parse_url(link)

                    content_list = self.get_content_list(html_str)

                    content = ''.join(content_list[0]["other"])

                    data_list = [
                        {'Name': query, 'Create_Time': create_time ,'Title': title, 'Content': content, 'URL': link},
                    ]

                    # 调用函数将数据保存到CSV文件
                    self.save_to_csv(data_list)

        # print('cover --- %s' % per.get('cover'))

        except Exception as e:

            traceback.print_exc()


    def message_content_setting(self):

        '''
        创建邮箱本身实例
        '''

        msg = MIMEMultipart()

        # 设置邮件头部内容
        msg["Subject"] = Header(self.mail_title,'utf-8')

        msg["From"] = self.sender_qq

        msg['To'] = ','.join(self.receiver)

        msg.attach(MIMEText(self.mail_content,'plain', 'utf-8')) # 附上邮件正文

        # 添加附件
        attachment = MIMEApplication(open(self.csv_file,'rb').read())

        # 给附件重命名
        basename = self.csv_file_name

        attachment.add_header('Content-Disposition', 'attachment', filename=('gbk', '', basename)) # 注意不要拼错，应该是disposition

        msg.attach(attachment)

        return msg


    def auto_sending(self):
        
        '''
        内容设置完毕，连接服务器并发送
        '''
        
        try:
            smtp = SMTP_SSL(self.host_server) # ssl登录连接到邮件服务器

            smtp.set_debuglevel(1) # 0是关闭，1是开启debug

            smtp.ehlo(self.host_server) # 跟服务器打招呼，告诉它我们准备连接，最好加上这行代码

            smtp.login(self.sender_qq,self.pwd)

            smtp.sendmail(self.sender_qq,self.receiver,self.message_content_setting().as_string())

            smtp.quit()

            print("邮件发送成功")

        except smtplib.SMTPException:

            print("无法发送邮件")
