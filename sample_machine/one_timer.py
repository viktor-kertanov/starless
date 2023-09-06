from pytube import YouTube
import os
import re
from config import settings
from pytube.exceptions import VideoUnavailable
from logs.log_config import logger
from pydub import AudioSegment



# sample_lib = settings.sample_lib
# sample_lib = settings.effects_sample_lib
# effects_sample_lib = settings.effects_sample_lib

audio_lib = settings.audio_lib

file_list = os.listdir(audio_lib)
file_list = [f"{audio_lib}{f}" for f in file_list if os.path.isfile(os.path.join(audio_lib, f)) if not f.startswith('.')]

for f in file_list:
    audio = AudioSegment.from_file(f, format="mp4")

    audio.export(f.replace('.mp4', '.mp3'), format="mp3")
    os.remove(f)

print('Hello world')
