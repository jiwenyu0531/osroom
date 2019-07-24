import http.client
import hashlib
import json
import urllib
import random
from apps.app import cache
from apps.core.utils.get_config import get_config


class BaiduTranslator:
    aip_call_count = 0
    appid = '20190602000304302'
    secretKey = '67HQenjjMusRbQ9CyyCd'

    def __init__(self):
        self.aip_call_count = 0

    def word_translate(self, word, from_lang, to_lang):
        pass

    @cache.cached(timeout=get_config("post", "GET_POST_CACHE_TIME_OUT"))
    def text_translate(self, content, from_lang, to_lang):
        return self.__baidu_translate(content, from_lang, to_lang)

    def __baidu_translate(self, content, fromLang, toLang):
        httpClient = None
        myurl = '/api/trans/vip/translate'
        q = content
        # fromLang = 'en'  # 源语言
        # toLang = 'zh'  # 翻译后的语言
        salt = random.randint(32768, 65536)
        sign = self.appid + q + str(salt) + self.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + self.appid + '&q=' + urllib.parse.quote(
            q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
            salt) + '&sign=' + sign

        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)
            # response是HTTPResponse对象
            response = httpClient.getresponse()
            if response.status != http.HTTPStatus.OK:
                return False, ''
            jsonResponse = response.read().decode("utf-8")  # 获得返回的结果，结果为json格式
            js = json.loads(jsonResponse)  # 将json格式的结果转换字典结构
            dst = str(js["trans_result"][0]["dst"])  # 取得翻译后的文本结果
            # print(dst)  # 打印结果
            return True, dst
        except Exception as e:
            return False, e
        finally:
            if httpClient:
                httpClient.close()

'''
if __name__ == '__main__':
    baidu_trans = BaiduTranslator()
    while True:
        print("请输入要翻译的内容,如果退出输入q")
        content = input()
        if (content == 'q'):
            break
        s, res = baidu_trans.text_translate(content, 'en', 'zh')
        print(res)
'''