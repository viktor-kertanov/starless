from youtube_api.classes import PlaylistApiRequest, VideoApiRequest
from google_services.google_sheets.read_sheets import read_google_sheet
from config import settings
import pandas as pd
from datetime import datetime, timedelta


if __name__ == '__main__':
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_pl = "playlists"
    google_sheet_videos = "videos"

    input_sheet_data = read_google_sheet(google_sheet_id, google_sheet_pl)
    deduped = input_sheet_data.drop_duplicates(subset='playlist_url', keep='first')
    
    deduped['date_processed'] = pd.to_datetime(deduped['date_processed'])

    threshold_date = datetime.now() - timedelta(days=365)
    filtered_df = deduped[deduped['date_processed'] < threshold_date]

    pl_ids = list(filtered_df['playlist_url'])
    pl = PlaylistApiRequest(pl_ids)
    pl_data = pl.get_pl_info_and_video_ids()

    video_ids = []
    for playlist in pl_data:
        pl_video_ids = playlist["video_ids"]
        video_ids += pl_video_ids
    
    video_ids = list(set(video_ids))

    video_data_instance = VideoApiRequest(pl_video_ids)
    video_data = video_data_instance.get_video_data()

    print('Hello world')
