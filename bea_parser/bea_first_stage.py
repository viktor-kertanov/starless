from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
import aiohttp
from random import random, randint
import json
from json import JSONDecodeError
import ssl

custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

async def scrape_multiple_pages(urls):
    tasks = [fetch_page(url) for url in urls]
    html_contents = await asyncio.gather(*tasks)
    for html_content in html_contents:
        parse_page(html_content)
        await asyncio.sleep(randint(3,7)+random())


async def fetch_page(url, rate_limit=3):
    async with asyncio.Semaphore(rate_limit):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx)) as session:
            async with session.get(url) as response:
                return await response.text()


def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    charts = [tag for tag in soup.select('tr')]
    chart_full_data = []
    for tag_idx, tag in enumerate(charts):
        if not tag.select_one('th b a'):
            continue
        chart_by = tag.select('th b')[-1].get_text(strip=True)
        
        chart_year = tag.select_one('th').get_text(strip=True)
        chart_year = int(chart_year.split('(')[-1].split(')')[0])
        
        chart_data =  tag.select_one('th b a')
        chart_url = chart_data.get("href", None)
        if chart_url:
            chart_url = 'https://www.besteveralbums.com' + chart_url
        chart_name = chart_data.get_text(strip=True)
        chart_description = charts[tag_idx+1].get_text(strip=True)
        row = {
            "chart_name": chart_name,
            "chart_by": chart_by,
            "chart_description": chart_description,
            "chart_year": chart_year,
            "chart_url": chart_url,
            "chart_contents_url": None,
            "chart_publication_date": None,
            "created": str(datetime.utcnow()),
            "modified": str(datetime.utcnow())
        }
        chart_full_data.append(row)

    try:
        with open('charts.json', 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, JSONDecodeError):
        existing_data = []

    existing_data.extend(chart_full_data)

    with open('charts.json', 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)


async def main():
    url = 'https://www.besteveralbums.com/thechart.php'
    url += '?src=recognised&ct=All&ctv=All&orderby=DateCreated&sortdir=desc&page='
    max_page = 355
    urls = [url + str(el) for el in range(1, max_page + 1)]

    await scrape_multiple_pages(urls)


if __name__ == '__main__':
   asyncio.run(main())
   print('Hello world')
