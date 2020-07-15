import requests
import pathlib
import utils
import time
import math
import bs4
import re
import fileStorage
import client

# 登陆部分
# 下载二维码，以供扫描


def downloadQRCode(uuid):
    image = requests.get(
        "https://open.weixin.qq.com/connect/qrcode/"+uuid)
    print("qr address: ", image.url)
    # print("qr content: ", image.content)
    # with 语句实质是上下文管理。
    # 1、上下文管理协议。包含方法__enter__() 和 __exit__()，支持该协议对象要实现这两个方法。
    # 2、上下文管理器，定义执行with语句时要建立的运行时上下文，负责执行with语句块上下文中的进入与退出操作。
    # 3、进入上下文的时候执行__enter__方法，如果设置as var语句，var变量接受__enter__()方法返回值。
    # 4、如果运行时发生了异常，就退出上下文管理器。调用管理器__exit__方法。
    with open("./qr_code.png", "wb") as f:
        f.write(image.content)
        f.close()


# 根据页面获取二维码的uuid
def getQRConnectIfream():
    response = requests.get("https://open.weixin.qq.com/connect/qrconnect?appid=wx5cb34fe58d130615&scope=snsapi_login&redirect_uri=https%3A%2F%2Fa.weixin.qq.com%2Findex.html&state=test&login_type=jssdk&self_redirect=default&styletype=&sizetype=&bgcolor=&rst=&href=https://wximg.qq.com/wxp/assets/css/agencyweb_login_v2.css")
    print("url:", response.url)
    # 使用BeautifulSoup解析代码,并锁定页码指定标签内容
    content = bs4.BeautifulSoup(response.text, "html.parser")
    element = content.find("img", attrs={
        "class": "qrcode-image js_qr_img"
    })
    element = str(element)
    uuid = re.search(r'src="(.+)"', element).group(1)
    uuid = uuid.split("/")
    # 取出第三个
    uuid = uuid[3]
    print(uuid)

    currentTime = math.ceil(time.time() * 1000)
    getQRConnect(uuid, currentTime)

# hasLast为false标识扫码前
# 为true标识扫码结果，成功后会返回wx_code，利用wx_code来做登陆操作


def getQRConnect(uuid, time, hasLast=False):
    params = {
        "uuid": uuid,
        "_": time
    }
    # 第二次调用时需要传入last
    if hasLast:
        params["last"] = "404"
        params["_"] += 1
    else:
        downloadQRCode(params["uuid"])

    response = requests.get(
        "https://lp.open.weixin.qq.com/connect/l/qrconnect", params=params)
    response.encoding = 'utf-8'
    print("扫码中", hasLast, response.text)

    if hasLast == False:
        # 如果wx_errcode为408，表示超时未扫码，需要重新请求该接口,并中断后续执行
        wx_errcode = re.search(r'wx_errcode=(\d+);', response.text)
        wx_errcode = wx_errcode.group(1)
        print("wx_errcode", wx_errcode, wx_errcode == "408")
        if wx_errcode == "408":
            getQRConnect(uuid, time)
        elif wx_errcode == "404":
            getQRConnect(uuid, time, True)
    else:
        code = re.search(r'wx_code=\'(.+)\'', response.text)
        code = code.group(1)
        print(code)
        getCookieByCode(code)


def getCookieByCode(code):
    response = requests.request("POST", "https://a.weixin.qq.com/cgi-bin/agency/login_auth", files={
        "code": (None, code)
    })

    # cookies
    # <RequestsCookieJar[
    # <Cookie ADUSER_OPEN_ID=oQiT2t2vUfwft9EbaE5S11nE-KJc for .a.weixin.qq.com/>,
    # <Cookie MMAD_TICKET=Uk+w0a22KvxbZl/nm+3a7U6urD0A9VkYaclmY2m+RuVkmcFn58M/sXuEKtMazPUoBFNS8RX6ssc= for .a.weixin.qq.com/>,
    # <Cookie MM_TICKET=LQYgss36+UYi25skjRzEYXD1RBbv8HYGHwQWF5t9jDQlI49p/jGS7VNzJISQMxUIqsWNC9c3bxuMQ7BrANNEEg== for .a.weixin.qq.com/>,
    # <Cookie agency_id=spid96eae64364 for .a.weixin.qq.com/>,
    # <Cookie data_bizuin=2021306821 for .a.weixin.qq.com/>,
    # <Cookie data_ticket=xfja39WVbCZzKq5NR7N4Lu4qivHYT3q45Jd4LtB8f3wOvYK8qjeBafI7FfJVrvn5 for .a.weixin.qq.com/>,
    # <Cookie headimgurl=http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLyqNCfTibibKTTbBwTDB1Tx3sAdt1vFdDskCG7MibVyNiaMp7ruFk02uJqOsqic8oGnAkVW5QcFVIx1Bg/132 for .a.weixin.qq.com/>,
    # <Cookie nick_name=%E5%B0%8FBug%E4%BB%96%E7%88%B9 for .a.weixin.qq.com/>
    # ]>

    # content
    # {"agency_id":"spid96eae64364","err":"OK","result":0,"ret":0,"review_status":1,"role":2}

    print("headers:", response.headers)
    print("content:", response.text)

    for name, value in response.cookies.items():
        print("item: ", name, value)
        fileStorage.GLOBAL_COOKIE[name] = value
        if name == "MMAD_TICKET":
            fileStorage.GLOBAL_G_TK = utils.transformTicketToGTK(value)
    fileStorage.setStorage("cookies", fileStorage.GLOBAL_COOKIE)
    fileStorage.setStorage("g_tk", fileStorage.GLOBAL_G_TK)
    client.getDeliveryMetrics()
