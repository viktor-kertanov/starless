from youtube_api.classes import SearchApi, VideoApiRequest
from database.db_config import db_session
from database.model import ChartRelease, Track, MusicChart, Playlist, YoutubeMatch

playlist_id = '4349aaa7-3d62-4732-846c-d99860d6a02d'

pl_tracks = db_session.query(Playlist).filter(Playlist.playlist_id == playlist_id).all()

track = pl_tracks[1]
metadata = f"{track.track.release.release_artist} - {track.track.track_title}"
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
        match_rate = None

    )





if __name__ == '__main__':

    print('Hello world')


