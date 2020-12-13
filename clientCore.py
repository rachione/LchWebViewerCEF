import win32con
import win32gui
import time
import json
import os
import math
from cefpython3 import cefpython as cef
from enum import IntEnum, auto
from win32api import GetMonitorInfo, MonitorFromPoint

from extendUI.system import ExtendUISystem
from searchImg.system import SearchImgSystem


packageDir = os.path.dirname(__file__)
cssInjectPath = packageDir + '/config/css_inject.txt'
configPath = packageDir + '/config/client.json'


class WindowAlign(IntEnum):
    top = auto()
    bottom = auto()


class SystemType(IntEnum):
    extendUI = auto()
    searchImg = auto()
    none = auto()


class ScriptExec():

    def __init__(self,  content_scripts):
        self.content_scripts = content_scripts
        with open(cssInjectPath, 'r') as f:
            self.cssInjectStr = f.read()

    def load_all(self, browser):
        scripts = self.content_scripts

        for path in scripts['css']:
            self.load_css(path, browser)

        for path in scripts['js']:
            self.load_js(path, browser)

    def load_css(self, path, browser):
        with open(path, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            css = ''.join([line.strip() for line in lines])
            css = self.cssInjectStr.replace('$css', css)

            browser.ExecuteJavascript(css)

    def load_js(self, path, browser):
        with open(path, mode='r', encoding='utf-8') as f:
            browser.ExecuteJavascript(f.read())


class BrowserSetting():
    SeqX1 = 0
    SeqX2 = 0
    SeqY = 0

    def __init__(self, appData):
        self.title = appData['title']
        self.url = appData['url']
        self.windowInfo = cef.WindowInfo()
        self.custom = None

        monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
        work_area = monitor_info.get("Work")
        self.resolutionX = work_area[2]
        self.resolutionY = work_area[3]

        if 'custom' in appData:
            self.custom = appData['custom']

    def customResolve(self, val, base):
        # ratio
        if isinstance(val, str):
            ratio = val.replace('r', '')
            ratio = float(ratio)
            return math.floor(ratio * base)
        else:
            return val

    def setWindowSize(self):

        if self.custom != None and 'window_w' in self.custom:
            window_w = self.custom['window_w']
            self.window_w = self.customResolve(window_w, self.resolutionX)

        else:
            self.window_w = self.resolutionX // 3

        if self.custom != None and 'window_h' in self.custom:
            window_h = self.custom['window_h']
            self.window_h = self.customResolve(window_h, self.resolutionY)
        else:
            self.window_h = self.resolutionY

    def setSeqWindow(self):
        # top to bottom
        if BrowserSetting.SeqX2 < BrowserSetting.SeqX1:
            self.window_x = BrowserSetting.SeqX2
            self.window_y = BrowserSetting.SeqY
        else:
            self.window_x = BrowserSetting.SeqX1
            self.window_y = BrowserSetting.SeqY

        BrowserSetting.SeqY += self.window_h
        if BrowserSetting.SeqY >= self.resolutionY:
            if BrowserSetting.SeqX1 == BrowserSetting.SeqX2:
                BrowserSetting.SeqX1 += self.window_w
            BrowserSetting.SeqY = 0
            BrowserSetting.SeqX2 += self.window_w
        else:
            BrowserSetting.SeqX1 += self.window_w

    def setWindowPos(self):
        self.setSeqWindow()
        if self.custom != None and 'align' in self.custom:
            align = WindowAlign[self.custom['align']]
            if align == WindowAlign.bottom:
                self.window_y = max(0, self.resolutionY - self.window_h)
            elif align == WindowAlign.top:
                self.window_y = 0

    def setWindowInfo(self):
        if Client.parentWindowHandle != None:
            self.windowInfo.SetAsPopup(Client.parentWindowHandle, '')


class Client():
    parentWindowHandle = None

    def __init__(self, transferServer):

        self.configPath = configPath
        switches = {
            "disable-gpu": "",
            "disable-web-security": ""
        }
        context_menu = {
            "enabled": False,
            "print": False,
            "devtools": False,
            "view_source": False
        }

        cefSetting = {
            "cache_path": "cache_path/",
            "persist_session_cookies": True,
            "persist_user_preferences": True,
            "downloads_enabled": False,
            "remote_debugging_port": -1  # remote debugging
            # 'context_menu': context_menu
        }

        cef.Initialize(switches=switches, settings=cefSetting)
        self.transferServer = transferServer
        self.extendUISystem = ExtendUISystem(self)
        self.searchImgSystem = SearchImgSystem(self)

    def set_client_handlers(self, browser, client_handlers):
        for handler in client_handlers:
            browser.SetClientHandler(handler)

    def customWindow(self, browser, setting):

        hwnd = browser.GetWindowHandle()
        if Client.parentWindowHandle == None:
            Client.parentWindowHandle = hwnd
        # get defualt window style
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        # mask out the style value we don't need
        style &= ~win32con.WS_CAPTION
        style &= ~win32con.WS_SYSMENU
        style &= ~win32con.WS_THICKFRAME
        style &= ~win32con.WS_MINIMIZE
        style &= ~win32con.WS_MAXIMIZEBOX

        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.MoveWindow(hwnd, setting.window_x,
                            setting.window_y, setting.window_w, setting.window_h, True)

    def createBrowserInit(self, appData):
        setting = BrowserSetting(appData)
        setting.setWindowSize()
        setting.setWindowPos()
        setting.setWindowInfo()
        return setting

    def createBrowser(self, appData):
        setting = self.createBrowserInit(appData)
        browser = cef.CreateBrowserSync(window_info=setting.windowInfo, window_title=setting.title,
                                        url=setting.url)
        self.customWindow(browser, setting)
        return browser

    def addSystem(self, appData):
        type = SystemType[appData['type']]
        if type == SystemType.extendUI:
            self.extendUISystem.createBrowser(appData)
        elif type == SystemType.searchImg:
            self.searchImgSystem.createBrowser(appData)

    def start(self):
        with open(self.configPath, mode='r', encoding='utf-8') as f:
            data = json.load(f)
            for appData in data['App']:
                self.addSystem(appData)

    def update(self):
        cef.MessageLoop()
        cef.Shutdown()
