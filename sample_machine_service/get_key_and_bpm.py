from config import settings
from logs.log_config import logger
import librosa
import os
import random
from sample_machine_service.define_key_classes import Tonal_Fragment

def define_pitch(audio_path):
    y, sr = librosa.load(audio_path)

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    tonal_fragment = Tonal_Fragment(y_harmonic, sr)
    main_key = tonal_fragment.key.replace(' ', '_').lower().replace('major', 'maj').replace('minor', 'min')
    alt_key = tonal_fragment.altkey

    if max(list(tonal_fragment.key_dict.values())) < 0.5:
        return "X", tonal_fragment.corr_table()
    
    if alt_key:
        alt_key = alt_key.replace(' ', '_').lower().replace('major', 'maj').replace('minor', 'min')
        return f"{main_key}_{alt_key}", tonal_fragment.corr_table()

    return main_key, tonal_fragment.corr_table()

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
        final_keys = define_pitch(file)
        logger.info("Tempo is %s BPM" % tempo)
        logger.info("Main defined keys: %s" % final_keys)
        logger.info('---'*15)


    print('Hello world')