# -*- coding: utf-8 -*-

import datetime
import time
import random
from pyquery import PyQuery as pq
import requests
import re
import csv

#TODO: Hotels, Attractions has different XPath, along Date format in all Restaurant, Hotel and ATTRaction.
urls=[
    "https://www.tripadvisor.com/Restaurant_Review-g60842-d2085195-Reviews-Mellow_Mushroom_Gatlinburg-Gatlinburg_Tennessee.html",
    "https://www.tripadvisor.co.uk/Restaurant_Review-g1443265-d21330904-Reviews-Bella_Italia-Whitfield_Dover_Kent_England.html",
    # "https://www.tripadvisor.com/Hotel_Review-g60763-d1888977-Reviews-The_Pearl_Hotel-New_York_City_New_York.html",
]

#FROM - TO - Historical Dates
RUN_DATE=str(datetime.date.today())
FROM = '2022/01/01'
TO = '2022/12/01'
RAW_DETAIL_CSV = 'Historic_'+RUN_DATE+'.csv' #sample file

RAW_FILE_CSV = 'Historic_.csv' #sample file

BASE_URL='https://www.tripadvisor.com'
PAUSEMIN=3
PAUSEMAX=8


#Column Headers
COL_DETAIL=["url", "total_reviews", "review_id", "user","user_review_count","review_date","review_rating","review_url","review_title","review_text","user_visited_date","user_location"]


def showTime(text=''):
    """
    text: will be displayed with time as 'Starting','Closing','...'
    """
    value=datetime.datetime.today()
    if text is not None and len(text.strip())>0:
        print(text.title()+" : "+str(value))
    else:
        print(str(value))

def pause():
    time.sleep(random.choice(range(PAUSEMIN,PAUSEMAX)))
    return ''

def expandReviews(id,referer):
    headers = {    
    'accept': 'text/html, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': BASE_URL,
    'pragma': 'no-cache',
    'referer': referer,
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',    
    'x-requested-with': 'XMLHttpRequest'
    }
    params = {
    'Mode': 'EXPANDED_HOTEL_REVIEWS_RESP',
    'metaReferer': '',
    'contextChoice': 'DETAIL',
    'reviews': id,
    }
    response = requests.post(BASE_URL+'/OverlayWidgetAjax',params=params,headers=headers)
    pause()
    response_detail = pq(response.content)
    ratingDate = response_detail.find('.ratingDate').attr('title')
    userLocation = response_detail.find('.userLoc').text().strip()
    review_text= response_detail.find('[class*="reviews_text_summary"]:first .entry p').text().strip()
    return {'ratingDate':ratingDate,'userLocation':userLocation,'detailText':review_text}
    # with open('detail.html', 'wb') as f:
    #    f.write(response.content)

def writeto_csv(details,columns,fileType):
    #print("Writing to CSV :"+fileType)
    with open(fileType, 'w', newline='',encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        for list in details:
            #print(list)
            writer.writerows([list])

def verifyDate(input):
    if re.match(r'.*\,\s+\d+',input):
        inputDate=datetime.datetime.strptime(input,"%B %d, %Y")
        inputDate1 = datetime.datetime.strftime(inputDate,"%Y/%m/%d")
    else:
        inputDate=datetime.datetime.strptime(input,"%d %B %Y")
        inputDate1 = datetime.datetime.strftime(inputDate,"%Y/%m/%d")

    if inputDate>=datetime.datetime.strptime(FROM,"%Y/%m/%d") and inputDate<=datetime.datetime.strptime(TO,"%Y/%m/%d"):
        return [True,inputDate1]
    else:
        print([FROM,inputDate1,TO])
        return [False,inputDate1]

def loadDocument(url,referer,businessId):#useragent: rotate
    pages=[url]
    refererPage=BASE_URL
    
    for count,page in enumerate(pages):
        """
        TEST 
        
        if count>5:
            break        
        """
        print("Loading Page...",count+1," -- ",page)#log
        pause()
        headersValue ={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            #'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-US,en;q=0.9',
            'cache-control':'no-cache',
            'pragma':'no-cache',
            'referer':refererPage,
            'sec-fetch-dest':'document',
            'sec-fetch-mode':'navigate',
            'sec-fetch-site':'same-origin',
            'sec-fetch-user':'?1',
            'upgrade-insecure-requests':'1',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        }
        if count>0:
           refererPage=pages[(count)] 
        print(pages[count], ' -- ',refererPage,' -- ',page) #log

        html = requests.get(page,headers=headersValue)
        respMenu = pq(html.content)
        no_of_reviews=respMenu.find('div.counts').text().strip()
        if 'result' in no_of_reviews:
            no_of_reviews = re.findall(r"([0-9\,]+)\s*results|results",no_of_reviews,re.MULTILINE | re.IGNORECASE)[0].replace(',','')
        else:
            no_of_reviews=respMenu.find('#REVIEWS').text().strip()  
            if "Review" in no_of_reviews:  
                no_of_reviews = re.findall(r"(.*)review",no_of_reviews,re.MULTILINE| re.IGNORECASE)[0]
        
        #print(no_of_reviews)
        totalPages = round(int(no_of_reviews)/15)
        
        pageNumbers = respMenu.find('a.pageNum')
        for pageNumber in pageNumbers.items():
            href = pageNumber.attr('href')
            if len(href)>0:
                href=BASE_URL+href
            if href not in pages:
                pages.append(href)
        if count==0:
            print("Reviews Found", int(no_of_reviews), " -- ",totalPages, '-- ',len(pages))#log
        
        # print_r(pages)
        # break        
        html_review_containers = respMenu.find(".review-container .reviewSelector")
        for review in html_review_containers.items():
            id=review.attr('data-reviewId')
            user = review.find('.info_text div').text().strip()
            user_review = review.find('.reviewerBadge badgeText').text().strip()
            review_date = review.find('.ratingDate').attr('title')
            review_rating = review.find('[class*="_bubble_rating"]').attr('class')
            review_rating = re.findall(r"bubble\_(\d+)$",review_rating,re.MULTILINE | re.IGNORECASE)[0].strip()
            if review_rating=="10":
                review_rating=1
            elif review_rating=="15":
                review_rating=1.5
            elif review_rating=="20":
                review_rating=2
            elif review_rating=="25":
                review_rating=2.5
            elif review_rating=="30":
                review_rating=3
            elif review_rating=="35":
                review_rating=3.5            
            elif review_rating=="40":
                review_rating=4
            elif review_rating=="45":
                review_rating=4.5
            elif review_rating=="50":
                review_rating=5 
            review_url=review.find('.quote a[href*="ShowUserReviews"]').attr('href')
            if len(review_url)>0:
                review_url=BASE_URL+review_url
            if id==None:
                id = re.findall(r"\-r(.*?)\-",review_url,re.MULTILINE | re.IGNORECASE)[0].strip()
            review_title=review.find('.quote a[href*="ShowUserReviews"] .noQuotes').text().strip()
            review.find('[class*="reviews_text_summary"]:first .entry p .ulBlueLinks').remove()
            review_text=review.find('[class*="reviews_text_summary"]:first .entry p').text().strip()
            
            #explore detail about USER and long review
            detailText=expandReviews(id,page)
            if len(detailText['detailText'])>len(review_text):
                review_text = detailText['detailText']
            user_location = detailText['userLocation']

            review_text = review_text.replace('ât',"\'t").strip()
            stay_date = review.find('[class*="reviews_stay_date"]').text().strip() #replace
            stay_date = re.findall(r"\:(.*)",stay_date,re.MULTILINE | re.IGNORECASE)[0].strip()
            check = verifyDate(review_date)
            formatted_review_date=check[1]
            if check[0]:                
                reviews.append([url,no_of_reviews,id,user,user_review,formatted_review_date,review_rating,review_url,review_title,review_text,stay_date,user_location])
                #write every passed row to CSV
                writeto_csv(reviews,COL_DETAIL,RAW_FILE_CSV.replace('_',businessId))
                #print(review_text)
            else:
                break


if __name__=="__main__":
    showTime("Starting")
    for url in urls:
        if'.co.uk' in url:
            BASE_URL = 'https://www.tripadvisor.co.uk'
        if'.com' in url:
            BASE_URL = 'https://www.tripadvisor.com'
        
        FILE_ID = re.findall(r".*(\-g[a-z0-9]+\-d[a-z0-9]+)\-",url,re.MULTILINE | re.IGNORECASE)[0]
        print(FILE_ID)
        reviews=[]
        showTime("URL Start")
        loadDocument(url,'',FILE_ID)
        # print(reviews)
        showTime("URL End")
    showTime("Ending")