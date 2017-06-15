# file: rhinoplasty.py
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd
import jieba

url = "http://y.soyoung.com/yuehui/hoti/p/10003_1_0_0_0_0_0_0"
#url = "http://y.soyoung.com/search/index/q/%E9%BC%BB%E7%BB%BC%E5%90%88/t/7/n/yes"	

def parse_url_to_html(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.content, "html.parser")
	return soup

def get_content(soup):
	list_set = soup.find_all(class_ = "list_set")[0]
	contents = list_set.find_all("li")
#	results = []
	results = pd.DataFrame(columns = ['doctor', 'hospital', 'new_price', 'ori_price', 'orders', 'diaries'])
	for i, c in enumerate(contents):
		doctor = c.find_all("p", class_ = "title")[0].a.get_text()
		hospital = c.find_all("p", class_ = "name")[0].a.get_text()
		
		prices = c.find_all("p", class_ = "price")[0]
		new_price = int(prices.find_all("span", class_ = "num")[0].get_text())
		ori_price = int(prices.find_all("del")[0].get_text()[1:])
		
		counts = c.find_all("div", class_ = "end")[0]
		orders = int(counts.find_all("div")[0].find_all("span")[0].get_text())
		diaries = int(counts.find_all("div")[1].find("span").get_text())
		
		results.loc[i] = [doctor, hospital, new_price, ori_price, orders, diaries] 
	return results

def get_results_set(csv_file, page_num = 20):
	results_set = pd.DataFrame(columns = ['doctor', 'hospital', 'new_price', 'ori_price', 'orders', 'diaries'])
	for page in range(1, page_num):
		soup = parse_url_to_html(url + '/page/' + str(page))
		if page == 1:
			results_set = get_content(soup)
		else:
			results_set = results_set.append(get_content(soup), ignore_index = True)	
	results_set.to_csv(csv_file, index = False, encoding = "utf-8")
	return results_set

def preprocessing(data):
	doctor_series = data['doctor']
	keys = [u'硅胶', u'膨体', u'肋软骨']
	keys_apex = [u'耳软骨', u'鼻中隔', u'全肋软骨', u'肋软骨']
	nose_bridge = pd.DataFrame(columns = ['nose_bridge'])
	nose_apex = pd.DataFrame(columns = ['nose_apex'])
	for i, d in enumerate(doctor_series):
		if d.find(keys[0]) > 0:
			nose_bridge.loc[i] = keys[0]
		elif d.find(keys[1]) > 0:
			nose_bridge.loc[i] = keys[1]
		elif d.find(keys[2]) > 0:
			nose_bridge.loc[i] = keys[2]
		else:
			nose_bridge.loc[i] = u'其他'

		if d.find(keys_apex[0]) > 0:
			nose_apex.loc[i] = keys_apex[0]
		elif d.find(keys_apex[1]) > 0:
			nose_apex.loc[i] = keys_apex[1]
		elif d.find(keys_apex[2]) > 0:
			nose_apex.loc[i] = keys_apex[2]
		elif d.find(keys_apex[3]) > 0:
			nose_apex.loc[i] = keys_apex[3]
		else:
			nose_apex.loc[i] = u'其他'	
#	data = pd.concat([data, nose_bridge], ignore_index = False)
	data = data.join(nose_bridge).join(nose_apex)
	return data 
 

if __name__ == "__main__":
	from sys import argv
	csv_file = argv[1]
#	data = pd.read_csv(csv_file, encoding = "utf-8")
	data = get_results_set(csv_file, 30)
	data = preprocessing(data)
	data.to_csv(csv_file, index = False, encoding = "utf-8")
