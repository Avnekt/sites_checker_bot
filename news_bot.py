import yaml
import time
import re
import requests
from bs4 import BeautifulSoup as bs
import fake_useragent as fua
import random
import datetime
#import sqlite3

start = time.time()

with open('tlgr.yml') as conf:
    my_params = yaml.safe_load(conf)
#print(my_params)
tgApiSend = 'https://api.telegram.org/bot' + my_params['tkn'] + '/sendMessage'
payload = dict(chat_id=my_params['chat_id'])

time_sleep = random.randint(0, 10)

targets = []
with open('smi_list.txt', 'r') as smi_list:
    line = smi_list.readline().replace('\n','')
    while line:
        targets.append(line)
        line = smi_list.readline().replace('\n','')

ua = fua.UserAgent()
ua.safari

s = requests.Session()
time.sleep(time_sleep)

for target in targets:
    try:
        response = s.get(target, headers={'User-Agent': ua.safari}, timeout=30)
    except:
        continue
    if response.status_code == requests.codes.ok:
        print(target, 'OK')
        bs_site = bs(response.content, 'html.parser')
        #for key, value in response.request.headers.items():
            #print(key+": "+value)
        #print(response)
    else:
        print('Not ok(')
        #with open('1.html', 'w') as out_file:
            #out_file.write(response.text)
        print(i)
    try:
        links = bs_site.find_all('a')
    except:
        continue
    for link in links:
        if re.findall('.*ростелеком|ртк|цод|солар|осиевск.*', str(link).lower()):
            if link['href'].startswith('https://'):
                #print(link['href'])
                message_text = link['href']
            else:
                #print(target + link['href'])
                message_text = target + link['href']
            message_text = str(message_text)
            news = {'date': datetime.datetime.now().date().strftime('%d.%m.%Y'), 'url': message_text}
            do_not_send = False
            with open('urls_news.txt', 'r') as was_sent:
                line = was_sent.readline()
                while line:
                    if re.findall('.*' + message_text + '.*', line):
                        do_not_send = True
                    line = was_sent.readline()
            if do_not_send:
                continue
            with open('urls_news.txt', 'a') as was_sent:
                was_sent.write(str(news) + '\n')
            payload['text'] = str(message_text)
            req = requests.post(tgApiSend, data=payload)
            #time.sleep(2)
            print(req)
            break
#payload['text'] = 'news_bot is alive!'
#req = requests.post(tgApiSend, data=payload)
print(f'Затраченное время: {round(time.time() - start, 1)} сек.')
