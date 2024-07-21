from google_services.authorization.get_oauth_creds import get_creds
from googleapiclient.discovery import build
from youtube_api.helpers import ids_to_str
import arrow
import re
from datetime import timedelta
from youtube_api.helpers import YOUTUBE_VIDEO_PREFIX, YOUTUBE_CHANNEL_PREFIX,\
    YOUTUBE_PLAYLIST_PREFIX, YOUTUBE_CHANNEL_RSS_PREFIX
from config import logger
from bs4 import BeautifulSoup
from youtube_api.regions_codes import MOST_IMPORTANT_REGIONS
import requests

class Video():
    def __init__(self, raw_api_video_item: dict):
        self.id = raw_api_video_item['id']
        
        self.snippet = raw_api_video_item['snippet']
        self.status = raw_api_video_item['status']
        self.content_details = raw_api_video_item['contentDetails']
        self.statistics = raw_api_video_item['statistics']
        
        self.original_metadata = self.snippet['title']
        self.channel_id = self.snippet['channelId']
        self.video_category = int(self.snippet['categoryId'])
        self.upload_status = self.status['uploadStatus']
        self.privacy_status = self.status['privacyStatus']
        self.views = (lambda x: int(x) if x else None) (self.statistics.get('viewCount'))
        self.likes = (lambda x: int(x) if x else None)(self.statistics.get('likeCount', None))
        self.comment_count = (lambda x: int(x) if x else None)(self.statistics.get('commentCount', None))
        
        self.raw_published = self.snippet['publishedAt']
        self.raw_length = raw_api_video_item['contentDetails']['duration']

        self.relevant_channel_info = ""

        self.video_url = f'{YOUTUBE_VIDEO_PREFIX}{self.id}'
        self.channel_url = f'{YOUTUBE_CHANNEL_PREFIX}{self.channel_id}'
    
    @property
    def published(self):
        arrow_date = arrow.get(self.raw_published)
        return arrow_date.datetime
    
    @property
    def published_humanize(self):
        arrow_date = arrow.get(self.raw_published)
        return arrow_date.humanize()
    
    @property
    def length(self):
        '''
        https://en.wikipedia.org/wiki/ISO_8601#Durations
        :param yt_dur: "P2DT3H24M5S" is a possible input, where all the D/H/M/S are all optional
        :return: duration is returned as datetime length
        '''
        length_pattern = re.findall('P(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?', self.raw_length)[0]
        duration_object = []
        for el in length_pattern:
            el = re.split('\D', el)[0]
            if not el:
                el = 0
            duration_object.append(int(el))
        return timedelta(days = duration_object[0], hours = duration_object[1], minutes = duration_object[2], seconds = duration_object[3])

    def __repr__(self):
        return f'''
        <Video ID: {self.id}, {self.original_metadata},
        published: {self.published} // {self.published_humanize}
        length: {self.length}, upload status: {self.upload_status}
        video url: {self.video_url}
        channel url: {self.channel_url}
        category: {self.video_category}>'''

class Channel():
    def __init__(
        self,
        raw_api_channel_item: dict,
        relevant_video_id = None
        ):
        self.id = raw_api_channel_item['id']

        self.snippet = raw_api_channel_item['snippet']
        self.content_details = raw_api_channel_item['contentDetails']
        self.statistics = raw_api_channel_item['statistics']
        self.topic_details = raw_api_channel_item.get('topicDetails', None)

        self.title = self.snippet['title']
        self.custom_url = self.snippet.get('customUrl', None)
        self.raw_published = self.snippet['publishedAt']
        self.raw_country = self.snippet.get('country', '---')
        self.default_language = self.snippet.get('defaultLanguage', '---')
        self.playlist_id = self.content_details['relatedPlaylists']['uploads']
        self.total_views = int(self.statistics['viewCount'])
        self.subscribers = int(self.statistics['subscriberCount'])
        self.video_count = (lambda x: x if x else 0)(int(self.statistics['videoCount']))
        
        if self.topic_details:
            self.topic_ids = self.topic_details.get('topicIds', None)
            self.topic_categories = self.topic_details.get('topicCategories', None)

        self.relevant_video_id = relevant_video_id
        
        self.channel_url = f'{YOUTUBE_CHANNEL_PREFIX}{self.id}'
        self.playlist_url = f'{YOUTUBE_PLAYLIST_PREFIX}{self.playlist_id}'
    
   
    @property
    def published(self):
        arrow_date = arrow.get(self.raw_published)
        return arrow_date.datetime
    
    @property
    def published_humanize(self):
        arrow_date = arrow.get(self.raw_published)
        return arrow_date.humanize()
    
    def __repr__(self):
        return f'''
        <Channel ID: {self.id}, Title: {self.title},
        published: {self.published} // {self.published_humanize}
        channel url: {self.channel_url}
        playlist url: {self.playlist_url}
        topic categories: 
            {'; '.join(self.topic_categories)}
        total views: {self.total_views}
        video count: {self.video_count}
        subscribers: {self.subscribers}
        country: {self.raw_country}
        >'''


class ApiRequest():
    def service(self):
        creds = get_creds()
        return build('youtube', 'v3', credentials=creds)


class VideoApiRequest(ApiRequest):
    def __init__(self, video_ids: list[str]):
        self.video_ids_chunks = ids_to_str(video_ids)
        self.num_videos = len(video_ids)
        self.num_chunks = len(self.video_ids_chunks)
        self.part_parameter = 'contentDetails,snippet,statistics,status'
    
    def get_video_data(self, get_channel_data=True) -> list[Video]:
        video_data = []
        for chunk_index, chunk in enumerate(self.video_ids_chunks, start=1):
            logger.info(f'Chunk #{chunk_index} out of {len(self.video_ids_chunks)}.')
            api_response = self.service().videos().list(
                part=self.part_parameter,
                id=chunk
            ).execute()
            for item in api_response['items']:
                video_data.append(Video(item))
        if get_channel_data:
            channel_ids = list({video.channel_id for video in video_data})
            channels_obj = ChannelApiRequest(channel_ids)
            channels_data = channels_obj.get_channel_data()
            cnl_dict = {cnl.id:cnl for cnl in channels_data}
            for video in video_data:
                current_channel = video.channel_id
                video.relevant_channel_info = cnl_dict.get(current_channel, None)

        return video_data


class ChannelApiRequest(ApiRequest):
    def __init__(self, channel_ids: list[str]):
        self.channel_ids_chunks = ids_to_str(channel_ids)
        self.num_videos = len(channel_ids)
        self.num_chunks = len(self.channel_ids_chunks)
        self.part_parameter = 'contentDetails,id,snippet,statistics,status,topicDetails'
        
    def get_channel_data(self) -> list[Channel]:
        channel_data = []
        for chunk_idx, chunk in enumerate(self.channel_ids_chunks, start=1):
            logger.info(f'Chunk #{chunk_idx} out of {len(self.channel_ids_chunks)}.')
            api_response = self.service().channels().list(
                part=self.part_parameter,
                id=chunk
            ).execute()
            for item in api_response['items']:
                channel_data.append(Channel(item))
        return channel_data


class PlaylistApiRequest(ApiRequest):
    def __init__(self, playlist_ids: list[str]):
        self.playlist_ids = playlist_ids
        self.playlist_ids_chunks = ids_to_str(playlist_ids)
        self.num_videos = len(playlist_ids)
        self.num_chunks = len(self.playlist_ids_chunks)

    def get_playlist_info(self) -> dict:
        next_page_token = 'dummy'
        pl_info_result = []
        for chunk_idx, chunk in enumerate(self.playlist_ids_chunks, start=1):
            logger.info(f'Chunk #{chunk_idx} out of {len(self.playlist_ids_chunks)}.')
            while next_page_token or next_page_token == 'dummy':
                api_response = self.service().playlists().list(
                    part = 'contentDetails, snippet',
                    id=chunk,
                    maxResults=50,
                    pageToken = (lambda x: x if x and x!='dummy' else None)(next_page_token)
                ).execute()
                for item in api_response['items']:
                    snip = item['snippet']
                    pl_info = {
                        'pl_id': item['id'],
                        'pl_title': snip['title'],
                        'cnl_id': snip['channelId'],
                        'cnl_title': snip['channelTitle'],
                        'published_at': snip['publishedAt'],
                        'video_count': item['contentDetails']['itemCount']
                    }
                    pl_info_result.append(pl_info)
                next_page_token = api_response.get('nextPageToken', None)
        return pl_info_result

    def get_video_ids(self, playlist_id: str) -> list[str]:
        next_page_token = 'dummy'
        video_ids = []
        while next_page_token or next_page_token == 'dummy':
            api_response = self.service().playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults = 50,
                    pageToken = (lambda x: x if x and x!='dummy' else None)(next_page_token)
                ).execute()
            for video in api_response['items']:
                video_ids.append(video['contentDetails']['videoId']) 
            next_page_token = api_response.get('nextPageToken', None)
        return video_ids
    
    def get_pl_info_and_video_ids(self):
        pl_info_result = self.get_playlist_info()
        for pl in pl_info_result:
            video_ids = self.get_video_ids(pl['pl_id'])
            pl['video_ids'] = video_ids
        
        return pl_info_result

    def __repr__(self):
        return f''


class MostPopularApiRequest(ApiRequest):
    def __init__(self, max_videos_per_region=200):
        self.most_important_regions = list(MOST_IMPORTANT_REGIONS.keys())
        self.part_parameter = 'contentDetails'
        self.max_videos_per_region = max_videos_per_region
    def get_videos_ids(self) -> dict[list]:
        final_chart = {}
        for region in self.most_important_regions:
            next_page_token = 'dummy'
            final_chart[region] = []
            while (next_page_token or next_page_token == 'dummy')\
                and len(final_chart[region]) <= self.max_videos_per_region:
                api_response = self.service().videos().list(
                    part=self.part_parameter,
                    chart='mostPopular',
                    regionCode=region,
                    videoCategoryId='10',
                    maxResults = 50
                ).execute()
                
                for video in api_response['items']:
                    final_chart[region].append(video['id'])
                
                next_page_token = api_response.get('nextPageToken', None)

        return final_chart

class SearchApi(ApiRequest):
    def __init__(self, search_query):
        self.search_query = search_query
        self.part_parameter = 'id'
    def get_search_results(self):
        api_response = self.service().search().list(
            part=self.part_parameter,
            q=self.search_query,
            maxResults = 50).execute()
        return api_response['items']
        
class ChannelRssRequest():
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.rss_url = f'{YOUTUBE_CHANNEL_RSS_PREFIX}{channel_id}'
        self.cnl_url = f'{YOUTUBE_CHANNEL_PREFIX}{channel_id}'

    def get_video_ids(self) -> list[str]:
        with requests.Session() as session:
            req = requests.get(self.rss_url, timeout=200)
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, parser='html.parser')
                entries = soup.find_all('entry')
                return [video.find("yt:videoid").text for video in entries]
            return f'Something went wrong with {self.rss_url} // Status code: {req.status_code}'
    
    def __repr__(self):
        return f'''
        <Channel ID: {self.channel_id}. 
        RSS url: {self.rss_url}.
        Channel url: {YOUTUBE_CHANNEL_PREFIX}{self.channel_id}>'''


class UserApiRequest(ApiRequest):
    def __init__(self, user_ids: list[str]):
        self.user_ids_chunks = ids_to_str(user_ids)
        self.num_videos = len(user_ids)
        self.num_chunks = len(self.user_ids_chunks)
        self.part_parameter = 'contentDetails,id,snippet,statistics,status,topicDetails'
        
    def get_user_data(self):
        user_data = []
        for chunk in self.user_ids_chunks:
            api_response = self.service().channels().list(
                part=self.part_parameter,
                forUsername=chunk
            ).execute()
            for item in api_response['items']:
                user_data.append(item)
        return user_data

if __name__ == '__main__':
    # pl_ids = [
    #     'PL4fGSI1pDJn5C8dBiYt0BTREyCHbZ47qc',
    #     'PLgMaGEI-ZiibpOQW9NaU2lQdnTxpRohMj',
    #     'PL-DfNcB3lim9IZmUXEjE1Ov0Ir1NDa3Yr',
    #     'PLp12xt0S4J0UYXerKrIPCLTk15ZUzFdKz'
    #     ]
    # pl = PlaylistApiRequest(pl_ids)

    # pl_info_w_videos = pl.get_pl_info_and_video_ids()

    # print('Hello World!')

    # vid = pl.get_video_ids(pl_ids[0])
    # pl_info_result = pl.get_playlist_info()
    # print(vid)
    # print(len(vid))
    # for pl_info in pl_info_result:
    #     print(pl_info)

    search_q = 'Oathbreaker - No rest for the weary'
    search = SearchApi(search_q)
    results = search.get_search_results()

    videos = [el['id']['videoId'] for el in results if el['id']['kind']=='youtube#video']

    video_data_instance = VideoApiRequest(videos)
    video_data = video_data_instance.get_video_data()


    print('Hello world!')