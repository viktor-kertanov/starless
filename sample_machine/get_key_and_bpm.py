from config import settings
from logs.log_config import logger
import librosa
import os
import random
from sample_machine.define_key_classes import Tonal_Fragment

def define_pitch(audio_path):
    y, sr = librosa.load(audio_path)

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tonal_fragment = Tonal_Fragment(y_harmonic, sr)
    
    return {
        "main_key": tonal_fragment.key,
        "alternative_key": tonal_fragment.altkey
    }

def define_bpm(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    return round(tempo,0), beat_times

if __name__ == '__main__':
    test_lib = settings.test_lib
    file_list = os.listdir(test_lib)
    file_list = [
        f"{test_lib}{f}"
        for f in file_list
        if os.path.isfile(os.path.join(test_lib, f))
        if not f.startswith('.')
    ]

    audio_files = random.sample(file_list, k=len(file_list))

    for file in audio_files:
        logger.info('---'*15)
        logger.info(file)
        tempo, beat_times = define_bpm(file)
        keys = define_pitch(file)
        logger.info("Tempo is %s BPM" % tempo)
        logger.info("Main defined key: {%s}. Alternative: {%s}" % (keys["main_key"], keys["alternative_key"]))
        logger.info('---'*15)


    print('Hello world')