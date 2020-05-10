from flask import Flask, jsonify, request
import json
import os
import csv
import re, string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from os import system
import json
import os
application = Flask(__name__)
import sqlite3
from datetime import datetime, timedelta
import pymongo
import sys
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb = client['trip_advisor']


# Only enable Flask debugging if an env var is set to true
application.debug = os.environ.get('FLASK_DEBUG') in ['true', 'True']

# Get application version from env
app_version = os.environ.get('APP_VERSION')

# # Get cool new feature flag from env
# enable_cool_new_feature = os.environ.get('ENABLE_COOL_NEW_FEATURE') in ['true', 'True']
def map_month(month):
        if month == "January":return "01"
        elif month == "February":return "02"
        elif month == "March":return "03"
        elif month == "April":return "04"
        elif month == "May":return "05"
        elif month == "June":return "06"
        elif month == "July":return "07"
        elif month == "August":return "08"
        elif month == "September":return "09"
        elif month == "October":return "10"
        elif month == "November":return "11"
        elif month == "December":return "12"
def convert_date(date):
        if date.find('today') != -1:
                temp = datetime.today()
                return temp.strftime('%x')
        if date.find('yesterday') != -1:
                temp = datetime.today() - timedelta(days=1)
                return temp.strftime('%x')
        if date.find('day before yesterday') != -1:
                temp = datetime.today() - timedelta(days=2)
                return temp.strftime('%x')
        if date.find('ago') != -1:
                diff = [int(i) for i in date.split() if i.isdigit()][0]
                temp = datetime.today() - timedelta(days=diff)
                return temp.strftime('%x')
        print(date)
        op_date = date
        try:
                string = date.split()
                date = string[0]
                month = map_month(string[1])
                year = string[2]
                return date + '/' + month + '/' + year
        except:
                date = op_date
                # print(date)
                string = date.split(',')
                # print(string)
                temp = string[0].split()
                # print(temp)
                date = temp[1]
                month = map_month(temp[0])
                year = string[1].strip()
                return month + '/' + date + '/' + year


@application.route('/', methods = ['GET', 'POST'])
def test():
    return "success"

@application.route('/reset', methods = ['GET', 'POST'])
def cls():
        try:
                os.remove('tripadvisor.db')
                return "RESET SUCCESSFUL"
        except:
                return "NOTHING TO RESET"

@application.route('/scrape', methods = ['GET', 'POST'])
def get():
        r_min = 1
        mark = 1
        thresh = 10
        try :
                user_query = request.args.get('url')
        except:
                return "ERROR : URL Not Found"
        
        # base = user_query['url']
        base = user_query
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        driver = webdriver.Chrome("../drivers/chromedriver.exe",chrome_options= options)
        pages = 3
        count = 0
        t1 = time.time()
        response = {}
        ind = base.find('Reviews')
        
        col_name = user_query.split('/')[-1].split('.')[0].replace('-','_')
        print(col_name)
        mycol = mydb[col_name]
        print(mycol)
        try:
                mydoc = mycol.find_one({'_id' : 1})
                count = mydoc['pages']
                r_min = count + 1
                print(mydoc['pages'])
        except:
                count = 0
                r_min = 1
        try:
                mydoc = mycol.find_one({'_id' : 1})
                status = mydoc['full_scrape']
                print(status)
                if status == 1:
                        system('cls')
                        print('yes')
                        time.sleep(1)
                        count = 0
                        r_min = 1
        except:
                status = 0
        while count <  r_min:
                url = base[:ind] + "Reviews-or"+ str(count) + "0" + base[ind+7:]
                # url = "https://www.tripadvisor.com/Restaurant_Review-g34439-d438251-Reviews-or180-Hosteria_Romana-Miami_Beach_Florida.html"
                try:
                        driver.get(url)
                        element = driver.find_elements_by_class_name('checkmark')[0]
                        webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                        if count == 0:
                                time.sleep(1)
                        element = driver.find_element_by_class_name("ulBlueLinks")
                        webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                        time.sleep(3) 
                        # print('clicked')
                        # time.sleep(1)
                except:
                        continue

                data = {"companyName" : [], "streetAddress" :[], "city": [], "state" :[],  "postalCode" : [], "country" : [], "phone": [], "ratingsReviews" : [], "createdDateTime"  : [], "listingId" : [], "publishedDateTime" : [], "modifiedDateTime" : [], "rating": [], "_id": [], "businessURL" : [], "reviewerName" : [],  "reviewerProfile" : [], "reviewerImage" : [],  "sourceId" : [], "sourceName" : [], "title" : [], "reviewBody" : [], "reviewURL" : [], "responderDateTime" : [], "responderName" : [], "reviewResponse" : []}
                #code block
                    

                content = driver.page_source

                soup = BeautifulSoup(content,features="html.parser")

                source = soup.find('a',attrs={'class':'pageNum last'})    
                r_min = int(source.text)
                print(r_min)

                source = soup.find('div',attrs={'id':'REVIEWS'})
                for inst in source.findAll('div',attrs={'class':'reviewSelector'}):
                        get_id = inst.attrs['data-reviewid']
                        system('cls')
                        data['_id'].append(get_id)
                        system('cls')

                source = soup.find('div',attrs={'class' : "restaurantName"})

                data['businessURL'].append(url)
                data['companyName'].append(source.findAll('h1')[0].text)
                data['streetAddress'].append(soup.find('span',attrs={'class' : "street-address"}).text)

                source = soup.find('span',attrs={'class' : "locality"})
                source_text = source.text.split(',')
                data['city'].append(source_text[0])
                source_text = source_text[1].split()
                data['state'].append("".join(list(source_text[:len(source_text)-1])))
                data['postalCode'].append(source_text[-1])
                source = soup.find('ul',attrs={'class' : "breadcrumbs"}).findAll('li',attrs={'class' : "breadcrumb"})[0]
                source_text = source.findAll('span')[0].text
                data['country'].append(source_text)


                source_text = soup.find('span',attrs={'class': 'detail is-hidden-mobile'}).text
                data['phone'].append(source_text)

                buffer = []
                for source in soup.findAll('div',attrs={'class':'restaurants-detail-overview-cards-RatingsOverviewCard__ranking--17CmN'}):
                        buffer.append(source.text)

                data['ratingsReviews'].append("".join(buffer))

                buffer = []
                for source in soup.findAll('span',attrs={'class':'ratingDate'}):
                        buffer.append(source.attrs['title'])
                for i in buffer:
                        data['publishedDateTime'].append(convert_date(i))

                source = soup.find('div',attrs={'id':'REVIEWS'})
                for inst in source.findAll('span',attrs={'class':'ui_bubble_rating'}):
                          data['rating'].append(inst.attrs['class'][1][-2])


            
                for inst in source.findAll('div',attrs ={'class':'info_text pointer_cursor'}):
                        data['reviewerName'].append(inst.text.split()[0])

                sources = driver.find_elements_by_class_name('ui_avatar')
                k = 0
                while k != len(sources):
                        try:
                                element = sources[k]
                                webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                                time.sleep(3)
                                cont = driver.page_source
                                soup2 = BeautifulSoup(cont,features="html.parser")
                                soup2 = soup2.find('div',attrs={'class':'body_text'})
                                a = soup2.find('a')
                                data['reviewerProfile'].append("https://www.tripadvisor.com" + a.attrs['href'])
                                # print(len(data['reviewerProfile']))
                                webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                                # time.sleep(3)
                        except:
                                data['reviewerProfile'].append("")
                                pass
                        k += 1


                for element in soup.findAll('div',attrs = {'class':'ui_avatar resp'}):
                        img = element.find('img',attrs ={'class' : 'basicImg'})
                        if str(img.attrs['src']).find('jpg') != -1:
                                data['reviewerImage'].append(img.attrs['src'])
                        else:
                                data['reviewerImage'].append(img.attrs['data-lazyurl'])

                for inst in soup.findAll('div',attrs = {'class':'quote'}):
                        a = inst.find('a')
                        data["reviewURL"].append("https://www.tripadvisor.com" + a.attrs['href'])
                        span = inst.find('span',attrs = {'class' : 'noQuotes'})
                        data['title'].append(span.text)

                i = 0
                for source in soup.findAll('div',attrs={'class' : 'review-container'}):
                        p = source.find_all('p',attrs={'class' : 'partial_entry'})
                        if len(p) > 1:
                                data['reviewBody'].append(p[0].text)
                                data['reviewResponse'].append(p[1].text)
                                inst = source.find('span',attrs = {'class' : 'responseDate'})
                                date  = inst.attrs['title']
                                date = " ".join(date.split()[1:])
                                print(date)
                                time.sleep(10)
                                data['responderDateTime'].append(convert_date(date))
                                system('cls')
                                print(data['responderDateTime'][-1])
                                time.sleep(10)
                                inst_text = str(inst.previousSibling).split(',')
                                data['responderName'].append("".join(inst_text[:len(inst_text) - 1]))
                        else:
                                data['reviewBody'].append(p[0].text)
                                data['reviewResponse'].append("")
                                data['responderName'].append("")
                                data['responderDateTime'].append("")


                        i += 1

                reviews = {}
                info_list = ['title','reviewBody','publishedDateTime','rating','_id','reviewerName','reviewerProfile','reviewerImage','reviewURL','responderDateTime','responderName','reviewResponse']
                for i in range(len(data['_id'])):
                        temp = {}
                        for field in info_list:
                                try:
                                        temp[field] = data[field][i]
                                except:
                                        pass

                        reviews[i] = temp

                system('cls')

                info = {}
                # for field in [i for i in list(data.keys()) if i not in info_list]:
                #         info[field] = "".join(data[field])
                
                new_reviews = []
                system('cls')
                # print(reviews.keys())
                # time.sleep(1)
                for i,j in reviews.items():
                        temp = j 
                        for field in [i for i in list(data.keys()) if i not in info_list]:
                                temp[field] = "".join(data[field])
                        new_reviews.append(temp)
                # print(new_reviews[0])
                # time.sleep(5)
                # print(exist)
                over = 0
                l = 0
                for i in new_reviews:
                        try:
                                x = mycol.insert_one(i)
                                system('cls')
                                print(x)

                                l += 1
                                # time.sleep(3)
                        except:
                                system('cls')   
                                print(sys.exc_info()[0])
                                print("page",count)
                                print('break point found')
                                time.sleep(1)
                                if status == 1:
                                        over = 1
                                        break
                                
                print(l,"records inserted properly")
                
                

                # info['reviews'] = new_reviews
                # print(json.dumps(info,indent=4))


                # send[count] = info
                system('cls')
                print('success',count)
                time.sleep(1)
                count += 1
                if not status:
                        if count == r_min:
                                status = 1
                                mycol.update_one({'_id' : 1}, { "$set": { 'pages' : count,'full_scrape' : 1 } },upsert = True)
                        else:
                                mycol.update_one({'_id' : 1}, { "$set": { 'pages' : count,'full_scrape' : 0 } },upsert = True)
                
                t2 = time.time()
                print(t2-t1)
                # print(data['_id'])
                if over == 1 or count == r_min:
                        break
                        
        k = 0
        database = {}
        db=sqlite3.connect('tripadvisor.db')
        cur = db.cursor()
        cur.execute("select * from reviews order by id desc")
        db.commit()
        i = 0
        while True:
                record=cur.fetchone()
                if record == None:
                        break
                database[i] = record[1]
                i += 1
        database = json.dumps(database)
        driver.close()
        if mark == 1:
                return jsonify({'new_reviews':info,'database' : database})
        else:
                return jsonify({'database' : database})


if __name__ == '__main__':
        application.run(host="0.0.0.0",port = 80,debug=True)