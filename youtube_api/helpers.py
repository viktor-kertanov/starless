from google_auth.get_oauth_creds import get_creds
from googleapiclient.discovery import build
from youtube_api.test_data import test_sources, test_video_ids
import re

YOUTUBE_CHANNEL_PREFIX = 'https://www.youtube.com/channel/'
YOUTUBE_VIDEO_PREFIX = 'https://www.youtube.com/watch?v='
YOUTUBE_PLAYLIST_PREFIX = 'https://www.youtube.com/playlist?list='
YOUTUBE_CHANNEL_RSS_PREFIX = 'https://www.youtube.com/feeds/videos.xml?channel_id='
CUSTOM_CHANNEL_URL_PREFIX = 'https://www.youtube.com/c/'


def _list_divider(list, size=50):
    for i in range(0, len(list), size):
        yield list[i:i + size]

def _joiner(list, separator=","):
    res_chart=[]
    for el in list:
        joined_string=separator.join(el)
        res_chart.append(joined_string)
    return res_chart

def ids_to_str(video_ids: list[str]) -> list[str]:
    chunkedList = list(_list_divider(video_ids))
    stringsList = _joiner(chunkedList)
    return stringsList

def proper_source_id(input_string):
    """
    the function gets youtube urls, channel ids, playlist ids and converts them into the proper
    standard ID form: "UC...." or "UU...." (24 characters string); or "PL...." (34 character string)
    :param input_string:
    :return:
    """
    patterns = [re.compile(r'U[UC][^&=]{22}'),
                re.compile(r'PL[^&=]{32}'),
                re.compile(r'RD[^&=]{41}')]
    for p in patterns:
        my_search = p.search(input_string)
        if my_search:
            break
        else:
            continue
    if my_search:
        proper_yt_id = my_search.group()
        proper_yt_id = re.sub('^UU', 'UC', proper_yt_id)
        return proper_yt_id
    if 'youtube.com/c/' in input_string:
        channel_id = _get_id_by_custom_url(input_string)
        return channel_id

def _get_id_by_custom_url(custom_channel_url):
    string_prepared = re.sub('.*youtube.com/c/', '', custom_channel_url)
    string_prepared = string_prepared.split('/')[0]
    creds = get_creds()
    service = build('youtube', 'v3', credentials=creds)
    part_parameter = 'id'
    api_response = service.search().list(
        part=part_parameter,
        q=string_prepared,
        maxResults = 5).execute()
    for item in api_response['items']:
        if item['id']['kind'] != 'youtube#channel':
            continue
        else:
            channel_id = item['id']['channelId']
            print(f'''
            Our found channel for {CUSTOM_CHANNEL_URL_PREFIX}{string_prepared}
            is {YOUTUBE_CHANNEL_PREFIX}{channel_id}''')
            return channel_id

def proper_video_id(input_string):
    input_string = str(input_string)
    patterns = [re.compile(r'v=[^?/=&.]{11}'), re.compile(r'[^ ?/=&.]{11}')]
    for p in patterns:
        my_search = p.search(input_string)
        if my_search:
            break
        else:
            continue
    if my_search:
        proper_video_id = my_search.group()
        proper_video_id = re.sub("v=","", proper_video_id)
        return proper_video_id
    else:
        # print(f"Problem with INPUT: {input_string}")
        return None


if __name__ == '__main__':
    # for el in test_sources:
    #     a = proper_source_id(el)
    #     print(a)
    a = proper_video_id('qbqJVEbQgXQ')
    print(a)