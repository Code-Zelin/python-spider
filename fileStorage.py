import json

# 用于保存所有的cookie，用wx_code换取的cookie
GLOBAL_COOKIE = {}
# 用户标识
GLOBAL_G_TK = 0


# 设置缓存
def setStorage(key, value):
    with open("./storage.json", "r") as load_f:
        storage = json.load(load_f) or {}
    with open("./storage.json", "w") as dump_f:
        storage[key] = value
        # print(storage)
        json.dump(storage, dump_f)

# 读取缓存中的数据
def getStorage(key):
    with open("./storage.json", "r") as load_f:
        storage = json.load(load_f)
    return storage.get(key)
