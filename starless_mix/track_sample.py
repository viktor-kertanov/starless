from database.model import Release, ChartRelease, Track, MusicChart
from database.db_config import db_session
from sqlalchemy import func, text
from random import sample
from config import logger
from youtube_api.classes import SearchApi, VideoApiRequest

if __name__ == '__main__':
    random_seed = 0.669
    query = text(f"SELECT setseed({random_seed})")
    db_session.execute(query)
    random_chart = db_session.query(MusicChart).filter(MusicChart.chart_by == 'VISIONS').order_by(func.random()).limit(1).first()

    print(random_chart)
    releases_in_chart = db_session.query(ChartRelease).filter(ChartRelease.chart_id == random_chart.id).all()
    
    # for el_idx, el in enumerate(releases_in_chart, start=1):
    #     print(f"{el_idx}. {el.release.release_metadata}")
    
    num_releases_in_mix = 10

    chart_sample = sample(releases_in_chart, num_releases_in_mix)
    
    tracks_for_mix = []
    for el_idx, el in enumerate(chart_sample, start=1):
        # logger.info(f"{el_idx}. {el.release.release_metadata}")
        track_choice = db_session.query(Track).filter(Track.release_id == el.release_id).order_by(func.random()).limit(1).first()
        tracks_for_mix.append(track_choice)
    
    for idx, el in enumerate(tracks_for_mix, start=1):
        logger.info(f"{idx}. {el}")
    
    
    


    
    


    print('Hello world!')


