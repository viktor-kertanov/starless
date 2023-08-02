from database.db_config import db_session
from database.model import Release, Track
from sqlalchemy import func, and_

# Duplicate release have a problem: they appear on different charts
duplicates_query = db_session.query(
        Track.release_id, Track.track_title, Track.idx_in_release, Track.user_avg_rating, Track.user_num_votes, func.count()
    ).group_by(
        Track.release_id, Track.track_title, Track.idx_in_release, Track.user_avg_rating, Track.user_num_votes
    ).having(func.count() > 1)

duplicates = duplicates_query.order_by(Track.release_id, Track.idx_in_release).all()

for rls_id, title, idx_in_rls, usr_avg_rating, usr_num_votes, count in duplicates:
    print(f"{rls_id}. {idx_in_rls}. {title}::{usr_avg_rating}::{usr_num_votes} Count: {count}")
    track_to_delete = db_session.query(Track).filter(and_(
        Track.release_id == rls_id,
        Track.track_title == title,
        Track.idx_in_release == idx_in_rls,
        Track.user_avg_rating == usr_avg_rating,
        Track.user_num_votes == usr_num_votes
    )).first()
    db_session.delete(track_to_delete)
    db_session.commit()



# filtered_releases = db_session.query(Release).filter(and_(Release.in_num_charts > 30, Release.num_favourites == 0)).all()

# for el in filtered_releases:
#     print(el)