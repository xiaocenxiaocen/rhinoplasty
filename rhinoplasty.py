# file: rhinoplasty.py
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pandas as pd

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

if __name__ == "__main__":
	url = "http://y.soyoung.com/yuehui/hoti/p/10003_1_0_0_0_0_0_0"
#	url = "http://y.soyoung.com/search/index/q/%E9%BC%BB%E7%BB%BC%E5%90%88/t/7/n/yes"	
	results_set = pd.DataFrame(columns = ['doctor', 'hospital', 'new_price', 'ori_price', 'orders', 'diaries'])
	for page in xrange(1, 20):
		soup = parse_url_to_html(url + '/page/' + str(page))
		if page == 1:
			results_set = get_content(soup)
		else:
			results_set = results_set.append(get_content(soup), ignore_index = True)	
#	print results_set
	from sys import argv
	results_set.to_csv(argv[1], index = False, encoding = "utf-8")
