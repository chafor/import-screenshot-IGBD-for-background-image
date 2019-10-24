import os
import json
import requests
import datetime
import time
import uuid
import urllib.request

apiKeyIGDB = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
#platformIdIGDB = '5' #WII
#platformIdPlaynite = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx' #WII
platformIdIGDB = '19' #SNES
platformIdPlaynite = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx' #sNES
pathDatabase = "D:\\Playnite\\Database"

def LoadJsonFile(pathJson, platformIdPlaynite):
    #print(pathJson)
    with open(pathJson, encoding='utf-8') as json_file:
        data = json.load(json_file)
        if 'BackgroundImage' in data.keys():
            return -1,"",data
        else:
            if data['PlatformId'] == platformIdPlaynite:
                return data['Name'], os.path.basename(pathJson).replace(".json", ""),data
            else:
                return -1,"",data

def IsImagesNameAlreadyUsed(GameFileIdPlaynite,uuid):
    return os.path.exists(pathDatabase + '\\files\\' + GameFileIdPlaynite + '\\' + uuid + '.jpg')

def IsImagesDirectoryPresent(GameFileIdPlaynite):
    return os.path.exists(pathDatabase + '\\files\\' + GameFileIdPlaynite + '\\')

def Get1stScreenshotImagesFromIGDB(platformId, nameOfGame):
    url = 'https://api-v3.igdb.com/games/'

    headers = {'user-key': apiKeyIGDB}
    payload = 'fields *,screenshots.*; where platforms = (' + platformId + ') & name = "' + nameOfGame + '"; limit 50;'

    r = requests.get(url, data=payload, headers=headers)
    igdbGameData = r.json()
    
    if igdbGameData:
        if 'screenshots' in igdbGameData[0].keys():
            return 'http:' + igdbGameData[0]['screenshots'][0]['url'].replace('t_thumb', 't_720p')
        else:
            return -1
    else:
        return -1

def GetPlatformFromIGDB():
    url = 'https://api-v3.igdb.com/platforms/'
    headers = {'user-key': apiKeyIGDB}
    payload = 'fields *; where category = (1); limit 50;'
    print(payload)
    r = requests.get(url, data=payload, headers=headers)

    igdbGameData = r.json()
    print(igdbGameData)

def DownloadImgFromURL(url, pathImage):
    print(pathImage + ' ' + url)
    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    try:
        urllib.request.urlretrieve(url, pathImage)
        return True
    except Exception:
        print('Web Error')
        return False
    time.sleep(5)

def GenerateUUIDForFileName(path):
    uuidForImages = str(uuid.uuid4())
    while IsImagesNameAlreadyUsed(path,uuidForImages):
        uuidForImages = str(uuid.uuid4())
    return uuidForImages
        
for dirs, rien, files in os.walk(pathDatabase):
    strTmp = ""
    strTmp = dirs

    if "games" in dirs:
        i=0
        gamesWithBackground=0
        gamesWithoutBackground=0
        for fileTmp in files:
            i+=1
            print(dirs + "\\" + fileTmp)
            result = LoadJsonFile(dirs + "\\" + fileTmp, platformIdPlaynite)
            #print(result)
            if result[0] == -1:
                gamesWithBackground+=1
            else:
                gamesWithoutBackground+=1
                urlImageScreenshoot  = Get1stScreenshotImagesFromIGDB(platformIdIGDB,result[0])
                if urlImageScreenshoot != -1:
                    if IsImagesDirectoryPresent(result[1]) == False:
                        a=1#On creer le dossier
                    else:    
                        uuidForImages = GenerateUUIDForFileName(result[1])
                        if DownloadImgFromURL(urlImageScreenshoot,pathDatabase + '\\files\\' + result[1] + '\\' + uuidForImages + '.jpg') == True:
                            print(urlImageScreenshoot)
                            print(pathDatabase + '\\files\\' + result[1] + '\\' + uuidForImages + '.jpg')
                            #On réécrit le json avec le nouveau background images
                            result[2]['BackgroundImage'] = result[1] + '\\' + uuidForImages + '.jpg'
                            with open(dirs + "\\" + fileTmp, 'w') as f:
                                json.dump(result[2], f)
                
        #print("Game with : " + str(gamesWithBackground) + " Game without : " + str(gamesWithoutBackground))
    

