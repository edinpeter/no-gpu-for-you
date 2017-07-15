import pycurl
import cStringIO
import datetime
import os
import time
from lxml import html
from twilio.rest import Client

agents = {"reddit" : os.environ['reddituseragent']}
iteration = 0
gpu_titles = []
cont = True
failures = 0

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
	if len(html_raw) < 50000 and iteration % 80 == 0:
		sendText("Odd html received, maybe blocked?")
		failures = failures + 1
		if failures > 50:
			cont = False
			sendText("Quitting program, too many failures")

	else:
		tree = html.fromstring(html_raw)
		titles = tree.xpath('//a[@class="title may-blank outbound"]/text()')

		for t in titles:
			if "[GPU]" in t and "1080" in t:
				if t not in gpu_titles:			
					gpu_titles.append(t)
					if iteration > 10:
						sendText("New gtx 1080 deal posted on reddit: " + t)

def sendText(message):
	account_sid = os.environ['twiliosid']
	auth_token = os.environ['twiliotoken']
	client = Client(account_sid, auth_token)

	message = client.api.account.messages.create(to=os.environ['myphone'],
	                                             from_=os.environ['twiliophone'],
	  	                                         body=message)
	print "Text sent!"

while cont:
	iteration = iteration + 1
	print iteration
	getPrice(getPage('https://www.reddit.com/r/buildapcsales/new/', 'reddit'), 'reddit')
	time.sleep(8.5)

