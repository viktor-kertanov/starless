
from pytube import YouTube
import os
import re
from config import settings


def dl_yt_as_mp3(video_url: str, output_path: str, character_limiter: int=60):
    yt = YouTube(video_url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=output_path)
    
    base, ext = os.path.splitext(out_file)
    video_id = video_url.split('v=')[-1]
    filename=base.split('/')[-1]
    filename = re.sub(r"\s+", "_", filename).lower()
    filename = video_id + '_id_' + filename
    filename = filename[:character_limiter]
    filename+='.mp3'
    
    output_path = output_path + filename
    os.rename(out_file, output_path)
    print(f'Output: {output_path}.')
    
    return output_path


if __name__ == '__main__':
    yt_dl_folder = settings
    video_url = "https://www.youtube.com/watch?v=__-EM_IUVuw"
    dl_yt_as_mp3(video_url, yt_dl_folder, character_limiter=50)

    print('Hello world!')