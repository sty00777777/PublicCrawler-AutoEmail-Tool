from ContentSpider_AutoSending import Spider_Sender

# 在此输入需要发送的对象邮箱
receivers = ["xxxxxxxxxxx","xxxxxxxxxxx"]

# 创造对象实例
spider_sender = Spider_Sender(receivers)

spider_sender.login()

# 在此输入需要爬取的公众号的名称
official_account_list = ['xxxxxxxxxxx','xxxxxxxx','xxxxxxxxx','xxxxxxxxx']

# 循环爬去列表内的公众号内容
for i in official_account_list: 

    spider_sender.get_article(i)

# 对存储结果进行自动发送
spider_sender.auto_sending()    