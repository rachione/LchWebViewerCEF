from urllib.request import Request, urlopen, urlparse, quote

Headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}


class SearchCore():

    def __init__(self, query):
        self.query = query
        pass

    def getUrl(self, keyword):
        url = self.query % keyword
        url = urlparse(url)
        url = url.scheme + "://" + url.netloc + quote(url.path)
        return url

    def getUrlResp(self, keyword):
        url = self.getUrl(keyword)
        req = Request(url)
        req.headers = Headers
        with urlopen(req) as resp:
            data = resp.read()
            data = data.decode(resp.headers.get_content_charset())
        return data
