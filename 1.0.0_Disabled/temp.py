## -*- coding: utf8 -*-
import time
from time import sleep
from bs4 import BeautifulSoup
from lxml import etree
import requests
from datetime import datetime

price_std = [0] * 9
price_buf1 = [0] * 9
price_buf2 = [0] * 9
price_buf3 = [0] * 9
buf_info = [0]*9
mes = [0] * 9


##################
#####Constant#####
OPEN_TIME = (9,30)
CLOSE_TIME = (16,0)
K_MY_XY_CH = (756,346)
K_MY_XY_OK = (983,320)
K_OP_XY_CH = (747,670)
K_OP_XY_OK = (983,644)
BACK_XY = (234,8)
#####Constant#####
##################

super_token = 1
market_open_token = [1]*9
market_close_token = [1]*9
shortsqueezelock = [1]*9
go = 0
server_token = 1
current_time = 0

HEADERS = ({'User-Agent':
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"})


def etf_info_upd(ticker):
	try :
		URL = "https://www.investing.com/etfs/" + ticker
		  
		webpage = requests.get(URL, headers=HEADERS)
		webpage.raise_for_status()
		if webpage.status_code != requests.codes.ok :
			return -1
		soup = BeautifulSoup(webpage.content, "html.parser")
		dom = etree.HTML(str(soup))
		try :
			state = dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/text()')[0].replace(' ','')
		except :
			state = ""
		print(state)
		if state == 'PreMarket ' or state == 'AfterHours' :
			price = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/span/text()')[0])
			variance = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/div[1]/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/div[2]/text()')[0].replace('%',''))
		else :
			price = float(dom.xpath('//*[@id="last_last"]/text()')[0])
			variance = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[2]/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[4]/text()')[0].replace('%',''))

		return price, variance, variance_per, '%+.2f, (%+.2f%%)' % (variance,variance_per), 1 if state == 'PreMarket' else 2 if state == 'AfterHours' else 0

	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	#except TimeOutException as eT:
#		print(f'ERROR : {eT}')
#		stock_info_upd(ticker)
	except Exception as ex:
		print(f'ERROR crol : {ex}')
		print(current_time)

print(etf_info_upd("bmo-rex-mcrsctrs-fang-index-3x-lvrg"))