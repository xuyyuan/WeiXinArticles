import requests
import re
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
from config import *
import pymongo
import os
from hashlib import md5   # 新的内容

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}
# 最好headers放做全局变量，这样就不用在每个方法里面都要引用咯

def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'ture',
        'count': 20,
        'cur_tab': 3
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('请求索引页失败！')
        return None

def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):  # 返回一个列表  字典的get以及setdefault方法要看一下, 'data‘是一个列表
            yield item.get('article_url')

def get_page_detail(url):
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print('请求详情页失败！')
        return None

def parse_page_detail(html, url):
    pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),', re.S)
    results = re.search(pattern, html)  # ！！！这里还是不要加group，因为不能保证每个网页都是组图形式的，有些网页不是以组图（gallery）的形式存在的。而我们就是要找组图形式的。
    # return results                    # 前面不小心误加了个return程序就会中断！！！血与泪的教训啊---
    if results:
        # print(results)
        results = results.group(1)   # 这里才加上group(1)
        results = re.sub(r'\\', '', results)  # !!!关键啊 把里面的正则给去掉，加上此句之前花了好长时间来处理报错
        data = json.loads(results)
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('title').string
        # if title:
        #     print(title)
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: download_image(image)  # 通过遍历来保存图片
            return {
                'title':title,
                'url':url,
                'images':images
            }

def download_image(url): # z这里注意下url
    print('正在下载', url)
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            save_images(res.content)
        return None
    except RequestException:
        print('请求图片失败！', url)
        return None

def save_images(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')  # 联合下面的if语句，为了防止图片图片是一样的而造成出错之类的，这里用了hashlib
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)

def save_to_mongodb(results):
    try:
        if db[MONGO_TABLE].insert(results):
            print('存储到mongodb成功', results)
    except Exception: # 直接用Exception父类
        print('存储到mongodb失败', results)

def main():
    json_string = get_page_index(0, '街拍')  # json_string最好不要用html代替，代码容易混淆，可读性不好
    for url in parse_page_index(json_string):
        html = get_page_detail(url)
        if html:
            # print(url)  # 可以加上这句来作为判断和比较
            results = parse_page_detail(html, url)  # 抽象出函数很重要
            if results:
                save_to_mongodb(results)

if __name__ == '__main__':
    main()
