import requests
import re
from bs4 import BeautifulSoup
import json
import demjson

url = 'https://www.toutiao.com/a6544286342644236803/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}
html = requests.get(url, headers=headers).text
soup = BeautifulSoup(html, 'lxml')
title = soup.find('title').text
# print(title)
pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),', re.S)
result = re.search(pattern, html).group(1)
# if result:
#     print(result)
# result_json = json.loads(result)
result = re.sub(r'\\', '', result)
print(result)
result_json = json.loads(result)

def get_space_end(lever):
    return '  ' * lever + '-'

def get_space_expand(lever):
    return '  ' * lever + '+'

def find_keys(target, lever):
    for each in target:
        if type(target[each]) is not dict:
            print(get_space_end(lever), each)
        else:
            print(get_space_expand(lever), each)
            next_lever = lever + 1
            find_keys(target[each], each)

find_keys(result_json, 1)
