import pymongo
import sqlite3
from flask import Flask, jsonify, request
import json
import os
import sys
import csv
import re
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from os import system
import json
import os
application = Flask(__name__)

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb = client['yelp']

# Only enable Flask debugging if an env var is set to true
application.debug = os.environ.get('FLASK_DEBUG') in ['true', 'True']

# Get application version from env
app_version = os.environ.get('APP_VERSION')

# # Get cool new feature flag from env
# enable_cool_new_feature = os.environ.get('ENABLE_COOL_NEW_FEATURE') in ['true', 'True']
@application.route('/', methods=['GET', 'POST'])
def test():
    return "success"


@application.route('/reset', methods=['GET', 'POST'])
def clear():
        try:
                client.drop_database('yelp')
                return "RESET SUCCESSFUL"
        except:
                return "NOTHING TO RESET"


@application.route('/scrape', methods=['GET', 'POST'])
def get():
        test = None
        r_min = 1
        mark = 1
        thresh = 20
        send = {}
        try:
                user_query = request.args.get('url')
        except:
                return "ERROR : URL Not Found"

        # base = user_query['url']
        base = user_query
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(
            "./chromedriver", chrome_options=options)
        pages = 2
        count = 0
        t1 = time.time()
        response = {}

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
                        system('clear')
                        print('yes')
                        time.sleep(1)
                        count = 0
                        r_min = 1
        except:
                status = 0
        while count < r_min:
                print(r_min)
                # url = base[:ind] + "Reviews-or"+ str(count) + "0" + base[ind+7:]
                url =  base +'?' + 'sort_by=date_desc'
                if not count == 0:
                        url = base + '?start=' + str((count)*2) + '0'+'&sort_by=date_desc'
                print(url)
                time.sleep(1)
                driver.get(url)


                data = {"companyName" : [], "streetAddress" :[], "city": [], "state" :[],  "postalCode" : [], "country" : [], "phone": [], "ratingsReviews" : [], "createdDateTime"  : [], "listingId" : [], "publishedDateTime" : [], "modifiedDateTime" : [], "rating": [], "_id": [], "businessURL" : [], "reviewerName" : [],  "reviewerProfile" : [], "reviewerImage" : [],  "sourceId" : [], "sourceName" : [], "title" : [], "reviewBody" : [], "reviewURL" : [], "responderDateTime" : [], "responderName" : [], "reviewResponse" : []}
                # code block
                    

                content = driver.page_source

                soup = BeautifulSoup(content,features="html.parser")

                data['companyName'].append(soup.find('h1',attrs = {'class' : 'lemon--h1__373c0__2ZHSL heading--h1__373c0__1VUMO heading--no-spacing__373c0__1PzQP heading--inline__373c0__1F-Z6'}).text)

                element = driver.find_element_by_xpath("//span[contains(text(),'Page')]")
                print(element.text)
                r_min = int(element.text.split()[-1])
                print(r_min)


                source = soup.findAll('ul',attrs={'class':'lemon--ul__373c0__1_cxs undefined list__373c0__2G8oH'})[8]
                for inst in source.findAll('li',attrs={'class':'lemon--li__373c0__1r9wz u-space-b3 u-padding-b3 border--bottom__373c0__uPbXS border-color--default__373c0__2oFDT'}):
                        for link in inst.findAll('a',attrs={'class' : 'lemon--a__373c0__IEZFH link__373c0__29943 link-color--blue-dark__373c0__1mhJo link-size--default__373c0__1skgq'}):
                                temp = link.attrs['href']
                                if not 'photos' in temp and temp != '':
                                        data['reviewerProfile'].append('www.yelp.com' + temp)
                print(data['reviewerProfile'])

                elements = driver.find_elements_by_xpath("//p[text()='Embed review']")
                i = 0
                for inst in elements:
                        try:
                                webdriver.ActionChains(driver).move_to_element(inst).click(inst).perform()
                                time.sleep(3.5)
                                cont = driver.page_source
                                soup_ = BeautifulSoup(cont,features="html.parser")
                                # print(soup_)
                                # time.sleep(5)
                                element = soup_.find('input',attrs={'id':'embed-code-field'})
                                print(element)
                                time.sleep(1)

                                get_id = element.attrs['value'].split()[2][element.attrs['value'].split()[2].find('"') + 1: -1]
                                data['reviewURL'].append(user_query+'?hrid=' + str(get_id))
                        except:
                                print((sys.exc_info()[0]))
                                print("ID NOT FOUND", i)
                                get_id = ""
                                data['reviewURL'].append("")
                        
                        cross = driver.find_element_by_xpath("//span[text()='×']")
                        webdriver.ActionChains(driver).move_to_element(cross).click(cross).perform()
                        time.sleep(1)
                        system('clear')
                        data['_id'].append(get_id)
                        system('clear')
                        # print(thresh)
                        print(data['_id'][-1])
                        i += 1

                print(data['_id'])
                # source = soup.find('h1',attrs={'class' : "lemon--div__173c0__1mboc island__373c0__3fs6U u-padding-t1 u-padding-r1 u-padding-b1 u-padding-l1 border--top__373c0__19Owr border--right__373c0__22AHO border--bottom__373c0__uPbXS border--left__373c0__1SjJs border-color--default__373c0__2oFDT background-color--white__574c0__GVEnp"})
                
                element = driver.find_element_by_xpath("//p[text()='Business website']/following-sibling::a")
                data['businessURL'].append(element.text)
                print(data['businessURL'])

                source = soup.find('div',attrs = {'class' : 'hidden'})
                address = source.find('address')
                span = address.findAll('span')
                data['streetAddress'].append(span[0].text)
                data['city'].append(span[1].text)
                data['state'].append(span[2].text)
                data['postalCode'].append(span[3].text)

                element = driver.find_element_by_xpath("//p[text()='Phone number']/following-sibling::p")
                data['phone'].append(element.text)
                print(data['phone'])


                source = soup.findAll('ul',attrs={'class':'lemon--ul__373c0__1_cxs undefined list__373c0__2G8oH'})[8]
                for inst in source.findAll('li',attrs={'class':'lemon--li__373c0__1r9wz u-space-b3 u-padding-b3 border--bottom__373c0__uPbXS border-color--default__373c0__2oFDT'}):
                        data['title'].append("")
                        for img in inst.findAll('img',attrs={'class' : 'lemon--img__373c0__3GQUb photo-box-img__373c0__O0tbt'}):
                                temp = img.attrs['src']
                                data['reviewerImage'].append(temp)

                        for select in inst.findAll('div', attrs = {'class' : "lemon--div__373c0__1mboc i-stars__373c0__Y2F3O i-stars--regular-3__373c0__1DXMK border-color--default__373c0__YEvMS overflow--hidden__373c0__3Usf-"}):
                                print(select)
                        select = inst.findAll("span", attrs = {'class' : "lemon--span__373c0__3997G text__373c0__2pB8f text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_"})
                        if len(select) > 2:
                                data['modifiedDateTime'].append(select[3].text)
                        else:
                                data['modifiedDateTime'].append("")

                        response = inst.find('div',attrs = {'class' : 'lemon--div__373c0__1mboc u-padding-l-half border-color--default__373c0__2oFDT'})
                        if response:
                                text  = response.find('p', attrs = {'class' : 'lemon--p__373c0__3Qnnj text__373c0__2pB8f text-color--mid__373c0__3G312 text-align--left__373c0__2pnx_ text-weight--bold__373c0__3HYJa text-size--small__373c0__3SGMi'}).text
                                text = " ".join(text.split()[2:-3])
                                data["responderName"].append(text)
                        else:
                                data["responderName"].append("")
                        response = inst.find('div',attrs = {'class' : 'lemon--div__373c0__1mboc u-space-t1 border-color--default__373c0__2oFDT'})
                        if response:
                                print('Inside')
                                text  = response.find('span', attrs = {'class' : 'lemon--span__373c0__3997G text__373c0__2pB8f text-color--normal__373c0__K_MKN text-align--left__373c0__2pnx_ text-bullet--after__373c0__1ZHaA'}).text
                                data['responderDateTime'].append(text)
                                content = response.findAll('span',attrs = {'class' :'lemon--span__373c0__3997G'})[-1].text
                                data["reviewResponse"].append(content)
                        else:
                                data['responderDateTime'].append("")
                                data["reviewResponse"].append("")
                        
                print(data['publishedDateTime'])
                print(data['modifiedDateTime'])

                # print(data['reviewerImage'])
                print('\n\n')
                update = 0
                source = soup.find('div', attrs = {'class' : 'hidden'})
                data['ratingsReviews'].append(source.find('meta',attrs = {'itemprop' : 'ratingValue'}).attrs['content'])
                data['country'].append(source.find('meta',attrs = {'itemprop' : 'addressCountry'}).attrs['content'])
                for info in source.findAll('div',attrs = {'itemprop' : 'review'}):
                        data['reviewerName'].append(info.find('meta',attrs = {'itemprop' : 'author'}).attrs['content'])
                        data['rating'].append(info.find('meta',attrs = {'itemprop' : 'ratingValue'}).attrs['content'])
                        data['publishedDateTime'].append(info.find('meta',attrs = {'itemprop' : 'datePublished'}).attrs['content'])
                        if data['modifiedDateTime'][update] != "":
                                data['publishedDateTime'],data['modifiedDateTime'] = data['modifiedDateTime'] ,data['publishedDateTime']
                        data['reviewBody'].append(info.find('p',attrs = {'itemprop' : 'description'}).text)
                        update += 1     
                

                for i,j in data.items():
                        print(i,j)
                        print('\n\n')
                

                reviews = {}
                info_list = ['title','reviewBody','publishedDateTime','rating','_id','reviewerName','reviewerProfile','reviewerImage','reviewURL','responderDateTime','responderName','reviewResponse']
                # for i in range(len(data['_id'])):
                for i in range(20):

                        temp = {}
                        for field in info_list:
                                try:
                                        temp[field] = data[field][i]
                                except:
                                        pass

                        reviews[i] = temp

                system('clear')

                info = {}
                # for field in [i for i in list(data.keys()) if i not in info_list]:
                #         info[field] = "".join(data[field])
                
                new_reviews = []
                system('clear')
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
                                system('clear')
                                print(x)

                                l += 1
                                # time.sleep(3)
                        except:
                                system('clear')   
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
                system('clear')
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
        
        send = {}
        k = 0
        for x in mycol.find():
                send[k] = x
                k += 1
        # print(send)
        # # send = json.dumps(send, default=str)
        driver.close()
        if mark == 1:
                return send
        else:  
                return jsonify({'data' : 'Refer database for the Reviews'})

if __name__ == '__main__':
        application.run(host="0.0.0.0",port = 80,debug=True)
