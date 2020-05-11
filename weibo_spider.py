# -*- coding: utf-8 -*-
import requests,random,re
import time
import os
import csv
import sys
import json
import importlib
from fake_useragent import UserAgent
from lxml import etree

importlib.reload(sys)
startTime = time.time() #get start/end time

#--------------------------------------------file storage-----------------------------------------------------
path = os.getcwd() + "/weiboComments.csv"
csvfile = open(path, 'a', newline='', encoding = 'utf-8-sig')
writer = csv.writer(csvfile)
#csv head
writer.writerow(('Post link','Post Content','User ID', 'User Nickname', 'User ID','Posted Date',
                 'Posted time', 'Reposts Count','Comments Count','Likes Count', 'Commenter ID', 'Commenter Nickname',
                 'Comment Nickname', 'Commented Date', 'Commented Time','Comment Content'))

#set heades
headers = {
    'Cookie': '_T_WM=22822641575; H5_wentry=H5; backURL=https%3A%2F%2Fm.weibo.cn%2F; ALF=1584226439; MLOGIN=1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5RJaVYrb.BEuOvUQ8Ca2OO5JpX5K-hUgL.FoqESh-7eKzpShM2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMceoBfeh2EeKBN; SCF=AnRSOFp6QbWzfH1BqL4HB8my8eWNC5C33KhDq4Ko43RUIzs6rjJC49kIvz5_RcOJV2pVAQKvK2UbAd1Uh6j0pyo.; SUB=_2A25zQaQBDeRhGeBM71cR8SzNzzuIHXVQzcxJrDV6PUJbktAKLXD-kW1NRPYJXhsrLRnku_WvhsXi81eY0FM2oTtt; SUHB=0mxU9Kb_Ce6s6S; SSOLoginState=1581634641; WEIBOCN_FROM=1110106030; XSRF-TOKEN=dc7c27; M_WEIBOCN_PARAMS=oid%3D4471980021481431%26luicode%3D20000061%26lfid%3D4471980021481431%26uicode%3D20000061%26fid%3D4471980021481431',
    'Referer': 'https://m.weibo.cn/detail/4312409864846621',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

#-----------------------------------scrape id of every topic under the front page of 战疫情------------------------------------------
comments_ID = []
def get_title_id():
    for page in range(1,21):  #every page has roughly 18 topics
        headers = {
            "User-Agent" : UserAgent().chrome #chrome random agent
        }
        time.sleep(1)

        api_url = 'https://m.weibo.cn/api/feed/trendtop?containerid=102803_ctg1_600059_-_ctg1_600059&page=' + str(page)
        print(api_url)
        rep = requests.get(url=api_url, headers=headers)

        for json in rep.json()['data']['statuses']:
            comment_ID = json['id'] 
            comments_ID.append(comment_ID)

#-----------------------------------scrape every topic under 战疫情 hashtag in details------------------------------------------
def spider_title(comment_ID):
    try:
        article_url = 'https://m.weibo.cn/detail/'+ comment_ID
        print ("article_url = ", article_url)
        html_text = requests.get(url=article_url, headers=headers).text
        #post text
        find_title = re.findall('.*?"text": "(.*?)",.*?', html_text)[0]
        title_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', find_title)
        print ("title_text = ", title_text)
        #user ID
        title_user_id = re.findall('.*?"id": (.*?),.*?', html_text)[1]
        print ("title_user_id = ", title_user_id)
        #user nickname
        title_user_NicName = re.findall('.*?"screen_name": "(.*?)",.*?', html_text)[0]
        print ("title_user_NicName = ", title_user_NicName)
        #user gender
        title_user_gender = re.findall('.*?"gender": "(.*?)",.*?', html_text)[0]
        print ("title_user_gender = ", title_user_gender)
        #posting time
        created_title_time = re.findall('.*?"created_at": "(.*?)".*?', html_text)[0].split(' ')
        #posting date
        if 'May' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '05', created_title_time[2])
        elif 'Apr' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '04', created_title_time[2])
        elif 'Mar' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '03', created_title_time[2])
        elif 'Feb' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '02', created_title_time[2])
        elif 'Jan' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '01', created_title_time[2])
        else:
            print ('Error: this time is not during the Covid-19 pandemic period！URL = ')
            pass
        print ("title_created_YMD = ", title_created_YMD)
        #posting time
        add_title_time = created_title_time[3]
        print ("add_title_time = ", add_title_time)
        #reposts amount
        reposts_count = re.findall('.*?"reposts_count": (.*?),.*?', html_text)[0]
        print ("reposts_count = ", reposts_count)
        #comments amount
        comments_count = re.findall('.*?"comments_count": (.*?),.*?', html_text)[0]
        print ("comments_count = ", comments_count)
        #likes amount
        attitudes_count = re.findall('.*?"attitudes_count": (.*?),.*?', html_text)[0]
        print ("attitudes_count = ", attitudes_count)   
        comment_count = int(int(comments_count) / 20) #every ajax can load 20 data once
        position1 = (article_url, title_text, title_user_id, title_user_NicName,title_user_gender, title_created_YMD, add_title_time, reposts_count, comments_count, attitudes_count, " ", " ", " ", " "," ", " ")

        writer.writerow((position1))
        return comment_count
    except:
        pass


#-------------------------------------------------scrape comments info---------------------------------------------------
#comment_ID
def get_page(comment_ID, max_id, id_type):
    params = {
        'max_id': max_id,
        'max_id_type': id_type
    }
    url = ' https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id'.format(comment_ID, comment_ID)
    try:
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            return r.json()
    except requests.ConnectionError as e:
        print('error', e.args)
        pass

#-------------------------------------------------scrape the max of commment items---------------------------------------------------
def parse_page(jsondata):
    if jsondata:
        items = jsondata.get('data')
        item_max_id = {}
        item_max_id['max_id'] = items['max_id']
        item_max_id['max_id_type'] = items['max_id_type']
        return item_max_id

#-------------------------------------------------file comments info---------------------------------------------------
def write_csv(jsondata):
    for json in jsondata['data']['data']:

        user_id = json['user']['id']

        user_name = json['user']['screen_name']

        user_gender = json['user']['gender']

        comments_text = json['text']
        comment_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', comments_text)

        created_times = json['created_at'].split(' ')

        if 'May' in created_times:
            created_YMD = "{}/{}/{}".format(created_times[-1], '05', created_times[2])
        elif 'Apr' in created_times:
            created_YMD = "{}/{}/{}".format(created_times[-1], '04', created_times[2])
        elif 'Mar' in created_times:
            created_YMD = "{}/{}/{}".format(created_times[-1], '03', created_times[2])
        elif 'Feb' in created_times:
            created_YMD = "{}/{}/{}".format(created_times[-1], '02', created_times[2])
        elif 'Jan' in created_times:
            created_YMD = "{}/{}/{}".format(created_times[-1], '01', created_times[2])
        else:
            print ('Error: this time is not during the Covid-19 pandemic period！')
            pass
        created_time = created_times[3]
        #if len(comment_text) != 0:
        position2 = (" ", " ", " ", " "," ", " ", " ", " ", " ", " ", user_id, user_name, user_gender, created_YMD, created_time, comment_text)
        writer.writerow((position2))
        #print (user_id, user_name, user_gender, created_YMD, created_time)    


#-------------------------------------------------Main Function---------------------------------------------------
def main():
    count_title = len(comments_ID)
    for count, comment_ID in enumerate(comments_ID):
        print ("The %s post is being scraped，%s posts are found"%(count+1, count_title))

        maxPage = spider_title(comment_ID)
        print ('maxPage = ', maxPage)
        m_id = 0
        id_type = 0
        if maxPage != 0:
            try:

                for page in range(0, maxPage):

                    jsondata = get_page(comment_ID, m_id, id_type)
                    

                    write_csv(jsondata)
                    

                    results = parse_page(jsondata)
                    time.sleep(1)
                    m_id = results['max_id']
                    id_type = results['max_id_type']              
            except:
                pass
        print ("---------------------------------------------------------")
    csvfile.close() 
    
if __name__ == '__main__':
    

    get_title_id()

    main()

    endTime = time.time()
    useTime = (endTime-startTime) / 60
    print("Total time costs: %s mins"%useTime)
