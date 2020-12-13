import os
import json
import requests
import time
import threading
import base64
from cefpython3 import cefpython as cef
from enum import IntEnum, auto


class SendType(IntEnum):
    url = auto()
    base64 = auto()


class DataTransfer():
    def __init__(self, destset):
        self.destset = destset
        self.sendHandlers = {
            SendType.url: self.sendByUrl,
            SendType.base64: self.sendByBase64
        }

    def getResponse(self, files, paths, succeed):
        names = [f['name'] for f in files]
        resp = {}
        resp['succeed'] = succeed
        resp['names'] = ','.join(names)
        resp['paths'] = ','.join(paths)
        return json.dumps(resp)

    def baseSend(self, data, callback):
        allSucceed = True
        indexs = data['indexs']
        files = data['files']
        title = data['title']
        isFolder = data['isFolder']

        paths = [self.destset.getPath(x) for x in indexs]

        if isFolder:
            for i, path in enumerate(paths):
                folder = os.path.join(path, title)
                if not os.path.exists(folder):
                    os.mkdir(folder, 0o666)
                paths[i] = folder

        for file in files:
            url = file['url']
            name = file['name']
            succeed, img = callback(url)
            if not succeed:
                allSucceed = False
                break
            for path in paths:
                self.saveImg(path, name, img)
            time.sleep(0.5)

        return self.getResponse(files, paths, allSucceed)

    def sendByUrl(self, data):
        callback = self.downloadImg
        return self.baseSend(data, callback)

    def sendByBase64(self, data):
        def callback(url):
            img = base64.b64decode(url)
            # succeed always true
            return True, img

        return self.baseSend(data, callback)

    def send(self, dataJson):
        data = json.loads(dataJson)
        type = SendType[data['type']]

        return self.sendHandlers.get(type)(data)

    def saveImg(self, path, name, img):
        with open("%s\\%s" % (path, name), "wb") as f:
            f.write(img)

    def downloadImg(self, url, timeout=10):
        succeed = True
        content = None
        r = requests.get(url, allow_redirects=False, timeout=timeout)
        if r.status_code != 200:
            succeed = False
            print("download img fail , HTTP status: %d" % r.status_code)

        content_type = r.headers["content-type"]
        if 'image' not in content_type:
            succeed = False
            print("download img fail ,Content-Type: %s" % content_type)
        content = r.content

        return succeed, content


class DestSet():
    def reslove(self, data):
        self.data = data['destSets']
        self.jsonStr = json.dumps(self.data)
        self.paths = self.data['paths']

    def getPath(self, index):
        return self.paths[index]['path']


class Server():
    def __init__(self, configPath):
        self.bindings = cef.JavascriptBindings(bindToFrames=False,
                                               bindToPopups=True)
        self.destSet = DestSet()
        self.dataTransfer = DataTransfer(self.destSet)
        with open(configPath, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            self.reslove(data)

    def reslove(self, data):
        self.destSet.reslove(data)

    def bindFuncs(self, browser):
        self.bindings.SetFunction("py_getDestPath", self.py_getDestPath)
        self.bindings.SetFunction("py_openPathFolder", self.py_openPathFolder)
        self.bindings.SetFunction("py_sendData", self.py_sendData_threading)
        browser.SetJavascriptBindings(self.bindings)

    def py_getDestPath(self, jsCallback):
        jsCallback.Call(self.destSet.jsonStr)

    def py_openPathFolder(self, index):
        path = self.destSet.getPath(index)
        os.startfile(path)

    # avoid UI block

    def py_sendData(self, dataJson, jsCallback):
        response = self.dataTransfer.send(dataJson)
        jsCallback.Call(response)

    def py_sendData_threading(self, dataJson, jsCallback):
        threading.Thread(target=self.py_sendData, args=[dataJson,
                                                        jsCallback]).start()
