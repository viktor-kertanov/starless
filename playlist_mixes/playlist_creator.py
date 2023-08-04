from database.model import ChartRelease, Track, MusicChart, Playlist
from database.db_config import db_session
from sqlalchemy import func, text
from random import sample
from config import logger
import uuid

def set_random_seed(random_seed_value: float) -> None:
    query = text(f"SELECT setseed({random_seed_value})")
    db_session.execute(query)


def create_playlist():
    # random_chart = db_session.query(MusicChart).filter(MusicChart.chart_by == 'VISIONS').order_by(func.random()).limit(1).first()
    random_chart = db_session.query(MusicChart).order_by(func.random()).limit(1).first()

    print(random_chart)
    releases_in_chart = db_session.query(ChartRelease).filter(ChartRelease.chart_id == random_chart.id).all()
    
    num_releases_in_mix = 10

    chart_sample = sample(releases_in_chart, num_releases_in_mix)
    
    playlist_uuid = uuid.uuid4()

    tracks_for_mix = []
    for el_idx, el in enumerate(chart_sample, start=1):
        logger.info(f"{el_idx}. {el.release.release_metadata}")
        track_choice = db_session.query(Track).filter(Track.release_id == el.release_id).order_by(func.random()).limit(1).first()
        tracks_for_mix.append(track_choice)
        playlist_element = Playlist(playlist_id=playlist_uuid, track_id=track_choice.id)
        db_session.add(playlist_element)
    db_session.commit()



if __name__ == '__main__':
    create_playlist()
    print('Hello world!')


