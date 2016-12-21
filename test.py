import os,json

def readGameList():
    path = "data/gameList"
    data = []
    for f in os.listdir(path):
        with open(path+"/"+f) as json_data:
            data.append(json.load(json_data))
    return data
print(readGameList())
