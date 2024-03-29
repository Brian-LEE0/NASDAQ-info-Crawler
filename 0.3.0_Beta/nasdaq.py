## -*- coding: utf8 -*-
import time
import re
from time import sleep
from bs4 import BeautifulSoup
from lxml import etree
import requests
from datetime import datetime
from kakaotalk_handle import open_chatroom, kakao_sendtext

price_std = [0] * 9
price_buf1 = [0] * 9
price_buf2 = [0] * 9
price_buf3 = [0] * 9
buf_info = [0]*9
mes = [0] * 9

SVSTATE_ROOMNAME = "이인영"


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

class TimeOutException(Exception):
	pass
# 요청 완료
#def alarm_handler(signum,frame) :
#	print("Time is up")
#	raise TimeOutException()

class DuplicationError(Exception):
	def __init__(self):
		super().__init__("DuplicationError")

def countdown(t):
	try :
		while t:
			mins, secs = divmod(t, 60)
			timer = '{:02d}:{:02d}'.format(mins, secs)
			print(timer, end="\r")
			sleep(1)
			t -= 1
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	except Exception as ex:
		print(f'ERROR : {ex}')


def KrwUsdconv():
	try :
		URL = "https://kr.investing.com/currencies/usd-krw"
		  
		web = requests.get(URL, headers=HEADERS)
		
		price = float(web.text.split("data-test=\"instrument-price-last\">")[1].split("</span>")[0].strip().replace(",",""))
		print(price)
		return price
		
	except Exception as ex:
		print(f'ERROR at currency : {ex}')
		return 1300



def stock_info_upd(ticker):
	try :
		URL = "https://www.investing.com/equities/" + ticker
		web = requests.get(URL, headers=HEADERS)
		try :
			state = web.text.split("<div class=\"closed-market_status")[1].split(">")[1].split("<")[0].strip()
		except :
			state = ""
		
		

		if state == 'Pre Market' or state == 'After Hours' :
			servtime = (("Pre" if state == "Pre Market" else "Aft") + web.text.split("<time")[2].split(">")[1].split("</time")[0])[:8]
			price = float(re.search("[+-]?\d+\.\d+",web.text.split("data-test=\"instrument-price-last\">")[2].split("</span>")[0].strip().replace(",","")).group())
			variance = float(re.search("[+-]?\d+\.\d+",web.text.split("data-test=\"instrument-price-change\">")[2].split("</span>")[0].strip().replace(",","")).group())
			variance_per = float(re.search("([+-]?\d+\.\d+)",web.text.split("data-test=\"instrument-price-change-percent\">")[2].split("</span>")[0].strip().replace(",","")).group())
			

		else :
			servtime = web.text.split("<time")[1].split(">")[1].split("</time")[0][:5]
			price = float(re.search("([+-]?\d+\.\d+)",web.text.split("data-test=\"instrument-price-last\">")[1].split("</span>")[0].strip().replace(",","")).group())
			variance = float(re.search("([+-]?\d+\.\d+)",web.text.split("data-test=\"instrument-price-change\">")[1].split("</span>")[0].strip().replace(",","")).group())
			variance_per = float(re.search("([+-]?\d+\.\d+)",web.text.split("data-test=\"instrument-price-change-percent\">")[1].split("</span>")[0].strip().replace(",","")).group())
			

		return price, variance, variance_per, '%+.2f, (%+.2f%%)' % (variance,variance_per), 1 if state == 'Pre Market' else 2 if state == 'After Hours' else 0, servtime
		
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	#except TimeOutException as eT:
#		print(f'ERROR : {eT}')
#		stock_info_upd(ticker)
	except Exception as ex:
		print(f'ERROR crol : {ex}')
		print(current_time)
		countdown(1)


def etf_info_upd(ticker):
	try :
		URL = "https://www.investing.com/etfs/" + ticker
		  
		webpage = requests.get(URL, headers=HEADERS)
		print(webpage.text[:200])
		webpage.raise_for_status()
		if webpage.status_code != requests.codes.ok :
			return -1
		soup = BeautifulSoup(webpage.content, "html.parser")
		dom = etree.HTML(str(soup))
		try :
			state = dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/text()')[0].replace(' ','')
		except :
			state = ""
		if state == 'PreMarket' or state == 'AfterHours' :
			price = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/span/text()')[0].replace(",",""))
			variance = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/div[1]/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[3]/div[1]/div[2]/text()')[0].replace('%',''))
		else :
			price = float(dom.xpath('//*[@id="last_last"]/text()')[0].replace(",",""))
			variance = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[2]/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quotes_summary_current_data"]/div[1]/div[2]/div[1]/span[4]/text()')[0].replace('%',''))
	
		return price, variance, variance_per, '%+.2f, (%+.2f%%)' % (variance,variance_per), 1 if state == 'PreMarket' else 2 if state == 'AfterHours' else 0, "00:00" 

	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	#except TimeOutException as eT:
#		print(f'ERROR : {eT}')
#		stock_info_upd(ticker)
	except Exception as ex:
		print(f'ERROR crol : {ex}')
		print(current_time)

def yahoo_info_upd(ticker):
	try :
		URL = "https://finance.yahoo.com/quote/" + ticker
		  
		webpage = requests.get(URL, headers=HEADERS)
		webpage.raise_for_status()
		if webpage.status_code != requests.codes.ok :
			return -1
		soup = BeautifulSoup(webpage.content, "html.parser")
		dom = etree.HTML(str(soup))
		try :
			state = dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[2]/span[2]/span/text()')[0]
		except :
			state = ""
		if state == 'After hours:' or state == 'Pre-Market:' :
			try :
				price = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[2]/fin-streamer[2]/text()')[0].replace(",",""))
			except :
				price = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[2]/span[1]/fin-streamer[1]/span/text()')[0].replace(",",""))
			variance = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[2]/span[1]/fin-streamer[1]/span/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[2]/span[1]/fin-streamer[2]/span/text()')[0].replace('%','').replace('(','').replace(')',''))
		else :
			price = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[1]/text()')[0].replace(",",""))
			variance = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[2]/span/text()')[0])
			variance_per = float(dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/fin-streamer[3]/span/text()')[0].replace('%','').replace('(','').replace(')',''))

		return price, variance, variance_per, '%+.2f, (%+.2f%%)' % (variance,variance_per), 1 if state == 'Pre-Market:' else 2 if state == 'After hours:' else 0, "00:00" 

	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	#except TimeOutException as eT:
#		print(f'ERROR : {eT}')
#		stock_info_upd(ticker)
	except Exception as ex:
		print(f'ERROR crol : {ex}')
		print(current_time)


def judgeval(tickerfull, ticker, key, variance, inc_emoji, dec_emoji, tothemoon_emoji, OPCHAT_ROOMNAME ,source_site = "investing"):
	try :
		global price_std
		global mes
		global market_open_token
		global market_close_token
		global price_buf1
		global price_buf2
		global price_buf3
		global buf_info
		global shortsqueezelock
		if current_time.hour >= 4 and current_time.hour < 21 and current_time.weekday() != 5 and current_time.weekday() != 6:
			if source_site == "investing" : price_info = stock_info_upd(tickerfull)
			elif source_site == "yahoo" : price_info = yahoo_info_upd(tickerfull)
			else : return -1

			##open notice
			if current_time.hour == OPEN_TIME[0] and current_time.minute >= OPEN_TIME[1] and price_info[4] == 0 and market_open_token[key] == 1 :
				mes[key] = f'[장 시작] ({price_info[5]})\n{ticker} 주가!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				market_open_token[key] = 0
				sendPricetoKAKAO(OPCHAT_ROOMNAME, key)
				countdown(3)
				return 0
			if current_time.hour == CLOSE_TIME[0] and current_time.minute >= CLOSE_TIME[1] and price_info[4] == 2 and market_close_token[key] == 1  :
				try :
					mes[key] = f'[장 종료] ({price_info[5]})\n{ticker} 주가!\n<{str(buf_info[key][0])}$, {buf_info[key][3]}>'
					print(mes[key])
					price_std[key] = price_info[2]
					market_close_token[key] = 0
					sendPricetoKAKAO(OPCHAT_ROOMNAME, key)
					countdown(3)
					return 0
				except :
					market_close_token[key] = 0
					return 0
				

			#duplicationError judg
			if price_buf1[key] != price_info[0] and price_buf2[key] != price_info[0] and price_buf3 != price_info[0] :
				try :
					price_buf3[key] = price_buf2[key]
					price_buf2[key] = price_buf1[key]
					price_buf1[key] = price_info[0]
				except Exception as ex :
					print(f'{ex} 발생')
			else :
				raise DuplicationError


			print(ticker + "'s info : " + str(price_info) + " / Std% : "+ str(price_std[key]))


			

			#############

			if  price_info[2] >= 20 and price_info[2] >= (price_std[key] + variance):
				mes[key] = f'[{(tothemoon_emoji)*7}] ({price_info[5]})\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>\n숏스퀴즈 예감!!!!!!!'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(OPCHAT_ROOMNAME, key)
				if shortsqueezelock[key] == 1 :
					sendPricetoKAKAOshortAlert(OPCHAT_ROOMNAME, ticker,tothemoon_emoji)
					shortsqueezelock[key] = 0
			elif price_info[2] >= (price_std[key] + variance):
				mes[key] = f'[{(inc_emoji)*4}] ({price_info[5]})\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(OPCHAT_ROOMNAME, key)
			elif price_info[2] <= price_std[key] - variance:
				mes[key] = f'[{(dec_emoji)*4}] ({price_info[5]})\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(OPCHAT_ROOMNAME, key)

			#############
		else :
			if (current_time.hour == 23) :
				market_open_token = [1]*9
				market_close_token = [1]*9
				shortsqueezelock = [1]*9
				price_std = [0]*9
			print("준비중! 안전벨트 꽉매")
			countdown(1)
			return 0
		buf_info[key] = price_info
		countdown(1)
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	except DuplicationError as Dp:
		print("Skip Process : {}, {}".format(ticker,price_info[0]))
		countdown(1)
	except Exception as ex:
		print(f'ERROR at judge : {ex}')
		countdown(5)

def sendPricetoKAKAO(OPCHAT_ROOMNAME,key):
	try :
		print(mes[key] + " OK")
		open_chatroom(OPCHAT_ROOMNAME)
		kakao_sendtext(OPCHAT_ROOMNAME, mes[key])
	except Exception as ex:
		print(f'ERROR : {ex}')\

def sendMestoKAKAO(OPCHAT_ROOMNAME,message):
	try :
		print(message + " OK")
		open_chatroom(OPCHAT_ROOMNAME)
		kakao_sendtext(OPCHAT_ROOMNAME, message)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOshortAlert(OPCHAT_ROOMNAME,ticker,tothemoon_emoji):
	try :
		mes = f'[{(tothemoon_emoji)*7}]\n{ticker}주가 20% 상승!!!!!!\n유심히 관찰하세요'
		open_chatroom(OPCHAT_ROOMNAME)
		for i in range(5) :
			print(mes + " OK")
			kakao_sendtext(OPCHAT_ROOMNAME, mes)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOerror(er):
	try :
		open_chatroom(SVSTATE_ROOMNAME)
		kakao_sendtext(SVSTATE_ROOMNAME, er)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOServerState():
	try :
		global server_token
		global super_token
		if ((current_time.minute%30) == 0 and server_token) or super_token :
			stock = [[0]*3 for _ in range(100)]
			count = 0
			option = 0
			won = 0
			message = f'{str(current_time)}\n'
			file = open("list.txt","r")
			if not file : return
			while True :
				line = file.readline()
				if not line : break
				line = line.split()
				stock[count][0] = line[0]
				try :
					stock[count][1] = yahoo_info_upd(line[0])
				except :
					stock[count][1] = [0,0,0,0,0]
				print(stock[count][1])
				stock[count][2] = int(line[1])
				count+=1
			file.close()
			currency = float(KrwUsdconv())
			for i in range (count):
				won += currency * stock[i][1][0] * stock[i][2]
				message += f'{stock[i][0]}:{stock[i][1][0]}$ ({stock[i][1][2]}%)\n'
			message += f'\ntotal : {round(won,2)}원\n 환율{round(currency,2)}'
			open_chatroom(SVSTATE_ROOMNAME)
			kakao_sendtext(SVSTATE_ROOMNAME, message)
			server_token = 0
			super_token = 0
			countdown(3)
		elif (current_time.minute%30) 	== 5 :
			server_token = 1
	except Exception as ex:
		print(f'ERROR : {ex}')

if __name__ == "__main__":
	current_time = datetime.now()
	rebootserv = "서버 재가동\n" + str(current_time)
	sendMestoKAKAO(SVSTATE_ROOMNAME,rebootserv)
	sendPricetoKAKAOServerState()
	while 1:
		try:
			current_time = datetime.now()
			print(current_time)
			judgeval("amc-entertat-hld","AMC", 0, 1.5,"💙","🔻","💎", "아이엠그라운드방")
			judgeval("gamestop-corp","GME", 1, 1.5,"💚","🔥","🚀", "아이엠그라운드방")
			judgeval("SQQQ","SQQQ", 2, 0.5,"💛","💩","🔔", "이인영", "yahoo")
			if current_time.hour >= 4 and current_time.hour < 21 and current_time.weekday() != 5 and current_time.weekday() != 6:
				sendPricetoKAKAOServerState()
		except KeyboardInterrupt as kI:
			print(f'ERROR : {kI}')
			break
		except Exception as ex:
			print(f'ERROR : {ex}')
			countdown(5)
			

