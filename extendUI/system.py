import os
import json

packageDir = os.path.dirname(__file__)
contentScriptPath = packageDir + '/config/content_scripts.json'


class LoadHandler(object):

    def __init__(self, content_scripts):
        from clientCore import ScriptExec
        self.scriptExec = ScriptExec(content_scripts)

    def OnLoadEnd(self, browser, frame, http_code):
        if http_code == 200 and frame.IsMain():
            self.scriptExec.load_all(browser)


class ExtendUISystem():

    def __init__(self, core):
        self.core = core
        with open(contentScriptPath, mode='r', encoding='utf-8') as f:
            self.content_scripts = json.load(f)['content_scripts']

    def createBrowser(self, appData):
        browser = self.core.createBrowser(appData)
        self.core.transferServer.bindFuncs(browser)
        client_handlers = [LoadHandler(self.content_scripts)]
        self.core.set_client_handlers(browser, client_handlers)
