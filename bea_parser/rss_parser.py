from bs4 import BeautifulSoup
from random import random, randint
from database.db_config import db_session
from database.model import MusicChart, Release, ReleaseChart
from logs.log_config import logger
from sqlalchemy.exc import IntegrityError
import asyncio
import ssl
import aiohttp
from time import time
import uuid
import csv


custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

async def scrape_multiple_pages(charts: list[MusicChart]):
    tasks = [fetch_page(chart.chart_contents_url) for chart in charts]
    html_contents = await asyncio.gather(*tasks)
    for idx, html_content in enumerate(html_contents):
        parse_page(html_content, charts[idx].id)
        await asyncio.sleep(randint(3, 5)+random()+random()*0.1)


async def fetch_page(url, rate_limit=3):
    async with asyncio.Semaphore(rate_limit):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx)) as session:
            async with session.get(url) as response:
                return await response.text()


def parse_page(html_content, chart_id):
    soup = BeautifulSoup(html_content, 'lxml')
    logger.info(f'Parsing {chart_id}')
    releases = soup.select('item')
    for rls in releases:
        full_metadata = rls.select_one('title').text
        position  = int(full_metadata.split('. ')[0])
        full_metadata = '. '.join(full_metadata.split('. ')[1:])
        if len(full_metadata.split(' - ')) > 2:
            risky_metadata = True
        else:
            risky_metadata = False
        
        artist = full_metadata.split(' - ')[-1]
        release_title = ' - '.join(full_metadata.split(' - ')[:-1])
        
        release_url = rls.select_one('a').get("href")
        release_url = 'https://www.besteveralbums.com' + release_url
        try:
            art_cover_url = rls.select_one('source[type="image/jpeg"]').get('data-srcset', None)
        except AttributeError:
            art_cover_url_tag = rls.select_one('img.albumart-bar')
            if art_cover_url_tag:
                art_cover_url = art_cover_url_tag.get('src', None)
            else:
                art_cover_url = None

        release_id = uuid.uuid4()
        release_data_row = {
            "id": release_id,
            "release_metadata": full_metadata,
            "release_artist": artist,
            "release_title": release_title,
            "release_url": release_url,
            "risky_metadata": risky_metadata,
            "album_art_url": art_cover_url,
        }
        try:
            db_session.add(Release(**release_data_row))
            db_session.commit()
        
        except IntegrityError:
            db_session.rollback()
            logger.info(f"IN THE SYSTEM:: Release: {full_metadata}")
            release_id = db_session.query(Release).filter(Release.release_metadata == full_metadata).first().id

        db_session.add(ReleaseChart(release_id=release_id, chart_id=chart_id, position=position))
        db_session.commit()


    processed = []
    with open('bea_parser/data/charts_processed.csv', 'r') as file:
        data = csv.reader(file)
        [processed.append(row[0]) for row in data]
    
    processed.append(chart_id)
    
    with open('bea_parser/data/charts_processed.csv', 'w') as file:
        writer = csv.writer(file)
        for value in processed:
            writer.writerow([value])


async def main():
    batch_size = 10
    offset = 0
    batch_idx = 1
    
    processed = []
    with open('bea_parser/data/charts_processed.csv', 'r') as file:
        data = csv.reader(file)
        charts = [processed.append(row[0]) for row in data]

    while True:
        start_time = time()

        charts = db_session.query(MusicChart).filter(~MusicChart.id.in_(processed)).order_by(MusicChart.created).offset(offset).limit(batch_size).all()
        logger.info(f'There are {len(charts)} to process.')

        if not charts:
            break

        chart_objects = [el for el in charts]

        await scrape_multiple_pages(chart_objects)

        end_time = time()
        elapsed_time = end_time - start_time
        logger.info(f"Batch # {batch_idx}. Time taken: {elapsed_time:.2f} seconds")

        offset += batch_size
        batch_idx += 1




if __name__ == '__main__':
    asyncio.run(main())    
    
    print('Hello world.')