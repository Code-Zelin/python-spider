import random
import string
import time
import datetime
import fileStorage


# 将对象转化成数组
def transformObjToArr(obj):
    result = []
    for key, value in obj.items():
        result.append(key + "=" + str(value))
    return result


# 数组的join方法
def arrJoinStr(arr, str=","):
    result = ""
    arr_last = arr[len(arr) - 1]
    for i in arr:
        result += i
        if i != arr_last:
            result += str
    return result


# 创建随机字符串，二维码的标识
# 验证码格式
def createRandomStr():
    # string.ascii_letters 获取字符常量 a-zA-Z
    # string.digits 获取数字 0-9
    # return "071" + ''.join(random.sample(string.ascii_letters + string.digits + "-", 13))
    return "061mA8it--U-klCL"


# 将cookie中的MMAD_TICKET转化成g_tk
def transformTicketToGTK(ticket):
    t = 5381
    if ticket:
        for a in ticket:
            t += (t << 5) + ord(a)
    return 2147483647 & t


# 获取距离今天多少天的时间戳，以及是否获取当天开始时间还是结束时间
def getTimeStampFromFewDaysAgo(days, isBegin=True):
    # 今天日期
    today = datetime.date.today()
    # 昨天时间 days = 1，前天 days-2
    yesterday = today - datetime.timedelta(days=days)
    return dateToTimeStamp(str(yesterday), '%Y-%m-%d', isBegin=isBegin)


# 格式化cookie，从dict转化成数组，在转化成字符串
def transfomrCookie(cookie):
    return arrJoinStr(transformObjToArr(cookie), "; ")


# 用日期换取时间戳
def dateToTimeStamp(date, temp="%Y%m%d", isBegin=True):
    if not temp:
        temp = "%Y%m%d"
    timeArr = time.strptime(date, temp)
    timeStamp = int(time.mktime(timeArr))
    # 如果不是开始，则需要加一天，再减去一秒，得到当天的23:59:59
    if isBegin != True:
        timeStamp = timeStamp + 3600 * 24 - 1
    return str(timeStamp)
