import yaml
import time
import re
import requests
from bs4 import BeautifulSoup as bs
import fake_useragent as fua
import random
import datetime

def send_new_message(message_text):
    message_text = str(message_text)
    with open('tlgr.yml') as conf:
        my_params = yaml.safe_load(conf)
    tgApiSend = 'https://api.telegram.org/bot' + my_params['tkn'] + '/sendMessage'
    payload = dict(chat_id=my_params['chat_id'], text=message_text)
    news = datetime.datetime.now().date().strftime('%d.%m.%Y') + ': ' + message_text
    with open('urls_news.txt', 'r') as was_sent:
        line = was_sent.readline()
        while line:
            if re.findall('.*' + message_text + '.*', line):
                return 0
            line = was_sent.readline()
    with open('urls_news.txt', 'a') as was_sent:
        was_sent.write(str(news) + '\n')
    req = requests.post(tgApiSend, data=payload)

def scan_sites():
    targets = []
    with open('smi_list.txt', 'r') as smi_list:
        line = smi_list.readline().replace('\n','')
        while line:
            if not line.startswith('#'):
                targets.append(line)
            line = smi_list.readline().replace('\n','')
    ua = fua.UserAgent()
    with requests.Session() as session:
        for target in targets:
            try:
                response = session.get(target, headers={'User-Agent': ua.safari}, timeout=120)
            except:
                continue
            if response.status_code == requests.codes.ok:
#                 print(target, 'OK')
                bs_site = bs(response.content, 'html.parser')
            else:
                print(f'{target} not ok(')
            try:
                links = bs_site.find_all('a')
            except:
                continue
            for link in links:
                if re.findall('.*ростелеком|\Wртк|^ртк|\s+цод|^цод|\Wсолар|осиевск.*', str(link).lower()):
                    if link['href'].startswith('https://'):
                        message_text = link['href']
                    else:
                        message_text = target + link['href']
                    send_new_message(message_text)

def main():
    scan_sites()

if __name__ == '__main__':
    time_sleep = random.randint(0, 10)
    time.sleep(time_sleep)
    start = time.time()
    main()
    print(f'Затраченное время: {round(time.time() - start, 1)} сек.')
