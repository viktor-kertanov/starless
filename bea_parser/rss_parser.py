from bs4 import BeautifulSoup
from datetime import datetime
from random import random, randint
from database.db_config import db_session
from database.model import MusicChart
from logs.log_config import logger
import requests
from sqlalchemy.exc import IntegrityError
import asyncio
import ssl
import json
from json import JSONDecodeError
import aiohttp


custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

async def scrape_multiple_pages(urls):
    tasks = [fetch_page(url) for url in urls]
    html_contents = await asyncio.gather(*tasks)
    for html_content in html_contents:
        parse_page(html_content)
        await asyncio.sleep(randint(2,4)+random())


async def fetch_page(url, rate_limit=3):
    async with asyncio.Semaphore(rate_limit):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx)) as session:
            async with session.get(url) as response:
                return await response.text()


def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'xml')
    releases = soup.select('item')

    try:
        with open('charts.json', 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, JSONDecodeError):
        existing_data = []

    # existing_data.extend(chart_full_data)

    # with open('charts.json', 'w', encoding='utf-8') as file:
    #     json.dump(existing_data, file, indent=4, ensure_ascii=False)


async def main(charts: list[MusicChart]):
    rss_urls = [el.chart_contents_url for el in charts]

    await scrape_multiple_pages(rss_urls)


if __name__ == '__main__':
    # charts = db_session.query(MusicChart).all()[:10]
    # asyncio.run(main(charts))

    req = requests.get('https://www.besteveralbums.com/feeds/BestEverAlbumsdotCom_Boomkat_BestAlbumsOf2022.xml')
    soup = BeautifulSoup(req.content, 'xml')
    releases = soup.select('item')

    print('Hello world.')