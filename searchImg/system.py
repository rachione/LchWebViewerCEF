import os
import json
from cefpython3 import cefpython as cef


packageDir = os.path.dirname(__file__)
contentScriptPath = packageDir + '/config/content_scripts.json'
localPagePath = "file://" + cef.GetAppPath() + '/searchImg/UI/index.html'


class LoadHandler(object):

    def __init__(self, content_scripts):
        from clientCore import ScriptExec
        self.scriptExec = ScriptExec(content_scripts)

    def OnLoadEnd(self, browser, frame, http_code):
        self.scriptExec.load_all(browser)

    # def OnLoadStart(self, browser, frame):
    #     pass
    # def OnLoadingStateChange(self, browser, is_loading, **_):
    #     pass


class SearchImgSystem():

    def __init__(self, core):
        self.core = core
        with open(contentScriptPath, mode='r', encoding='utf-8') as f:
            self.content_scripts = json.load(f)['content_scripts']

    def setLocalPagePath(self, appData):
        appData['url'] = localPagePath

    def createBrowser(self, appData):
        self.setLocalPagePath(appData)
        browser = self.core.createBrowser(appData)
        self.core.transferServer.bindFuncs(browser)
        client_handlers = [LoadHandler(self.content_scripts)]
        self.core.set_client_handlers(browser, client_handlers)
