from database.model import Release, ChartRelease, Track, MusicChart
from database.db_config import db_session
from sqlalchemy import func, text
from random import sample


if __name__ == '__main__':
    random_seed = 0.669
    query = text(f"SELECT setseed({random_seed})")
    db_session.execute(query)
    random_chart = db_session.query(MusicChart).order_by(func.random()).limit(1).first()

    print(random_chart)
    releases_in_chart = db_session.query(ChartRelease).filter(ChartRelease.chart_id == random_chart.id).all()
    
    # for el_idx, el in enumerate(releases_in_chart, start=1):
    #     print(f"{el_idx}. {el.release.release_metadata}")
    
    num_releases_in_mix = 10

    chart_sample = sample(releases_in_chart, num_releases_in_mix)
    
    for el_idx, el in enumerate(chart_sample, start=1):
        print(f"{el_idx}. {el.release.release_metadata}")
    
    

    print('Hello world!')


