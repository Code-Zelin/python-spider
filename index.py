import json
import login
import fileStorage
import client


# 项目由此进入
def entry():
    # 首先读取缓存，看看是否有数据
    _g_tk = fileStorage.getStorage("g_tk")
    _cookies = fileStorage.getStorage("cookies")
    # 如果没有缓存的g_tk，则去走登陆
    if _g_tk == None and _cookies == None:
        login.getQRConnectIfream()
    else:
        fileStorage.GLOBAL_G_TK = _g_tk
        fileStorage.GLOBAL_COOKIE = _cookies
        client.getDeliveryMetrics()
    exitProgram()


def exitProgram():
    print("输入exit退出")
    str = input()
    if str == "exit":
        print("再见")


entry()