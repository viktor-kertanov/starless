from youtube_api.classes import PlaylistApiRequest, VideoApiRequest, ChannelApiRequest
from youtube_api.helpers import get_id_by_custom_url
from google_services.google_sheets.read_sheets import read_google_sheet
from google_services.google_sheets.write_sheets import append_to_spreadsheet, write_to_spreadsheet
from config import settings
import pandas as pd
from datetime import datetime, timedelta
from youtube_api.classes import Video
from logs.log_config import logger
import json


def prepare_chart_google(
    video_data: list[Video],
    spreadsheet_id: str,
    sheet_name: str,
    with_channel_info_block: bool=False
    ) ->list[list]:
    """Here we prepare the chart with VIDEO data from Youtube, for input to Google Sheets"""

    output_chart = []
    for index_video, video in enumerate(video_data, start=1):
        row = {}
        row['video_id'] = video.id
        row['video_url'] = video.video_url
        row['v_go'] = f'=HYPERLINK("{video.video_url}"; "go")'
        row['channel_id'] = video.channel_id
        row['c_go'] = f'=HYPERLINK("{video.channel_url}"; "go")'
        row['channel_title'] = video.relevant_channel_info.title if video.relevant_channel_info else "N/A"
        row['video_title'] = video.original_metadata
        row['views'] = video.views
        row['published'] = video.published_humanize
        row['pub_date'] = video.published.strftime('%Y-%m-%d %H:%M')
        row['length'] = str(video.length)
        row['length_sec'] = str(video.length.seconds) #added
        row['category'] = video.video_category
        row['row_inserted'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        if with_channel_info_block:
            cnl_block = video.relevant_channel_info
            if not cnl_block:
                continue
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


def work_with_playlists(
        playlists_ids: list[str] = None,
        days_no_check: int = 30
    ):
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_pl = "playlists"
    
    input_sheet_data = read_google_sheet(google_sheet_id, google_sheet_pl)
    playlist_headers = input_sheet_data.columns.tolist()
    deduped = input_sheet_data.drop_duplicates(subset='playlist_id', keep='first')

    if not playlists_ids:
        deduped['date_processed'] = pd.to_datetime(deduped['date_processed'], format='%d.%m.%Y')
        threshold_date = datetime.now() - timedelta(days=days_no_check)
        playlists_to_check = deduped[(deduped['date_processed'] < threshold_date) | pd.isna(deduped['date_processed'])]
        playlists_ids = list(playlists_to_check['playlist_id'])

    write_youtube_video_data_by_playlists_ids_to_google_sheets(playlists_ids)
    
    # update the date_processed column and update the google sheet with the new data
    deduped['date_processed'] = datetime.now().strftime('%d.%m.%Y')
    updated_playlist_info = deduped.values.tolist()
    updated_playlist_info.insert(0, playlist_headers)
    write_to_spreadsheet(updated_playlist_info, google_sheet_id, google_sheet_pl)
    
    return None


def work_with_channels(
        channels_to_check: list[str] = None,
        days_no_check: int = 30
    ):
    
    input_from_google_sheet = True if channels_to_check else False

    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_cnl = "channels"
    # get the videos set that we already have on the final list
    if not channels_to_check:
        # read what playlists we need to check
        input_sheet_data = read_google_sheet(google_sheet_id, google_sheet_cnl)
        playlist_headers = input_sheet_data.columns.tolist()
        deduped = input_sheet_data.drop_duplicates(subset='channel', keep='first')
        deduped['date_processed'] = pd.to_datetime(deduped['date_processed'], format='%d.%m.%Y')
        threshold_date = datetime.now() - timedelta(days=days_no_check)

        final_playlists_to_check = deduped[(deduped['date_processed'] < threshold_date) | pd.isna(deduped['date_processed'])]

        # extract playlist ids and send request to YT API to get video ids
        channels_to_check = list(final_playlists_to_check['channel'])
    
    channels_to_check = [get_id_by_custom_url(cnl) for cnl in channels_to_check]
    final_channels_to_check = [el for el in channels_to_check if el]

    if len(final_channels_to_check) != len(channels_to_check):
        logger.info(
            "%s is initial list of channels VS. %s the end list of channels" 
            % (len(channels_to_check), len(final_channels_to_check))
        )

    cnl = ChannelApiRequest(final_channels_to_check)
    cnl_data = cnl.get_channel_data()

    playlists_ids = [cnl.playlist_id for cnl in cnl_data]

    write_youtube_video_data_by_playlists_ids_to_google_sheets(playlists_ids)

    # update the date_processed column and update the google sheet with the new data
    if input_from_google_sheet:
        deduped['date_processed'] = datetime.now().strftime('%d.%m.%Y')
        updated_playlist_info = deduped.values.tolist()
        updated_playlist_info.insert(0, playlist_headers)
        write_to_spreadsheet(updated_playlist_info, google_sheet_id, google_sheet_cnl)
    
    return playlists_ids


def write_youtube_video_data_by_playlists_ids_to_google_sheets(playlists_ids: list[str]) -> None:
     # collect the list of all the video ids from every playlist and dedupe existing videos, duplicates
    google_sheet_id = settings.sample_machine_sheet_id
    google_sheet_videos = "videos"

    videos_exist = read_google_sheet(google_sheet_id, google_sheet_videos)
    existing_video_ids = set(videos_exist["video_id"])
    
    pl = PlaylistApiRequest(playlists_ids)
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

    return None

if __name__ == '__main__':
    data_path = "sample_machine_service/vk_history_data_july_2024/watched.json"
    with open(data_path, 'r', encoding='utf-8') as file:
        videos = json.load(file)
    video_urls = videos[:1000]
    video_urls = [v.split("v=")[-1] for v in video_urls]
    api_req = VideoApiRequest(video_urls)
    video_data = api_req.get_video_data(get_channel_data=True)
    

    prepare_chart_google(video_data, spreadsheet_id='1XZE_NvDu2mnBJVcu1DcOY_EpTa81ikQjqOuFIUnmDko', sheet_name='history', with_channel_info_block=True)
    # work_with_channels(channels_to_check=None)
    # work_with_playlists(playlists_ids=None)

    print('Hello world')
