from bs4 import BeautifulSoup
from random import random, randint
from database.db_config import db_session
from database.model import MusicChart, Release, ChartRelease, Track
from logs.log_config import logger
from sqlalchemy.exc import IntegrityError
import asyncio
import ssl
import aiohttp
from time import time
import uuid
import csv
from datetime import datetime
import re
from utils.backoff import backoff


custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

async def scrape_multiple_pages(releases: list[Release]):
    tasks = [fetch_page(rls.release_url) for rls in releases]
    html_contents = await asyncio.gather(*tasks)
    for idx, html_content in enumerate(html_contents):
        parse_page(html_content, releases[idx])
        await asyncio.sleep(random()+random()*0.1)


async def fetch_page(url, rate_limit=5):
    async with asyncio.Semaphore(rate_limit):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx)) as session:
            async with session.get(url) as response:
                return await response.text()


def parse_page(html_content, input_release: Release):
    soup = BeautifulSoup(html_content, "html.parser")

    warning = soup.select_one('div.bea-content p.alert-warning')
    if warning:
        warn_text = warning.text
    else:
        warn_text = ''
    if 'has been deleted and merged with' in warn_text:
        new_href = warning.select_one('a.nav2').get('href')
        new_href = 'https://www.besteveralbums.com' + new_href

        logger.info(f"There's no release {input_release} via {input_release.release_url}")
        logger.info(f"New url for this release is: {new_href}")
        input_release.release_url = new_href
        db_session.commit()
        return 

    release_year_tag = soup.select_one('span[itemprop="copyrightYear"]')
    try:
        release_year = int(release_year_tag.text.split('Year: ')[-1].strip())
    except (ValueError, AttributeError):
        release_year = 0
    
    try:
        release_date = release_year_tag.find_next_sibling("b").next_sibling.strip()
        release_date = datetime.strptime(release_date, '%Y-%m-%d')
    except:
        release_date = None


    ranks_data = soup.select('table.ranks-table tfoot.charthead th.chartnumber')
    ranks_data = [int(el.text.replace(',', '')) for el in ranks_data]
    try:
        num_charts = ranks_data[0] 
    except IndexError:
        num_charts = None
    try:
        total_rank = ranks_data [1]
    except IndexError:
        total_rank = None
    try:
        fav_text = soup.select_one("div[id='div_fav']").text
        match = re.search(r'(Show(?:ing)?) all (\d+)', fav_text)
    except AttributeError:
        match = None

    if match:
        prefix = match.group(1)
        in_favourites = int(match.group(2))
    else:
        in_favourites = 0

    try:
        num_ratings_tag = soup.select_one('div.star-caption-average').text
        num_ratings = int(num_ratings_tag.split('(from ')[-1].split(' ')[0].replace(',', ''))
    except AttributeError:
        num_ratings = None
    # num_ratings = int(soup.select_one('div[id="div_rat"] a.nav2').text.split('Show all ')[1].split(' ')[0])

    rating_section = soup.select_one('div[id="div_rat"]')
    paragraph_with_data = rating_section.find_next_sibling('p')
    if 'Rating metrics' in paragraph_with_data.text:
        tag_to_delete = paragraph_with_data.select_one("span.smallerbody")
        tag_to_delete.decompose()
        stats_literal_data = paragraph_with_data.text
        try:
            top_percentile = float(stats_literal_data.split('This album is rated in the top ')[1].split('%')[0])
        except:
            top_percentile = None
        
        bayes_avg = float(stats_literal_data.split('a Bayesian average rating of ')[1].split('/')[0])
        mean_avg = float(stats_literal_data.split('a mean average of ')[1].split('/')[0])
        standard_deviation = float(stats_literal_data.split('The standard deviation for this album is ')[1][:-1])

    else:
        top_percentile = None
        bayes_avg = None
        mean_avg = None
        standard_deviation = None

    release_obtained_data = {
        "release_year": release_year,
        "release_date": release_date,
        "in_num_charts": num_charts,
        "total_ranking": total_rank,
        "num_ratings": num_ratings,
        "top_percentile": top_percentile,
        "bayes_avg_rating": bayes_avg,
        "mean_avg_rating": mean_avg,
        "std_rating": standard_deviation,
        "num_favourites": in_favourites,
        "modified": datetime.utcnow()
    }

    for attr, value in release_obtained_data.items():
        setattr(input_release, attr, value)

    db_session.commit()
    

    track_raw_data = soup.select('div[id="tracks_div"] div.item-row')
    track_data = []
    for track in track_raw_data:
        position_in_release = int(track.select_one('.chartnumber').text.replace('.', ''))
        track_name = track.select_one('a.nav2emph').text.strip()
        rating_data = track.select_one('span.track-list-ave').text.replace('Rating:\xa0', '')

        average_rating = (lambda x: None if x=='Not enough data' else float(x))(rating_data.split(' (')[0])
        num_votes = (lambda x: 0 if x=='Not enough data' else int(x))(rating_data.split(' (')[-1].split(' vote')[0].replace(',', ''))

        track_row = {
            "release_id": input_release.id,
            "track_title": track_name,
            "idx_in_release": position_in_release,
            "user_avg_rating": average_rating,
            "user_num_votes": num_votes,

        }
        track_data.append(track_row)
    
    try:
        db_session.bulk_insert_mappings(Track, track_data, return_defaults=True)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    
    

@backoff(start_sleep_time=0.2, factor=2, border_sleep_time=50)
async def main():
    batch_size = 10
    offset = 0
    batch_idx = 1

    while True:
        start_time = time()

        releases = db_session.query(Release).filter(Release.release_year.is_(None)).order_by(Release.created).offset(offset).limit(batch_size).all()

        if not releases:
            break

        release_objects = [el for el in releases]

        await scrape_multiple_pages(release_objects)

        end_time = time()
        elapsed_time = end_time - start_time
        logger.info(f"Batch # {batch_idx}. Time taken: {elapsed_time:.2f} seconds")

        offset += batch_size
        batch_idx += 1




if __name__ == '__main__':
    asyncio.run(main())    
    
    print('Hello world.')