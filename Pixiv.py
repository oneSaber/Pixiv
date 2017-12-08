import requests
from bs4 import BeautifulSoup
import os
import time
import datetime
import json
se = requests.Session()
class Pixiv():
    def __init__(self):
        self.id = '你的登陆id'
        self.password = '你的登陆密码'
        self.baseurl = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        self.loginurl = 'https://accounts.pixiv.net/api/login?lang=zh'
        self.header = {
            'Host': "accounts.pixiv.net",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        }
        self.searchbase = 'https://www.pixiv.net/search.php'
        self.return_to = "http://www.pixiv.net/"
        self.passkey= []
        self.Cookie = ''

    def Login(self):
        login_html = se.get(self.baseurl,headers = self.header).text
        login_BS = BeautifulSoup(login_html,'lxml')
        self.passkey = login_BS.find('input')['value']
        login_data = {
            "pixiv_id": self.id,
            "password": self.password,
            'post_key': self.passkey,
            'return_to': self.return_to
        }
        self.Cookie = se.post(self.loginurl,login_data,headers = self.header).cookies

    #得到页面
    def GetPage(self,url):
        # 需要一个新的请求头
        headers = { 'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
                    'Host':'www.pixiv.net',
                   }
        try:
            html = se.get(url,headers = headers,cookies = self.Cookie).text
            page = BeautifulSoup(html,'lxml')
            return page
        except:
            # 返回None
            headers['Referer'] = 'https://www.pixiv.net/'
            try:
                html = se.get(url, headers=headers, cookies=self.Cookie).text
                page = BeautifulSoup(html, 'lxml')
                return page
            except:
                print("can't get")
            return None

    def DownloadImg(self,img_src,img_name,img_url):
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
        except:
            return
        if img.status_code == 200:
            try:
                f = open(img_name,'wb')
                f.write(img.content)
                f.close()
                return True
            except:
                print(img_name+'保存失败')
                return False
        elif img.status_code==404:
            img_name = img_name.replace('jpg','png')
            img_src = img_src.replace('jpg','png')
            img = se.get(url=img_src,headers= header)
            if img.status_code==200:
                try:
                    with open(img_name,'wb') as f:
                        f.write(img.content)
                    return True
                except:
                    print(img_name + '保存失败')
                    return False
        else :
            print('保存失败')
            return False

    def GetImg(self,img_url):
        imgpage = self.GetPage(img_url)
        #图片标题
        base_title = imgpage.find('section', {'class': 'work-info'}).find('h1', {'class': 'title'}).text
        img_info = imgpage.find('div', {'class': '_layout-thumbnail ui-modal-trigger'})
        # 多图
        if img_info == None:
            img_info = imgpage.find('div', {'class': 'works_display'}).find('div', {'class': '_layout-thumbnail'})
            self.MakeDir(base_title,True)
            print(os.getcwd())
            pg_cout = img_info.find('div', {'class': 'page-count'}).find('span').text
            base_src = img_info.find('img')['src']
            for i in range(int(pg_cout)):
                src = base_src.replace('p0', 'p' + str(i)).replace('c/600x600/', '')
                title = base_title + str(i)+src[-4:]
                if self.DownloadImg(src,title,img_url):
                    print(str(i)+'保存成功')
                time.sleep(5)
            os.chdir(os.path.abspath('..'))
            print(os.getcwd())
        else:
            # text_info = img_info.find('div',{'class':'_illust_modal ui-modal-close-box'})
            src = img_info.find('img')['src'].replace('c/600x600/img-master', 'img-original').replace('_master1200', '')
            img_name = img_info.find('img')['alt']+src[-4:]
            print(img_name,src)
            if self.DownloadImg(src,img_name,img_url):
                print('保存成功')
                time.sleep(5)
            else:
                time.sleep(5)
    def MakeDir(self,name,change=False):
        if change == False:
            path = name.strip()
            isExists = os.path.exists(os.path.join("F:\P站图", path))
            if not isExists:
                print('创建新的文件夹')
                os.makedirs(os.path.join("F:\P站图", path))
                os.chdir("F:\P站图\\" + name)
                return True
            else :
                print('文件夹已经存在')
                os.chdir("F:\P站图\\" +name)
                return False
        else:
            dirname = name.strip()
            path = os.getcwd()
            dir_path = os.path.join(path,dirname)
            isExists = os.path.exists(dir_path)
            if not isExists:
                print('创建新的文件夹'+dirname)
                os.makedirs(dir_path)
                os.chdir(dir_path)
                return True
            else :
                print('文件夹已经存在')
                os.chdir(dir_path)
                return False


    # def text(self):
    #     self.Login()
    #     self.GetImg('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=66164218')
class PixivRank(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)
        self.rankurl = 'https://www.pixiv.net/ranking.php?mode=daily&content=illust'
    def work(self):
        self.Login()
        self.MakeDir(str(datetime.date.today()))
        rank_page = self.GetPage(self.rankurl)
        li_list = rank_page.find_all('section',attrs={'class':'ranking-item'})
        for li in li_list:
            print(li['data-rank'],li['data-title'])
            img_url = 'https://www.pixiv.net' + li.find('div',attrs = {'class':'ranking-image-item'}).find('a')['href']
            self.GetImg(img_url)
            time.sleep(5)
        print(str(datetime.date.today()) + '保存完成')

class Artist(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)
    def work(self):
        self.Login()
        name = input("Artist name:")
        id = input("Aritst id:")
        self.MakeDir(name)
        url = 'https://www.pixiv.net/member_illust.php?id=' + id+'&type=all'
        base_url = 'https://www.pixiv.net/member_illust.php'
        Artist_page = self.GetPage(url)
        next_page = Artist_page.find('span',attrs= {'class':'next'})

        while next_page != None:
            try:
                next_href = next_page.find('a')['href']
            except:
                break
            url = base_url +next_href
            pic_list = Artist_page.find_all('li',attrs={'class':'image-item'})
            for pic_info in pic_list:
                href = pic_info.find('a')['href']
                pic_url = 'https://www.pixiv.net'+href
                self.GetImg(pic_url)
                time.sleep(5)
            Artist_page = self.GetPage(url)
            next_page = Artist_page.find('span', attrs={'class': 'next'})


class PixivSearch(Pixiv):
    def __init__(self):
        Pixiv.__init__(self)
        self.search_url = 'https://www.pixiv.net/search.php?word='# search Nier
        self.pic_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='

    def FindStar(self,pic_url):
        pic = self.GetPage(pic_url)
        return pic.find('dd',attrs={'class':'rated-count'}).text

    def CleanData(self,li):
        li = li[1:-1].rsplit('}')
        li_json = []
        for l in li:
            if l.startswith(','):
                l = l[1:]
                l = l + '}'
                try:
                    li_json.append(json.loads(l))
                except:
                    continue
        return li_json
    def work(self):
        self.Login()
        base_url ='https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
        key_word = input('key word is english:')
        maxNum = int(input('maxmarkcout:'))
        self.MakeDir(key_word)
        for i in range(1,100):
            print('page ',i)
            search_url = self.search_url + key_word + '&order=date_d&p=' + str(i)
            search_page = self.GetPage(search_url)
            result1 = search_page.find('input',attrs={'id':'js-mount-point-search-result-list'})
            Id = result1['data-items']
            li_list = self.CleanData(Id)
            for lj in li_list:
                if lj['bookmarkCount'] > maxNum:
                    print(lj['illustId'], lj['illustTitle'],lj['bookmarkCount'])
                    pic_img = base_url+lj['illustId']
                    self.GetImg(pic_img)

if __name__ == '__main__':
    model = input("1.Rank\n2.Artist\n3.Search\n")
    if model == 'Rank':
        pixiv = PixivRank()
        pixiv.work()
    if model == 'Artist':
        pixiv = Artist()
        pixiv.work()
    if model== 'Search':
        pixiv = PixivSearch()
        pixiv.work()
# pixiv = Pixiv()
# pixiv.text()
