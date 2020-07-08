import random
import string

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
# 071kk IMkby Y-7wb H
# 011xSteK-THhXXOF
# 011uSI4Twk6R68qY
# 0814LLVck-4-KaLz
# 021SIqH4LdPzOw2d
# 011ZK28qqksqLwI5
# 061QWkvgq-QzLwRL
def createRandomStr():
    # string.ascii_letters 获取字符常量 a-zA-Z
    # string.digits 获取数字 0-9
    # return "071" + ''.join(random.sample(string.ascii_letters + string.digits + "-", 13))
    return "061mA8it--U-klCL"
