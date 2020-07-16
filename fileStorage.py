import json

# 用于保存所有的cookie，用wx_code换取的cookie
GLOBAL_COOKIE = {}
# 用户标识
GLOBAL_G_TK = 0


# 设置缓存
def setStorage(key, value):
    storage = getStorage("") or {}
    with open("./storage.json", "w") as dump_f:
        storage[key] = value
        # print(storage)
        json.dump(storage, dump_f)

# 读取缓存中的数据


def getStorage(key):
    storage = {}
    try:
        with open("./storage.json", "r") as load_f:
            storage = json.load(load_f)
    except IOError:
        print("Error: 没有找到文件或读取文件失败")
    
    if not key:
        return storage
    else:
        return storage.get(key)
