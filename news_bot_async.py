import yaml
import time
import re
import requests
from bs4 import BeautifulSoup as bs
import fake_useragent as fua
import random
import datetime
import asyncio
import aiohttp

async def get_url_page(session, target_url):
    ua = fua.UserAgent()
    ua.safari
    try:
        async with session.get(target_url, headers={'User-Agent': ua.safari}, timeout=120) as response:
            assert response.status == 200
            response_text = await response.text()
            bs_site = bs(response_text, 'html.parser')
            try:
                links = bs_site.find_all('a')
            except:
                return 0
            for link in links:
                if re.findall('.*ростелеком|\Wртк|^ртк|\s+цод|^цод|\Wсолар|осиевск.*', str(link).lower()):
                    if link['href'].startswith('https://'):
                        message_text = link['href']
                    else:
                        message_text = target_url + link['href']
                    send_new_message(message_text)
    except:
        print(f'[ERROR] Site processing is unsuccessful {target_url}')
        return 0
#     print(f'[INFO] Site processing is successful {target_url}')

async def gather_data():
    targets = []
    with open('smi_list.txt', 'r') as smi_list:
        line = smi_list.readline().replace('\n','')
        while line:
            if not line.startswith('#'):
                targets.append(line)
            line = smi_list.readline().replace('\n','')
    async with aiohttp.ClientSession() as session:
        tasks = []
        for target in targets:
            task = asyncio.create_task(get_url_page(session, target))
            tasks.append(task)
        await asyncio.gather(*tasks)

def send_new_message(message_text):
    message_text = str(message_text)
    news = datetime.datetime.now().date().strftime('%d.%m.%Y') + ': ' + message_text
    with open('urls_news.txt', 'r') as was_sent:
        line = was_sent.readline()
        while line:
            if re.findall('.*' + message_text + '.*', line):
                return 0
            line = was_sent.readline()
        with open('urls_news.txt', 'a') as was_sent:
            was_sent.write(str(news) + '\n')
    with open('tlgr.yml') as conf:
        my_params = yaml.safe_load(conf)
    tgApiSend = 'https://api.telegram.org/bot' + my_params['tkn'] + '/sendMessage'
    payload = dict(chat_id=my_params['chat_id'], text=message_text)
    requests.post(tgApiSend, data=payload)

def main():
    time_sleep = random.randint(0, 18)
    asyncio.run(gather_data())

if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f'Затраченное время {round(time.time() - start_time, 1)} сек.')
