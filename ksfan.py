
import os
import datetime
import requests
from bs4 import BeautifulSoup
from time import sleep

home_link = "https://ksfan.net/amp/"
page_link_prefix = "https://ksfan.net/amp/?page="
album_list_file = "album_list.txt"
download_prefix = "https://ksfan.net"

session = requests.Session()

my_headers = {
    "Host": "ksfan.net",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Cookie": "__cfduid=d28cb43824b2a4d40cc2641fb17f363ee1588038887",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "referer": "https://ksfan.net/amp/",
    }
my_data = {
    "userId":"username",   
    "password":"password",
}

def log_to_file(msg,file_name):
    if not isinstance(msg,str):
        msg = str(msg)
    timestamp = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    file = open(file_name, 'a') # a is append mode
    file.write("["+timestamp +"]: " + msg+"\n")
    file.close()

if __name__ == "__main__":
    #删除专辑列表文件
    if os.path.exists(album_list_file):
        os.remove(album_list_file)

    response = session.get(home_link,headers=my_headers)
    bs = BeautifulSoup(response.text,features="html.parser")
    last_page_link = bs.find(title="最后一页").get("href")
    page_count = int(last_page_link[len(page_link_prefix):]) #总页数
    print("收集专辑列表中...")
    i =1
    while i <= page_count:
        page_link = page_link_prefix+str(i)
        response = session.get(page_link,headers=my_headers)
        bs = BeautifulSoup(response.text,features="html.parser")
        for album in bs.find_all(attrs={"class": "card"}):
            album_name = album.h5.text
            log_to_file(album_name,album_list_file)
            album_link = album.a["href"]
            log_to_file(album_link,album_list_file)
        i = i + 1
    print("专辑列表已保存在 album_list.txt")

    album_link = input("请输入需要下载的专辑链接:")
    print("要下载的专辑链接是 "+album_link)
    track_link_prefix = album_link+"?page="
    my_headers["referer"] = album_link # 更新请求头 , my_headers 为字典全局变量
    response = session.get(album_link,headers=my_headers)
    bs = BeautifulSoup(response.text,features="html.parser")
    last_track_link = bs.find(title="最后一页").get("href")
    track_count = int(last_track_link[len(track_link_prefix):]) #音轨总数

    i =1
    while i <= track_count:
        track_link = track_link_prefix+str(i)
        response = session.get(track_link,headers=my_headers)
        bs = BeautifulSoup(response.text,features="html.parser")
        
        track = bs.find("amp-audio")
        track_title = track.get("title") #音乐标题
        track_album = track.get("album") #专辑名
        track_src = track.get("src") #播放链接
        
        track_full_name = track_album+"_"+str(i)+"_"+track_title+".mp3"
        track_full_link = download_prefix+track_src
        print("下载中... "+track_full_name)
        try:
            response = session.get(track_full_link,headers=my_headers)
            if response.status_code == 200:
                open(track_full_name, "wb").write(response.content)
                log_to_file(track_full_name+" 下载成功","ksfan.log")
            else:
                log_to_file(track_full_name+" download error,response.status_code is "+str(response.status_code),"error.log")
                print("Failed")
        except Exception as e:
            log_to_file(track_full_name+" download error: "+str(e),"error.log")
            print("Failed")
        sleep(1)
        i = i + 1

    print("Done")
    os.system("pause")

 