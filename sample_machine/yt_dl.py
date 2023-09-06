
from pytube import YouTube
import os
import re
from config import settings
from pytube.exceptions import VideoUnavailable
from logs.log_config import logger
from pydub import AudioSegment


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
    out_file = video.download(output_path=output_path)
    
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


if __name__ == '__main__':
    yt_dl_folder = settings.effects_sample_lib
    # video_url = "https://www.youtube.com/watch?v=TOypSnKFHrE"
    video_urls = [
        "https://www.youtube.com/watch?v=8sgycukafqQ",
        "https://www.youtube.com/watch?v=bW62WKwVTM4",
        "https://www.youtube.com/watch?v=WPbeEtjo70g",
        "https://www.youtube.com/watch?v=1zioQ4SfIvo",
        "https://www.youtube.com/watch?v=gdmHHoI9beM",
        "https://www.youtube.com/watch?v=6Ux6SlOE9Qk",
        "https://www.youtube.com/watch?v=1SaFRqFnRQQ",
        "https://www.youtube.com/watch?v=RSdKmX2BH7o"
        # "https://www.youtube.com/watch?v=rYEDA3JcQqw",
        # "https://www.youtube.com/watch?v=WIF4_Sm-rgQ",
        # "https://www.youtube.com/watch?v=YlUKcNNmywk",
        # "https://www.youtube.com/watch?v=SBjQ9tuuTJQ",
        # "https://www.youtube.com/watch?v=rn_YodiJO6k",
        # "https://www.youtube.com/watch?v=ekzHIouo8Q4",
        # "https://www.youtube.com/watch?v=sMmTkKz60W8",
        # "https://www.youtube.com/watch?v=XFkzRNyygfk",
        # "https://www.youtube.com/watch?v=hTWKbfoikeg",
        # "https://www.youtube.com/watch?v=u9WgtlgGAgs"
    ]
    for video_url in video_urls:
        dl_yt_as_mp3(video_url, yt_dl_folder, character_limiter=50)

    print('Hello world!')