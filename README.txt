目的是抓取今日头条上的街拍中的图集（gallery）的相关信息。

1.在parse_page_detail函数这里容易出现问题，这一点尤其重要，纠错结果是：
 （1）注意if判断语句（还有try语句）运用,这样才更细致，避免出现各种不必要的麻烦
 （2）要注意并列的关系
    如：
     soup = BeautifulSoup(html, 'lxml')
     title = soup.find('title').string
     if title:
         print(title)
    和
    pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),', re.S)
    results = re.search(pattern, html)
    if results:
        print(results)
    两者不是并列的关系，两者之间还是有联系的！
 （3）断点调试要有耐心啊！！！不耐心就会前功尽弃！！！

2.test.py是为了简单测试用的，可做参考

3.spider解决了单页的爬取，下载图片到本地以及存储一些信息到mongodb数据库

4.spider2是终结版，多页爬取，引进多进程，并且在程序的执行中不断调试和优化

Have completed !

