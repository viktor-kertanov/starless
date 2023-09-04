from youtube_api.classes import SearchApi, VideoApiRequest
from database.db_config import db_session
from database.model import ChartRelease, Track, MusicChart, Playlist, YoutubeMatch
from fuzzywuzzy import fuzz, process
from config import settings, logger

playlist_id = '28ac763d-34e6-488c-ada2-d0e0e6016133'

pl_tracks = db_session.query(Playlist).filter(Playlist.playlist_id == playlist_id).all()

for track in pl_tracks:
    if db_session.query(YoutubeMatch).filter(YoutubeMatch.track_id == track.track_id).all():
        logger.info("Track ID: %s already in the match table", track.track_id)
        continue
    metadata = track.original_metadata
    print(metadata)

    search = SearchApi(metadata)
    search_results = search.get_search_results()
    search_video_ids = [el["id"]["videoId"] for el in search_results  if el["id"]["kind"] == 'youtube#video']

    video_data_inst = VideoApiRequest(search_video_ids)
    video_data = video_data_inst.get_video_data(get_channel_data=True)

    for match_idx, match in enumerate(video_data):
        youtube_match = YoutubeMatch(
            track_id = track.track_id,
            idx_in_search = match_idx,
            yt_video_id = match.id,
            yt_metadata = match.original_metadata,
            duration = match.length,
            yt_category = match.video_category,
            channel_id = match.channel_id,
            channel_name = match.relevant_channel_info.title,
            match_rate = fuzz.ratio(track.original_metadata.lower(), match.original_metadata.lower())
        )
        db_session.add(youtube_match)

    db_session.commit()





if __name__ == '__main__':

    print('Hello world')


