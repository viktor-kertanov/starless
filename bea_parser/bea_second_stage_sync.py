from bs4 import BeautifulSoup
from datetime import datetime
from random import random, randint
import ssl
from database.db_config import db_session
from database.model import MusicChart
from logs.log_config import logger
import requests
from sqlalchemy.exc import IntegrityError

custom_ca_bundle_path = 'certificates/certificate.pem'
ssl_ctx = ssl.create_default_context(cafile=custom_ca_bundle_path)

def main():
    charts = db_session.query(MusicChart).filter(MusicChart.chart_contents_url.is_(None)).all()
    with requests.Session() as session:
        for music_chart in charts:
            html_content = session.get(music_chart.chart_url).content
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
            try:
                db_session.commit()
            except IntegrityError:
                db_session.rollback()
                db_session.delete(music_chart)
                db_session.commit()
                logger.debug(f'ROW DELETED: {music_chart}. ID: {music_chart.id}')
            logger.info(f'Rss url: {rss_url} [{music_chart.modified}]')

if __name__ == '__main__':
    main()

    print('Hello world')
