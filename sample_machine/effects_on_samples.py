from config import settings
from logs.log_config import logger
import librosa
import soundfile as sf
import os
import random
import shutil
import numpy as np
from sample_machine.define_key_classes import Tonal_Fragment


def stretch_speedup_audio(audio_path: str, factor: float):
    audio_path = f"{sample_lib}{audio_file}"
    y, sr = librosa.load(audio_path)
    y_slowed = librosa.effects.time_stretch(y, rate=factor)
    
    return y_slowed


def define_pitch(audio_path):
    y, sr = librosa.load(audio_path)
    print('----'*30)
    print(audio_path)

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

    return {
        "tempo": tempo,
        "beat_times": beat_times
    }


def imply_fade_in_out():

    return

def reverse_sample():


    return


if __name__ == '__main__':
    frequency = 3990
    note = librosa.hz_to_note(frequency)
    logger.info(f"The note for {frequency} Hz is {note}")


    sample_lib = settings.sample_lib
    sample_lib = settings.effects_sample_lib
    effects_sample_lib = settings.effects_sample_lib
    file_list = os.listdir(sample_lib)
    file_list = [f for f in file_list if os.path.isfile(os.path.join(sample_lib, f)) if not f.startswith('.')]

    audio_files = random.sample(file_list, k=len(file_list))

    for audio_file in audio_files:
        audio_path = f"{sample_lib}{audio_file}"
        y, sr = librosa.load(audio_path, sr=None)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        logger.info(audio_path)
        logger.info(f"Tempo: {tempo} BPM")

        y_harmonic, y_percussive = librosa.effects.hpss(y)
        
        chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)

        print(chromagram)

    print('Hello world')