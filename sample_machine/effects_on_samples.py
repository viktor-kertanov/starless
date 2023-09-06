from config import settings
from logs.log_config import logger
import librosa
import soundfile as sf
import os
import random
import shutil
import numpy as np


def stretch_audio():
    sample_lib = settings.sample_lib
    effects_sample_lib = settings.effects_sample_lib
    file_list = os.listdir(sample_lib)
    file_list = [f for f in file_list if os.path.isfile(os.path.join(sample_lib, f)) if not f.startswith('.')]

    audio_files = random.sample(file_list, k=3)
    for audio_file in audio_files:
        audio_path = f"{sample_lib}{audio_file}"
        shutil.copy2(audio_path, f"{effects_sample_lib}{audio_file}")
        factor_array = np.logspace(np.log10(0.1), np.log10(5), 5)

        y, sr = librosa.load(audio_path)

        for factor in factor_array:
            y_slowed = librosa.effects.time_stretch(y, rate=factor)
            sf.write(f"{effects_sample_lib}f{round(factor,1)}_{audio_file}", y_slowed, sr)
    return

def define_pitch():

    return

def define_bpm():

    return

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
        # Estimate pitch
        # pitch, _ = librosa.piptrack(y=y, sr=sr)

        # # Find the most dominant pitch
        # pitch_values = [p.max() for p in pitch]
        # dominant_pitch_index = pitch_values.index(max(pitch_values))
        # dominant_pitch = pitch[dominant_pitch_index]

        # # Convert the pitch to a note or frequency
        # # You can use additional libraries or functions to map pitch values to notes or frequencies.
        # # For example, you can use MIDI note numbers or a pitch class notation.

        # # Print the estimated pitch
        # print(f"Estimated Pitch: {dominant_pitch}")

    print('Hello world')