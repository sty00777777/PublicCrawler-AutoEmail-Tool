## Read me

### 1.项目介绍

本爬虫主要用于爬取公众号内容，并且将爬取内容自动发送至指定邮箱，具体实现逻辑为以下：

1. 利用selenium通过公众号创作平台的个人token等参数+抓包（此处需要人为扫码），通过超链接，获得某公众号的永久URL(一般公众号的url会是随机生成的，所以无法准确定位)，再利用requests库对获取的URL进行解析，提取其中文字内容，存储到csv文件，其中包含5个字段：NAME CREATE_TIME TITLE CONTENT URL。
2. 通过email库自动发送邮件+附件至指定联系人。

该项目的优点主要在于将爬虫和自动发送二者融合到了一起，降低了整合的难度，将具体细节封装在类文件里，可以不用反复改变其中的细节，主程序只包含最关键的参数，如发送至的指定邮箱地址和需要爬取的公众号名称。使用时可每天一爬并发送。

### 2.使用说明

该项目有一个类 ContentSpider_AutoSending.py 文件和一个调用主程序 Main.py 文件，在使用前需要定义以下参数：

1. 在 Main.py 中输入被发送者的邮箱，以及具体公众号的名字。

2. 在具体的类文件 ContentSpider_AutoSending.py 中的\_init\_里面输入自己的发送人邮箱和授权码（具体操作可自行搜索或参考最下方链接），并且可以更改爬文章的限定条件（如只想爬今天一天的，就对时间添加 if 限定，如只想爬最近五条，就限定输入的数量，可以进行细节修改）。

编辑器工作环境在总体的项目大文件夹中（包含code和data文件夹）。

​	$\bullet$  注意，csv文件中的create_time和实际发送的时间有所差别，一般是create_time之后一小时才会在公众号上发布，个人感觉可能是上传后需要审核，有一个时间差，不过这个时间差不会很长，一般不会跨过一天，所以仅用日期定位筛选的话可以放心使用。

​	$\bullet$ 目前，文件夹data中包含一份已经爬好的数据，方便读者了解爬去内容的细节

### 3.参考URL：

https://zhuanlan.zhihu.com/p/379062852

https://www.apispace.com/news/post/53183.html

https://www.zhihu.com/tardis/zm/art/89868804?source_id=1003

https://www.runoob.com/python/python-email.html

https://blog.csdn.net/weixin_44827418/article/details/111255414（授权码详情）

https://news.sangniao.com/p/2166408457
