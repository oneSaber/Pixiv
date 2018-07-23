import requests
from bs4 import BeautifulSoup
import os
import time
import datetime
import json
import re
se = requests.Session()


class Pixiv():
    def __init__(self):
        self.id = '' # 你自己的id
        self.password = '' # 密码
        self.baseurl = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.loginurl = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.header = {
            'Host': "accounts.pixiv.net",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        }
        self.searchbase = 'https://www.pixiv.net/search.php'
        self.return_to = "http://www.pixiv.net/"
        self.passkey = []
        self.Cookie = ''

    def Login(self):
        login_html = se.get(self.baseurl, headers=self.header).text
        login_BS = BeautifulSoup(login_html, 'lxml')
        self.passkey = login_BS.find('input')['value']
        login_data = {
            "pixiv_id": self.id,
            "password": self.password,
            'post_key': self.passkey,
            'return_to': self.return_to
        }
        self.Cookie = se.post(
            self.loginurl,
            login_data,
            headers=self.header).cookies

    # 得到页面
    def GetPage(self, url):
        # 需要一个新的请求头
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            'Host': 'www.pixiv.net',
        }
        try:
            html = se.get(url, headers=headers, cookies=self.Cookie)
            if html.status_code == 200:
                page = BeautifulSoup(html.text, 'lxml')
                return page
            else:
                return None
        except BaseException:
            # 返回None
            headers['Referer'] = 'https://www.pixiv.net/'
            try:
                html = se.get(url, headers=headers, cookies=self.Cookie).text
                page = BeautifulSoup(html, 'lxml')
                return page
            except BaseException:
                print("can't get")
            return None

    def DownloadImg(self, img_src, img_name, img_url):
        now_path = os.getcwd()
        path = img_name.strip()
        isExists = os.path.exists(os.path.join(now_path, path))
        if isExists:
            print('以存在')
            return False
        header = {
            'Referer': img_url,  # 这个referer必须要，不然get不到这个图片，会报403Forbidden,具体机制也不是很清楚，可能也和cookies之类的有关吧
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
        }
        try:
            img = se.get(img_src, headers=header)
        except BaseException:
            return
        if img.status_code == 200:
            try:
                f = open(img_name, 'wb')
                f.write(img.content)
                f.close()
                return True
            except BaseException:
                print(img_name + '保存失败')
                return False
        elif img.status_code == 404:
            img_name = img_name.replace('jpg', 'png')
            img_src = img_src.replace('jpg', 'png')
            img = se.get(url=img_src, headers=header)
            if img.status_code == 200:
                try:
                    with open(img_name, 'wb') as f:
                        f.write(img.content)
                    return True
                except BaseException:
                    print(img_name + '保存失败')
                    return False
        else:
            print('保存失败')
            return False


    def GetImg(self, img_url,img_title):
        # 多图的情况
        img_page = self.GetPage(img_url.replace('mode=medium', 'mode=manga'))
        if img_page is not None:
            imgList = img_page.find_all('div', {'class': 'item-container'})
            base_dir = os.getcwd()
            self.MakeDir(img_title, True)
            for img in imgList:
                title = img_title + img.find('img')['data-index']
                src = img.find('img')['data-src']
                print(title, src, os.getcwd())
                self.DownloadImg(src, title+src[-4:], img_url)
            os.chdir(base_dir)
        else:
            img_page = self.GetPage(img_url)
            info = img_page.find('head').find_all('script')[-1].text
            infoStr = re.search("original", info)
            src = info[infoStr.end()+3:re.search("tags", info).start()-4].replace('\/', '/')
            title = img_title + src[-4:]
            print(title, src)
            self.DownloadImg(src, title, img_url)


    def MakeDir(self, name, change=False):
        if name == '*':
            name = 'unknow'
        if not change:
            path = name.strip()
            isExists = os.path.exists(os.path.join("E:\P站图", path))
            if not isExists:
                print('创建新的文件夹')
                os.makedirs(os.path.join("E:\P站图", path))
                os.chdir("E:\P站图\\" + name)
                return True
            else:
                print('文件夹已经存在')
                os.chdir("E:\P站图\\" + name)
                return False
        else:
            dirname = name.strip()
            path = os.getcwd()
            dir_path = os.path.join(path, dirname)
            isExists = os.path.exists(dir_path)
            if not isExists:
                print('创建新的文件夹' + dirname)
                try:
                    os.makedirs(dir_path)
                except BaseException:
                    dir_path = os.path.join(path, 'unknow')
                    os.makedirs(dir_path)
                os.chdir(dir_path)
                return True
            else:
                print('文件夹已经存在')
                os.chdir(dir_path)
                return False

    # def text(self):
    #     self.Login()
    #     self.GetImg('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=69283019', '坂本龍馬')


class PixivRank(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)
        self.rankurl = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'

    def work(self):
        self.Login()
        self.MakeDir(str(datetime.date.today()))
        rank_page = self.GetPage(self.rankurl)
        li_list = rank_page.find_all(
            'section', attrs={
                'class': 'ranking-item'})
        for li in li_list:
            print(li['data-rank'], li['data-title'])
            img_url = 'https://www.pixiv.net' + \
                li.find(
                    'div', attrs={
                        'class': 'ranking-image-item'}).find('a')['href']
            self.GetImg(img_url, li['data-title'])
        print(str(datetime.date.today()) + '保存完成')


class Artist(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)

    def work(self):
        self.Login()
        # name = input("Artist name:")
        # id = input("Aritst id:")
        # 硬编码批量下载
        artists = [{'name': 'ましゅー', 'id': '15305293'},
                   {'name': 'wlop', 'id': '2188232'},
                   {'name': 'ASK', 'id': '1980643'},
                   {'name': 'Fori', 'id': '226174'},
                   {'name': '超凶の狄璐卡', 'id': '22124330'},
                   {'name': 'Soraizumi', 'id': '6559742'}]
        for artist in artists:
            name = artist['name']
            id = artist['id']
            self.MakeDir(name)
            url = 'https://www.pixiv.net/member_illust.php?id=' + id + '&type=all'
            base_url = 'https://www.pixiv.net/member_illust.php'
            Artist_page = self.GetPage(url)
            next_page = Artist_page.find('span', attrs={'class': 'next'})
            while next_page is not None:
                try:
                    next_href = next_page.find('a')['href']
                except BaseException:
                    break
                url = base_url + next_href
                pic_list = Artist_page.find_all(
                    'li', attrs={'class': 'image-item'})
                for pic_info in pic_list:
                    href = pic_info.find('a')['href']
                    title = pic_info.find('h1', {'class': 'title'})['title']
                    pic_url = 'https://www.pixiv.net' + href
                    self.GetImg(pic_url,title)
                Artist_page = self.GetPage(url)
                next_page = Artist_page.find('span', attrs={'class': 'next'})


class PixivSearch(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)
        self.search_url = 'https://www.pixiv.net/search.php?word='  # search Nier
        self.pic_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='

    def FindStar(self, pic_url):
        pic = self.GetPage(pic_url)
        return pic.find('dd', attrs={'class': 'rated-count'}).text

    def CleanData(self, li):
        li = li[1:-1].rsplit('}')
        li_json = []
        for l in li:
            if l.startswith(','):
                l = l[1:]
                l = l + '}'
                try:
                    li_json.append(json.loads(l))
                except BaseException:
                    continue
        return li_json

    def work(self):
        self.Login()
        base_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
        key_word = input('key word is english:')
        maxNum = int(input('maxmarkcout:'))
        self.MakeDir(key_word)
        for i in range(1, 100):
            print('page ', i)
            search_url = self.search_url + \
                key_word + '&order=date_d&p=' + str(i)
            search_page = self.GetPage(search_url)
            result1 = search_page.find(
                'input', attrs={
                    'id': 'js-mount-point-search-result-list'})
            Id = result1['data-items']
            li_list = self.CleanData(Id)
            for lj in li_list:
                if lj['bookmarkCount'] > maxNum:
                    print(
                        lj['illustId'],
                        lj['illustTitle'],
                        lj['bookmarkCount'])
                    pic_img = base_url + lj['illustId']
                    self.GetImg(pic_img)


if __name__ == '__main__':
    model = input("1.Rank\n2.Artist\n3.Search\n")
    if model == 'Rank':
        pixiv = PixivRank()
        pixiv.work()
    if model == 'Artist':
        pixiv = Artist()
        pixiv.work()
    if model == 'Search':
        pixiv = PixivSearch()
        pixiv.work()
# pixiv = Pixiv()
# pixiv.text()
