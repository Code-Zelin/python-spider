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
        # 这里需要判断是否有mp_cookies和token，如果有，可以直接进行下一步
        mp_cookies = fileStorage.getStorage("mp_cookies")
        token = fileStorage.getStorage("token")
        if mp_cookies != None and token != None:
            # 重定向
            # 微信广告的逻辑是，跳转到A接口，A接口返回的headers中的Location是下次跳转的路径
            # 反复两次，到https://mp.weixin.qq.com/promotion/splogin
            # 这次请求会返回真正的地址，以及真地址的cookies，并且可以从真地址上取到token的值
            getKeyDetailTable()
        else:
            redirectMp()


def redirectMp():
    params = {
        "appid": config.appids.get("qsgdmj"),
        "g_tk": fileStorage.GLOBAL_G_TK,
        "mgr_type": 1
    }
    url = "http://a.weixin.qq.com/cgi-bin/agency/redirect_mp?" + \
        utils.arrJoinStr(utils.transformObjToArr(params), "&")
    openMpPage(url)


def openMpPage(url):
    response = requests.get(url, headers={
        "Cookie": utils.transfomrCookie(fileStorage.GLOBAL_COOKIE)
    }, allow_redirects=False)
    print("mppage", response.url)
    location = response.headers["Location"]
    print("mppage: ", location)

    _cookies = response.cookies.items()
    if len(_cookies) > 0:
        # 从location中获取token
        token = re.search(r'token=(\d+)', location)
        token = token.group(1)
        print("token: ", token)
        fileStorage.setStorage("token", token)

        # 从headers的set-cookies中获取mp.weixin.qq.com的cookie，并存入缓存中
        mp_cookies = {}
        for name, value in _cookies:
            print("mpPage: cookies: ", name, value)
            mp_cookies[name] = value or ""
        fileStorage.setStorage("mp_cookies", mp_cookies)
        getKeyDetailTable()
    else:
        openMpPage(location)


def getKeyDetailTable():
    print("table request")
    startTime = str(utils.getTimeStampFromFewDaysAgo(1))
    endTime = str(utils.getTimeStampFromFewDaysAgo(1, False))
    token = fileStorage.getStorage("token")
    appid = config.appids.get("qsgdmj") or ""
    currentTime = str(math.ceil(time.time()))

    _url = "https://mp.weixin.qq.com/promotion/as_rock?action=get_ads_report&args=%7B%22condition%22%3A%7B%22report_type%22%3A1%2C%22dimension%22%3A2%2C%22pos_type%22%3A1000%7D%2C%22query_index%22%3A%22%5B%5C%22cname%5C%22%2C%5C%22exposure_score%5C%22%2C%5C%22material_preview%5C%22%2C%5C%22budget%5C%22%2C%5C%22bid%5C%22%2C%5C%22paid%5C%22%2C%5C%22conv_index%5C%22%2C%5C%22conv_index_cpa%5C%22%2C%5C%22conv_index_cvr%5C%22%2C%5C%22weapp_start_pv%5C%22%2C%5C%22second_ocpm_cpa%5C%22%2C%5C%22income_from_minigame_reg_arpu%5C%22%2C%5C%22begin_time%5C%22%2C%5C%22end_time%5C%22%2C%5C%22weapp_reg_pv%5C%22%2C%5C%22weapp_reg_cost%5C%22%2C%5C%22weapp_reg_rate%5C%22%2C%5C%22minigame_realization_roi_first_pv%5C%22%2C%5C%22weapp_purchase_pv%5C%22%2C%5C%22weapp_purchase_amount%5C%22%2C%5C%22weapp_purchase_firstday_pv%5C%22%2C%5C%22weapp_purchase_firstday_amount%5C%22%2C%5C%22weapp_purchase_amount_roi%5C%22%2C%5C%22weapp_purchase_all_dedup_pv%5C%22%2C%5C%22day_budget%5C%22%2C%5C%22bid_action_type%5C%22%2C%5C%22bid_avg%5C%22%2C%5C%22second_bid%5C%22%2C%5C%22bill_second_bid_avg%5C%22%2C%5C%22deep_conversion_bid%5C%22%2C%5C%22exp_pv%5C%22%2C%5C%22ecpm%5C%22%2C%5C%22exp_uv%5C%22%2C%5C%22exp_pv_avg%5C%22%2C%5C%22clk_pv%5C%22%2C%5C%22clk_uv%5C%22%2C%5C%22ctr%5C%22%2C%5C%22cpc%5C%22%2C%5C%22comindex_name%5C%22%2C%5C%22second_comindex_name%5C%22%2C%5C%22second_ocpm_comindex%5C%22%2C%5C%22second_ocpm_cvr%5C%22%2C%5C%22exp_pv%5C%22%2C%5C%22clk_pv%5C%22%2C%5C%22ctr%5C%22%2C%5C%22comindex%5C%22%2C%5C%22cpc%5C%22%2C%5C%22paid%5C%22%2C%5C%22conv_index%5C%22%2C%5C%22conv_index_cpa%5C%22%5D%22%2C%22begin_time%22%3A"+startTime+"%2C%22end_time%22%3A"+endTime+"%7D&token="+token+"&appid="+appid+"&spid=&_="+currentTime
    response = requests.get(_url, headers={
        "Cookie": utils.transfomrCookie(fileStorage.getStorage("mp_cookies"))
    })
    print("table url: ", response.url)
    print("table data:", response.text)

    responseData = json.loads(response.text)

    if responseData.get("ret") != 0:
        redirectMp()
    else:
        with open("./data.json", "w") as f:
            json.dump(responseData, f, ensure_ascii=False)
