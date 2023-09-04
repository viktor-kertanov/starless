from youtube_api.classes import PlaylistApiRequest, VideoApiRequest, ChannelApiRequest
from youtube_api.helpers import get_id_by_custom_url
from google_services.google_sheets.read_sheets import read_google_sheet
from google_services.google_sheets.write_sheets import append_to_spreadsheet, write_to_spreadsheet
from config import settings
import pandas as pd
from datetime import datetime, timedelta
from youtube_api.classes import Video
from logs.log_config import logger
from time import sleep
from random import randint


def prepare_chart_google(
    video_data: list[Video],
    spreadsheet_id: str,
    sheet_name: str,
    with_channel_info_block: bool=False
    ) ->list[list]:
    
    output_chart = []
    for index_video, video in enumerate(video_data, start=1):
        row = {}
        row['video_id'] = video.id
        row['video_url'] = video.video_url
        row['v_go'] = f'=HYPERLINK("{video.video_url}"; "go")'
        row['channel_id'] = video.channel_id
        row['c_go'] = f'=HYPERLINK("{video.channel_url}"; "go")'
        row['channel_title'] = video.relevant_channel_info.title
        row['video_title'] = video.original_metadata
        row['views'] = video.views
        row['published'] = video.published_humanize
        row['pub_date'] = video.published.strftime('%Y-%m-%d %H:%M')
        row['length'] = str(video.length)
        row['category'] = video.video_category
        row['row_inserted'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        if with_channel_info_block:
            cnl_block = video.relevant_channel_info
            row['subs'] = cnl_block.subscribers
            row['total_views'] = cnl_block.total_views
            row['video_count'] = cnl_block.video_count
            row['playlist_id'] = cnl_block.playlist_id
            row['cnl_created'] = cnl_block.published.strftime('%Y-%m-%d %H:%M')
            row['country'] = cnl_block.raw_country
            row['language'] = cnl_block.default_language
        append_row = list(row.values())
        message_row = f'#{index_video} out of {len(video_data)}. {video.video_url} :: {video.original_metadata}.'
        logger.info(message_row)
        output_chart.append(append_row)
    
    append_to_spreadsheet(output_chart, spreadsheet_id, sheet_name)
    
    return None


def work_with_playlists(days_no_check: int = 60):
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_pl = "playlists"
    google_sheet_videos = "videos"

    # get the videos set that we already have on the final list
    videos_exist = read_google_sheet(google_sheet_id, google_sheet_videos)
    existing_video_ids = set(videos_exist["video_id"])

    # read what playlists we need to check
    input_sheet_data = read_google_sheet(google_sheet_id, google_sheet_pl)
    playlist_headers = input_sheet_data.columns.tolist()
    deduped = input_sheet_data.drop_duplicates(subset='playlist_id', keep='first')
    deduped['date_processed'] = pd.to_datetime(deduped['date_processed'])
    threshold_date = datetime.now() - timedelta(days=days_no_check)
    final_playlists_to_check = deduped[(deduped['date_processed'] < threshold_date) | pd.isna(deduped['date_processed'])]

    # extract playlist ids and send request to YT API to get video ids
    pl_ids = list(final_playlists_to_check['playlist_id'])
    pl = PlaylistApiRequest(pl_ids)
    pl_data = pl.get_pl_info_and_video_ids()

    # collect the list of all the video ids from every playlist and dedupe existing videos, duplicates
    video_ids = []
    for playlist in pl_data:
        pl_video_ids = playlist["video_ids"]
        video_ids += pl_video_ids
    
    video_ids = set(video_ids)
    video_ids = list(video_ids - existing_video_ids)

    # gather information about each video
    if video_ids:
        video_data_instance = VideoApiRequest(video_ids)
        video_data = video_data_instance.get_video_data()

        prepare_chart_google(video_data, google_sheet_id, google_sheet_videos)
    
    # update the date_processed column and update the google sheet with the new data
    deduped['date_processed'] = datetime.now().strftime('%d.%m.%Y')
    updated_playlist_info = deduped.values.tolist()
    updated_playlist_info.insert(0, playlist_headers)
    write_to_spreadsheet(updated_playlist_info, google_sheet_id, google_sheet_pl)
    
    return None


def work_with_channels(days_no_check: int = 30):
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_cnl = "channels"
    google_sheet_videos = "videos"

    # get the videos set that we already have on the final list
    videos_exist = read_google_sheet(google_sheet_id, google_sheet_videos)
    existing_video_ids = set(videos_exist["video_id"])

    # read what playlists we need to check
    input_sheet_data = read_google_sheet(google_sheet_id, google_sheet_cnl)
    playlist_headers = input_sheet_data.columns.tolist()
    deduped = input_sheet_data.drop_duplicates(subset='channel', keep='first')
    deduped['date_processed'] = pd.to_datetime(deduped['date_processed'])
    threshold_date = datetime.now() - timedelta(days=days_no_check)
    final_playlists_to_check = deduped[(deduped['date_processed'] < threshold_date)| pd.isna(deduped['date_processed'])]

    # extract playlist ids and send request to YT API to get video ids
    cnl_ids = list(final_playlists_to_check['channel'])
    assumed_cnl_ids = [get_id_by_custom_url(cnl) for cnl in cnl_ids if get_id_by_custom_url(cnl)]
    cnl = ChannelApiRequest(assumed_cnl_ids)
    cnl_data = cnl.get_channel_data()

    # collect the list of all the video ids from every playlist and dedupe existing videos, duplicates
    
    pl_ids = [cnl.playlist_id for cnl in cnl_data]

    pl = PlaylistApiRequest(pl_ids)
    pl_data = pl.get_pl_info_and_video_ids()

    # collect the list of all the video ids from every playlist and dedupe existing videos, duplicates
    video_ids = []
    for playlist in pl_data:
        pl_video_ids = playlist["video_ids"]
        video_ids += pl_video_ids

    video_ids = set(video_ids)
    video_ids = list(video_ids - existing_video_ids)

    # gather information about each video
    if video_ids:
        video_data_instance = VideoApiRequest(video_ids)
        video_data = video_data_instance.get_video_data()

        prepare_chart_google(video_data, google_sheet_id, google_sheet_videos)
    
    # update the date_processed column and update the google sheet with the new data
    deduped['date_processed'] = datetime.now().strftime('%d.%m.%Y')
    updated_playlist_info = deduped.values.tolist()
    updated_playlist_info.insert(0, playlist_headers)
    write_to_spreadsheet(updated_playlist_info, google_sheet_id, google_sheet_cnl)
    
    return None

if __name__ == '__main__':
    work_with_channels()

    print('Hello world')
