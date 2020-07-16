import fileStorage
import requests
import time
import utils
import math
import json
import login
import config
import http
import re
import os
from urllib.parse import quote


# cgi-bin/agency/get_delivery_metrics
def getDeliveryMetrics():
    response = requests.get("https://a.weixin.qq.com/cgi-bin/agency/get_delivery_metrics", {
        "page": 1,
        "page_size": 30,
        "search_key": "",
        "order_by": "",
        "ascending": 1,
        "only_collect": 0,
        "g_tk": fileStorage.GLOBAL_G_TK,
        "_": math.ceil(time.time() * 1000)
    }, headers={
        "Cookie": utils.transfomrCookie(fileStorage.GLOBAL_COOKIE)
    })
    print('d url:', response.url)
    print("d content", response.text)
    responseData = json.loads(response.text)
    # 如果responseData的ret不是0的话，说明g_tk和cookie失效了，需要重新登录
    if responseData.get("ret") != 0:
        print("g_tk和cookie失效，请重新扫码登录")
        login.getQRConnectIfream()
    else:
        callInterfaceWithFn()


# 调用接口，获取需要爬取的数据，并执行传入的方法
def callInterfaceWithFn():
    responseData = requests.get(config.HOST + "/ad/get")
    resList = json.loads(responseData.text)

    for index in range(len(resList)):
        item = resList[index]
        # date【max】格式为20201207 YYYYMMDD
        # 这里需要判断是否有mp_cookies和token，如果有，可以直接进行下一步
        print("项目信息：", item)
        appid = item["appid"]
        storage = fileStorage.getStorage(appid)
        if storage != None:
            mp_cookies = storage["mp_cookies"]
            token = storage["token"]
            if mp_cookies != None and token != None:
                # 重定向
                # 微信广告的逻辑是，跳转到A接口，A接口返回的headers中的Location是下次跳转的路径
                # 反复两次，到https://mp.weixin.qq.com/promotion/splogin
                # 这次请求会返回真正的地址，以及真地址的cookies，并且可以从真地址上取到token的值
                getKeyDetailTable(item["appid"], item["max"], item["is_game"])
        else:
            redirectMp(item["appid"], item["max"], item["is_game"])


# 重定向到wechat mp的地址，带上appid
def redirectMp(appid, date, is_game):
    params = {
        "appid": appid,
        "g_tk": fileStorage.GLOBAL_G_TK,
        "mgr_type": 1
    }
    url = "http://a.weixin.qq.com/cgi-bin/agency/redirect_mp?" + \
        utils.arrJoinStr(utils.transformObjToArr(params), "&")
    openMpPage(url, appid, date, is_game)


# 打开资料页面，获取cookie信息，用于后续的接口调用
def openMpPage(url, appid, date, is_game):
    response = requests.get(url, headers={
        "Cookie": utils.transfomrCookie(fileStorage.GLOBAL_COOKIE)
    }, allow_redirects=False)
    print("mppage: ", response.url)
    location = response.headers["Location"]
    _cookies = response.cookies.items()
    if len(_cookies) > 0:
        storage = {}
        # 从location中获取token
        token = re.search(r'token=(\d+)', location)

        # 加这个判断是因为有可能有个连接会出现set-cookie，但是这个连接不是目标连接，也就是这些cookie是假的
        # 假的连接里面是没有token字段的，会导致后面出错
        if not token:
            openMpPage(location, appid, date, is_game)
            return
        token = token.group(1)
        print("token: ", token)

        storage["token"] = token
        # 从headers的set-cookies中获取mp.weixin.qq.com的cookie，并存入缓存中
        mp_cookies = {}
        for name, value in _cookies:
            mp_cookies[name] = value or ""

        storage["mp_cookies"] = mp_cookies
        fileStorage.setStorage(appid, storage)
        getKeyDetailTable(appid, date, is_game)
    else:
        openMpPage(location, appid, date, is_game)


# 获取具体的数据详情
# date为日期
def getKeyDetailTable(appid, date=-1, is_game=1):
    print("开始请求数据", appid, date, is_game)
    if date == -1:
        startTime = str(utils.getTimeStampFromFewDaysAgo(1))
    if date == 0:
        # 如果没有起始日期，则从2020年5月1号开始爬取
        startTime = "1588262400"
    else:
        startTime = utils.dateToTimeStamp(str(date))

    endTime = str(utils.getTimeStampFromFewDaysAgo(1, False))

    storage = fileStorage.getStorage(appid)
    token = storage["token"]
    # 这里需要的是毫秒
    currentTime = str(math.ceil(time.time() * 1000))
    dimension = "2"
    if not is_game:
        dimension = "3"

    cookie = utils.transfomrCookie(storage["mp_cookies"])
    _url = "https://mp.weixin.qq.com/promotion/as_rock?action=get_ads_report&args=%7B%22condition%22%3A%7B%22report_type%22%3A1%2C%22dimension%22%3A"+dimension+"%2C%22pos_type%22%3A1000%7D%2C%22query_index%22%3A%22%5B%5C%22cname%5C%22%2C%5C%22exposure_score%5C%22%2C%5C%22material_preview%5C%22%2C%5C%22budget%5C%22%2C%5C%22bid%5C%22%2C%5C%22paid%5C%22%2C%5C%22conv_index%5C%22%2C%5C%22conv_index_cpa%5C%22%2C%5C%22conv_index_cvr%5C%22%2C%5C%22weapp_start_pv%5C%22%2C%5C%22second_ocpm_cpa%5C%22%2C%5C%22income_from_minigame_reg_arpu%5C%22%2C%5C%22begin_time%5C%22%2C%5C%22end_time%5C%22%2C%5C%22weapp_reg_pv%5C%22%2C%5C%22weapp_reg_cost%5C%22%2C%5C%22weapp_reg_rate%5C%22%2C%5C%22minigame_realization_roi_first_pv%5C%22%2C%5C%22weapp_purchase_pv%5C%22%2C%5C%22weapp_purchase_amount%5C%22%2C%5C%22weapp_purchase_firstday_pv%5C%22%2C%5C%22weapp_purchase_firstday_amount%5C%22%2C%5C%22weapp_purchase_amount_roi%5C%22%2C%5C%22weapp_purchase_all_dedup_pv%5C%22%2C%5C%22day_budget%5C%22%2C%5C%22bid_action_type%5C%22%2C%5C%22bid_avg%5C%22%2C%5C%22second_bid%5C%22%2C%5C%22bill_second_bid_avg%5C%22%2C%5C%22deep_conversion_bid%5C%22%2C%5C%22exp_pv%5C%22%2C%5C%22ecpm%5C%22%2C%5C%22exp_uv%5C%22%2C%5C%22exp_pv_avg%5C%22%2C%5C%22clk_pv%5C%22%2C%5C%22clk_uv%5C%22%2C%5C%22ctr%5C%22%2C%5C%22cpc%5C%22%2C%5C%22comindex_name%5C%22%2C%5C%22second_comindex_name%5C%22%2C%5C%22second_ocpm_comindex%5C%22%2C%5C%22second_ocpm_cvr%5C%22%2C%5C%22exp_pv%5C%22%2C%5C%22clk_pv%5C%22%2C%5C%22ctr%5C%22%2C%5C%22comindex%5C%22%2C%5C%22cpc%5C%22%2C%5C%22paid%5C%22%2C%5C%22conv_index%5C%22%2C%5C%22conv_index_cpa%5C%22%5D%22%2C%22begin_time%22%3A"+startTime+"%2C%22end_time%22%3A"+endTime+"%7D&token="+token+"&appid="+appid+"&spid=&_="+currentTime
    response = requests.get(_url, headers={
        "Cookie": cookie
    })
    # print("table url: ", response.url)
    # print("table cookie: ", cookie)
    print("准备写入: ", appid)

    responseData = json.loads(response.text)

    if responseData.get("ret") != 0:
        redirectMp(appid, date, is_game)
    else:
        responseData["appid"] = appid
        res = requests.post(config.HOST + "/ad/add", json.dumps(responseData), headers={
            "content-type": "application/json"
        })
        print("本地请求： ", res.text)
        if os.path.isdir("./data") == False:
            os.mkdir("data")
        with open("./data/" + appid + ".json", "w", encoding="utf-8") as f:
            json.dump(responseData, f, ensure_ascii=False)
