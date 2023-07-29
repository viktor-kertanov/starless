from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
import aiohttp
from random import random, randint
import ssl
from database.db_config import db_session
from database.model import MusicChart
from logs.log_config import logger

custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

async def scrape_multiple_pages(chart_objects: list[MusicChart]):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx)) as session:
        tasks = [fetch_page(session, chart.chart_url) for chart in chart_objects]
        html_contents = await asyncio.gather(*tasks)
        for el_idx, html_content in enumerate(html_contents):
            parse_page(html_content, chart_objects[el_idx])
            await asyncio.sleep(randint(2,5)+random())


async def fetch_page(session: aiohttp.ClientSession, url, rate_limit=3):
    async with asyncio.Semaphore(rate_limit):
        async with session.get(url) as response:
            return await response.text()


def parse_page(html_content, music_chart: MusicChart):
    soup = BeautifulSoup(html_content, "html.parser")
    rss_tag = soup.select_one("span.addthis-rss")
    rss_url = rss_tag.select_one("a").get("href")
    rss_url = 'https://www.besteveralbums.com/' + rss_url
    chart_resource = soup.select_one("blockquote.quote")
    chart_urls_tags = chart_resource.select("a.external")
    chart_urls = ';'.join([el.get("href") for el in chart_urls_tags]).strip()
    
    music_chart.chart_contents_url = rss_url
    music_chart.chart_external_urls = chart_urls
    music_chart.modified = datetime.utcnow()
    
    db_session.commit()
    logger.info(f'Rss url: {rss_url} [{music_chart.modified}]')


async def main():
    urls = db_session.query(MusicChart).filter(MusicChart.chart_contents_url.is_(None)).all()
    logger.info(f"Overal charts: {len(urls)}")
    await scrape_multiple_pages(urls)


if __name__ == '__main__':
    asyncio.run(main())

    print('Hello world')
