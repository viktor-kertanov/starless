from config import settings
from google_services.google_sheets.read_sheets import read_google_sheet
from random import sample
import os
from sample_machine.yt_dl import dl_yt_as_mp3
from logs.log_config import logger

def get_existing_files(directory: str = settings.audio_lib):
    file_list = os.listdir(directory)
    file_list = [f for f in file_list if os.path.isfile(os.path.join(directory, f)) if not f.startswith('.')]
    video_ids = [el.split('_id_')[0] for el in file_list]

    return video_ids


def get_videos_from_google_sheet(
        sample_size: int = 100,
        sheetname: str = "videos",
        column_name: str = "video_id",
        filter_by_cnl_id: str = None
    ):
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_videos = sheetname

    videos_exist = read_google_sheet(google_sheet_id, google_sheet_videos)
    if filter_by_cnl_id:
        videos_exist = videos_exist[videos_exist["cnl_id"] == filter_by_cnl_id]
    existing_video_ids = set(videos_exist[column_name])

    downloaded_files = set(get_existing_files())

    final_video_ids = list(existing_video_ids - downloaded_files)
    try:
        return sample(final_video_ids, k=sample_size)
    except ValueError:
        logger.info("The sample %s is larger than population %s" % (sample_size, len(final_video_ids)))
        logger.info("We take the full list of video ids thus.")
        return final_video_ids


if __name__ == '__main__':
    filter_by_cnl_id = 'UCn5-OHqf7b_sd7knIbZJ6xQ'
    video_lib = get_videos_from_google_sheet(sample_size=130, filter_by_cnl_id=filter_by_cnl_id)
    video_lib = [f"https://www.youtube.com/watch?v={el}" for el in video_lib]
    
    for v_idx, v_url in enumerate(video_lib, start=1):
        dl_yt_as_mp3(v_url, settings.audio_lib, character_limiter=60)
        logger.info("%s. %s downloaded" % (v_idx, v_url))




    print('Hello world')


