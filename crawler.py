import pycurl
import cStringIO
import datetime
import os
import time
import sys
from lxml import html
from twilio.rest import Client
from targets import target

agents = {"reddit" : os.environ['reddituseragent']}
iteration = 0
target_titles = []
cont = True
failures = 0
targets = [target(['GTX', '1080']), target(['[SSD]'])]
query = '//a[@class="title may-blank outbound"]/text()'
url = 'https://www.reddit.com/r/buildapcsales/new/'

def getPage(url, website):
	html_raw = cStringIO.StringIO()
	c_opt = pycurl.Curl()
	c_opt.setopt(pycurl.USERAGENT, agents.get(website, ''))
	c_opt.setopt(pycurl.URL, url)
	c_opt.setopt(pycurl.WRITEFUNCTION, html_raw.write)
	
	try:
		c_opt.perform()
	except Exception as e:
		log = open('log.txt', 'a')
		entry = str(datetime.now())
		log.write(''.join([entry, str(e)]))
		failures = failures + 1

	return html_raw.getvalue()

def getPrice(html_raw, website):
	if len(html_raw) < 50000 and iteration % 10 == 0:
		sendText("Odd html received, maybe blocked?")
		failures = failures + 1
		if failures > 50:
			cont = False
			sendText("Quitting program, too many failures")

	else:
		tree = html.fromstring(html_raw)
		titles = tree.xpath(query)
		for target in targets:
			for t in titles:
				if all(cond_words in t for cond_words in target.title_conditions):
					if t not in target_titles:			
						target_titles.append(t)
						if iteration > 2:
							sendText("New deal posted matching criteria: " + t)

def sendText(message):
	account_sid = os.environ['twiliosid']
	auth_token = os.environ['twiliotoken']
	client = Client(account_sid, auth_token)

	message = client.api.account.messages.create(to=os.environ['myphone'],
	                                             from_=os.environ['twiliophone'],
	  	                                         body=message)
	print "Text sent!"

if len(sys.argv)> 3:
	url = 'https://www.reddit.com/r/test/'
	query = '//a[@class="title may-blank "]/text()'
while cont:
	iteration = iteration + 1
	print iteration
	getPrice(getPage(url, 'reddit'), 'reddit')
	time.sleep(8.5)

