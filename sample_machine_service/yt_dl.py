
from pytube import YouTube
import os
import re
from config import settings
from pytube.exceptions import VideoUnavailable
from logs.log_config import logger
from pydub import AudioSegment

from http.client import IncompleteRead
from urllib.error import URLError

def dl_yt_as_mp3(
    video_url: str,
    output_path: str,
    character_limiter: int=60
):
    yt = YouTube(video_url)
    try:
        video = yt.streams.filter(only_audio=True).first()
    except VideoUnavailable:
        return logger.info("%s unavailable" % video_url)
    try:
        out_file = video.download(output_path=output_path)
    except (IncompleteRead, URLError):
        print(f"A problem occurred, but we are moving on.")
        return None
    
    base, ext = os.path.splitext(out_file)
    video_id = video_url.split('v=')[-1]
    filename=base.split('/')[-1]
    filename = re.sub(r"\s+", "_", filename).lower()
    filename = video_id + '_id_' + filename
    filename = filename[:character_limiter]
    filename += ".mp3"
    output_path = output_path + filename

    audio = AudioSegment.from_file(out_file, format="mp4")

    # Export the audio as an MP3 file
    audio.export(output_path, format="mp3")
    os.remove(out_file)
    print(f'Output: {output_path}.')
    
    return output_path

def dl_yt_video(
    video_url: str,
    output_path: str,
    character_limiter: int = 60
):
    try:
        yt = YouTube(video_url)
    except Exception as e:
        print(f"Error: {e}")
        return None

    try:
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    except Exception as e:
        print(f"Error: {e}")
        return None

    try:
        in_file = video.download(output_path=output_path)
    except (IncompleteRead, URLError) as e:
        print(f"Error downloading: {e}")
        return None

    base, ext = os.path.splitext(in_file)
    video_id = yt.video_id
    filename = os.path.basename(base)
    filename = re.sub(r"\s+", "_", filename).lower()
    filename = f"{video_id}_id_{filename[:character_limiter]}.{ext}"

    # Rename the downloaded file
    os.rename(in_file, os.path.join(output_path, filename))

    return os.path.join(output_path, filename)


if __name__ == '__main__':
    yt_dl_folder = settings.test_lib
    video_urls = [
        "https://www.youtube.com/watch?v=rYEDA3JcQqw",
        "https://www.youtube.com/watch?v=WIF4_Sm-rgQ",
        "https://www.youtube.com/watch?v=YlUKcNNmywk",
        "https://www.youtube.com/watch?v=SBjQ9tuuTJQ",
        "https://www.youtube.com/watch?v=rn_YodiJO6k",
        "https://www.youtube.com/watch?v=ekzHIouo8Q4",
        "https://www.youtube.com/watch?v=sMmTkKz60W8",
        "https://www.youtube.com/watch?v=XFkzRNyygfk",
        "https://www.youtube.com/watch?v=hTWKbfoikeg",
        "https://www.youtube.com/watch?v=u9WgtlgGAgs"
    ]
    video_urls = ["https://www.youtube.com/watch?v=QV0NtCFHUrY"]
    dl_yt_video(video_urls[0], '/Volumes/KERTANOV_VIKTOR/itmo_screenology/yt_shorts')
    for video_url in video_urls:
        dl_yt_as_mp3(video_url, yt_dl_folder, character_limiter=50)

    print('Hello world!')