from bs4 import BeautifulSoup
from random import random, randint
from database.db_config import db_session
from database.model import MusicChart, Release, ChartRelease
from logs.log_config import logger
from sqlalchemy.exc import IntegrityError
import asyncio
import ssl
import aiohttp
from time import time
import uuid
import csv
import uuid
import requests

req = requests.get("https://www.besteveralbums.com/thechart.php?a=62670").content
soup = BeautifulSoup(req, "html.parser")

track_raw_data = soup.select('div[id="tracks_div"] div.item-row')

ranks_data = soup.select('table.ranks-table tfoot.charthead th.chartnumber')
ranks_data = [int(el.text) for el in ranks_data]
num_charts = ranks_data[0]
total_rank = ranks_data[1]

in_favourites = int(soup.select_one("div[id='div_fav']").text.split('Showing all ')[1].split(' ')[0])

num_ratings = int(soup.select_one('div[id="div_rat"] a.nav2').text.split('Show all ')[1].split(' ')[0])



rating_section = soup.select_one('div[id="div_rat"]')
paragraph_with_data = rating_section.find_next_sibling('p')
tag_to_delete = paragraph_with_data.select_one("span.smallerbody")
tag_to_delete.decompose()
stats_literal_data = paragraph_with_data.text

bayes_avg = float(stats_literal_data.split('a Bayesian average rating of ')[1].split('/')[0])
mean_avg = float(stats_literal_data.split('a mean average of ')[1].split('/')[0])
std_rating = float(stats_literal_data.split('The standard deviation for this album is ')[1].split('.')[0])




mean_std_data = soup.select('table.ranks-table tfoot.charthead th.chartnumber')

track_data = []
for track in track_raw_data:
    position_in_release = int(track.select_one('.chartnumber').text.replace('.', ''))
    track_name = track.select_one('a.nav2emph').text.strip()
    rating_data = track.select_one('span.track-list-ave').text.replace('Rating:\xa0', '')

    average_rating = float(rating_data.split(' (')[0])
    num_votes = int(rating_data.split(' (')[-1].split(' vote')[0])

    row = {
        "track_title": track_name,
        "idx_in_release": position_in_release,
        "user_avg_rating": average_rating,
        "user_num_votes": num_votes,

    }


if __name__ == '__main__':

    print('Hello world!')