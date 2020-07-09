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


# entry()


def transfromJson():
    result = {}
    with open("./index_classify_info.json", "r", encoding="utf-8") as read_f:
        data = json.load(read_f)
    for item in data:
        for inner in item["indexList"]:
            result[inner['db_name']] = {
                "name": inner["index_name"],
                "desc": inner["index_description"],
                "ad_level": inner["for_ad_level"]
            }

    with open("./info.json", "w", encoding="utf-8") as write_f:
        json.dump(result, write_f, ensure_ascii=False)


transfromJson()
