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
import logging

FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'
logging.basicConfig(
    level=logging.INFO,
    filename='news_bot.log',
    filemode='w',
    format=FORMAT
)

async def get_url_page(session, target_url, conf):
    pattern = conf['pattern']
    ua = fua.UserAgent()
    ua.safari
    try:
        async with session.get(target_url, headers={'User-Agent': ua.safari}, timeout=40) as response:
            logging.info(f'Sent request to {target_url}')
            assert response.status == 200, logging.warning(f'{target_url} status is {response.status}')
            response_text = await response.text()
            bs_site = bs(response_text, 'html.parser')
            try:
                links = bs_site.find_all('a')
            except:
                return 0
            for link in links:
                if re.findall(f'{str(pattern)}', str(link).lower()):
                    if link['href'].startswith('https://') or link['href'].startswith('http://'):
                        message_text = link['href']
                    else:
                        message_text = target_url + link['href']
                    send_new_message(message_text, conf)
    except Exception as e:
        logging.warning(f'{target_url}: {e}')
        return 0
    logging.info(f'{target_url} finished successful')
    return 1

async def gather_data(conf):
    targets = []
    for site in conf['sites_list']:
        if site:
            targets.append(site)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for target in targets:
            for _ in range(2):
                task = asyncio.create_task(get_url_page(session, target, conf))
                if task != 0:
                    tasks.append(task)
                    break
        await asyncio.gather(*tasks)

def send_new_message(message_text, my_params):
    message_text = str(message_text)
    news = datetime.datetime.now().date().strftime('%d.%m.%Y') + ': ' + message_text
    with open('urls_news.txt', 'r') as was_sent:
        line = was_sent.readline()
        while line:
            if message_text in line:
                return 0
            line = was_sent.readline()
        with open('urls_news.txt', 'a') as was_sent:
            was_sent.write(str(news) + '\n')
    tgApiSend = 'https://api.telegram.org/bot' + my_params['tkn'] + '/sendMessage'
    payload = dict(chat_id=my_params['chat_id'], text=message_text)
    requests.post(tgApiSend, data=payload)

def main(params):
    start_time = time.time()
    logging.warning(f'Starts script at {start_time}')
    asyncio.run(gather_data(params))
    logging.warning(f'Spended time is {round(time.time() - start_time, 1)} sec')

if __name__ == '__main__':
    with open('config.yml') as conf:
        my_params = yaml.safe_load(conf)
    main(my_params)
