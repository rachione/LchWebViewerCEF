import json
import os
from core import SearchCore

packageDir = os.path.dirname(__file__)
ConfigPath = packageDir + '/config/pixiv.json'
SearchUrlQuery = 'https://www.pixiv.net/ajax/search/artworks/%s?order=date_d&mode=all&p=1&s_mode=s_tag&type=all'


class IllustData():

    def __init__(self, data):
        self.id = data['illustId']
        self.title = data['illustTitle']
        self.userName = data['userName']
        self.thumbnail = data['url']


class SearchMain():

    def __init__(self):
        self.core = SearchCore(SearchUrlQuery)
        self.idatas = {}

    def resolve(self, config):
        for keyword in config['keyword']:
            resp = self.core.getUrlResp(keyword)
            pagedata = json.loads(resp)
            if pagedata['error'] == False:
                for data in pagedata['body']['illustManga']['data']:
                    if not data['isAdContainer']:
                        idata = IllustData(data)
                        self.idatas[idata.id] = idata

    def start(self):
        self.search()

    def search(self):
        with open(ConfigPath, mode='r', encoding='utf-8') as f:
            config = json.load(f)
        self.resolve(config)
