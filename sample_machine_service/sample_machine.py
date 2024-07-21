from random import randint
from pydub import AudioSegment, silence
from datetime import datetime
import os
from os.path import isfile, join
import shutil
from datetime import datetime
from google_services.speech_to_text.stt import speech_to_text
from config import settings
from logs.log_config import logger
from random import random, randint
from sample_machine_service.get_key_and_bpm import define_bpm, define_pitch
import numpy as np

def get_files_from_folder(folder_path):
    files = [f for f in os.listdir(folder_path) if isfile(join(folder_path, f)) if f != '.DS_Store']
    
    return files

def get_date_for_filename():
    '''Useful dateformat to append to filename'''
    return datetime.utcnow().strftime("%y%m%d_%H_%M")

def get_file_format(filename):
    return filename.split('.')[-1]

def msec_to_minutes_by_interval(interval_mseconds: int, segment_idx: int) -> str:
    total_seconds = int((segment_idx)*(interval_mseconds/1000))
    
    return msec_to_minutes_by_total(total_seconds)

def msec_to_minutes_by_total(total_msec: int) -> str:
    '''converts seconds (integer) to a string Xmin Ysec'''
    total_seconds = total_msec/1000
    
    whole_minutes = total_seconds // 60
    leftover_sec = total_seconds % 60
    
    return f"{int(whole_minutes)}m{int(leftover_sec)}s"


def minutes_seconds_from_millisec(ms):
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)

    return f"{minutes}:{seconds}"


def get_os_file_data(file_path):
    
    return {
        "filename": file_path.split("/")[-1],
        "size": os.path.getsize(file_path),
        "modified_date": datetime.fromtimestamp(os.path.getmtime(file_path)),
        "creation_date": datetime.fromtimestamp(os.path.getctime(file_path)),
        }

def detect_non_silent_frames(
        audio_path: str,
        min_silence_len_ms: int=2000,
        silence_thresh_dB: int=-50,
        seek_step_ms: int=5
        ) -> list[list]:
    
    audio = get_audio(audio_path)

    return silence.detect_nonsilent(
            audio,
            min_silence_len=min_silence_len_ms,
            silence_thresh=silence_thresh_dB,
            seek_step=seek_step_ms)

def detect_silent_frames(
        audio_path: str,
        min_silence_len_ms: int=2000,
        silence_thresh_dB: int=-50,
        seek_step_ms: int=5
        ) -> list[list]:
    
    audio = get_audio(audio_path)
    
    return silence.detect_silence(
            audio,
            min_silence_len=min_silence_len_ms,
            silence_thresh=silence_thresh_dB,
            seek_step=seek_step_ms
            )

def get_audio(audio_path, explicit_mono=False) -> AudioSegment:
    '''F(x) defines the audio format of a file via provided path and obtains pydub AudioSegment. For youtube downloaded files there's exception to try mp4 codec'''
    fileformat = get_file_format(audio_path)

    try:
        audio = AudioSegment.from_file(audio_path, format=fileformat)
    except:
        audio = AudioSegment.from_file(audio_path, format="mp4")
    
    if explicit_mono:
        audio = audio.set_channels(1)
    
    return audio

def get_filename_wo_ext(file_path):
    filename = file_path.split('/')[-1]
    filename = filename.split('.')[0]

    return filename


def make_output_folder(filename, output_path, folder_codename=None):
    if not folder_codename:
        output_folder = f"{output_path}/{get_date_for_filename()}_{filename}/".replace("//","/")
    else:
        output_folder = f"{output_path}/{get_date_for_filename()}_{filename}_[{folder_codename}]/".replace("//","/")
    
    try:
        os.mkdir(output_folder)
    except FileExistsError:
        shutil.rmtree(output_folder, ignore_errors=False)
        print(f"We are removing the current dir: {output_folder}")
        os.mkdir(output_folder)
    
    return output_folder



def export_by_timemap_to_audiofiles(
        audio_path: str,
        output_path: str,
        excerpts_timemap: list[list],
        fade_in_msec: int=300,
        fade_out_msec: int=300,
        leading_preserve_msec: int=1000,
        result_audio_export: bool=True,
        folder_codename: str=None,
        export_original: bool=True
        ) -> list[AudioSegment]:
    
    audio = get_audio(audio_path)
    
    filename = get_filename_wo_ext(audio_path)
    output_folder = make_output_folder(filename, output_path, folder_codename)
    
    total_sil_length = 0
    result_audio = AudioSegment.empty()
    for idx, silence in enumerate(excerpts_timemap, start=1):
        excrpt = audio[silence[0]:silence[1]+leading_preserve_msec].fade_in(fade_in_msec).fade_out(fade_out_msec)
        excrpt.export(f"{output_folder}/{idx}_{filename}.mp3".replace('//','/'))
        total_sil_length+=len(excrpt)
        print(f"{idx}. Length: {len(excrpt)}. Max volume: {excrpt.max}. Max dBFS: {excrpt.max_dBFS}.")
        result_audio += excrpt
    
    if result_audio_export:
        result_audio.export(f"{output_folder}/00_[final_{msec_to_minutes_by_total(total_sil_length)}]_{filename}.mp3")
    
    if export_original:
        audio.export(f"{output_folder}/01_[original_{msec_to_minutes_by_total(len(audio))}]_{filename}.mp3")
    
    print(f'Total [{folder_codename}] length is: {msec_to_minutes_by_total(total_sil_length)}. Original file length is: {msec_to_minutes_by_total(len(audio))}')
    
    return result_audio

def audio_to_flac(
        audio_path: str,
        output_folder: str,
        start_sec=None,
        finish_sec=None,
        fade_in_ms=100,
        fade_out_ms=100,
        delete_original=False,
        explicit_mono=False
        ) -> dict[str]:
    
    filename = audio_path.split('/')[-1]
    filename = filename.split('.')[0]

    if not explicit_mono:
        audio = get_audio(audio_path)
    else:
        audio = get_audio(audio_path, explicit_mono=True)
    
    if not start_sec and not finish_sec:
        pass
    elif start_sec and not finish_sec:
        audio = audio[start_sec*1000:]
    elif not start_sec and finish_sec:
        audio = audio[:finish_sec*1000+1]
    else:
        audio = audio[start_sec*1000:finish_sec*1000]
    
    output_path = f"{output_folder}/{filename}.flac".replace('//','/')
    
    # print(f"Num of audio channels: {audio.channels}")

    audio = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)
    audio.export(output_path, format="flac")

    if delete_original:
        os.remove(audio_path)
        print("The original file is deleted!")

    return {"audio_path": output_path, "audio_len_pretty": msec_to_minutes_by_total(len(audio)), "audio_len_ms": len(audio)}

def get_short_audio_transcript(audio_path: str):
    with open(audio_path, "rb") as audio_file:
        content = audio_file.read()
        audio = dict(content=content)
        try:
            config = dict(language_code="ru-RU", audio_channel_count=1, enable_automatic_punctuation=True)
            transcript = speech_to_text(config, audio)
        except:
            config = dict(language_code="ru-RU", audio_channel_count=2, enable_automatic_punctuation=True)
            transcript = speech_to_text(config, audio)
    
    if not transcript:
        transcript = ""
    
    return transcript


def get_samples_from_audiofile(
        filename: str,
        num_samples: int=5,
        sample_ms: [int|list[int]]=[300, 1200],
        min_fade_in_out: int = 50,
        apply_fade_in_out: bool=False,
        audio_lib: str=settings.audio_lib
        ) -> None:
    
    path_to_audio = f"{audio_lib}{filename}"
    audio = get_audio(path_to_audio)

    # length of audio in milliseconds
    duration_ms = len(audio)
    humanize_duration = minutes_seconds_from_millisec(duration_ms)
    logger.info(f"File provided: {filename}. Duration: {humanize_duration}")

    # now picking the random points
    segments = []
    for idx in range(num_samples):
        if type(sample_ms) == list:
            sample_duration_ms = random()*(max(sample_ms) - min(sample_ms)) + min(sample_ms)
            logger.info("Lenght of the segment %s is %s ms" % (idx, int(round(sample_duration_ms, 0))))
        
        start_sample_ms = randint(0, int(duration_ms - sample_duration_ms))
        end_sample_ms = int(start_sample_ms + sample_duration_ms)
        segments.append((start_sample_ms, end_sample_ms))
    
    
    # exporting samples
    for start, end in segments:
        fade_in_ms, fade_out_ms = None, None
        audio_sample = audio[start:end]
        output_sample_path=f"{sample_lib}{filename.replace('.mp3', '')}_ms{int(start/1000)}-{int(end/1000)}.mp3"
        audio_sample.export(output_sample_path, format='mp3')

        bpm, beat_times = define_bpm(output_sample_path)
        if len(beat_times) >= 2:
            inner_bpm = int(bpm)
            beat_times = np.round(beat_times * 1000,0)
            beat_times = beat_times.astype(int)
            if beat_times[-1] - beat_times[1] >= min_fade_in_out:
                audio_sample = audio_sample[beat_times[1]: beat_times[-1]]
                fade_in_ms = np.abs(beat_times[2] - beat_times[1])
                fade_out_ms = np.abs(beat_times[-1] - beat_times[-2])
        else:
            inner_bpm = "X" 
        
        if apply_fade_in_out and fade_in_ms and fade_out_ms:
            audio_sample = audio_sample.fade_in(fade_in_ms).fade_out(fade_out_ms)
        else:
            audio_sample = audio_sample.fade_in(min_fade_in_out).fade_out(min_fade_in_out)
        
        duration_ms = len(audio_sample)        
        outer_bpm = int(round(60000 / duration_ms, 0))

        music_key, corr_table = define_pitch(output_sample_path)

        key_bpm_output_sample_path = f"{sample_lib}{filename.replace('.mp3', '')[:20]}"
        key_bpm_output_sample_path += f"_s{int(start/1000)}-e{int(start/1000)}"
        key_bpm_output_sample_path += f"_d{duration_ms}_KEY_{music_key}_BPM_i{inner_bpm}_o{outer_bpm}.mp3"

        os.remove(output_sample_path)

        audio_sample.export(key_bpm_output_sample_path, format='mp3')

    return None



if __name__ == '__main__':
    
    audio_lib = settings.audio_lib
    sample_lib = settings.sample_lib

    files = get_files_from_folder(audio_lib)
    for idx, file in enumerate(files, start=1):
        logger.info(f"{idx} oo {len(files)}. {file}")
        file_format = get_file_format(file)
        num_samples = randint(0, 1)
        try:
            sample = get_samples_from_audiofile(
                file,
                num_samples=num_samples,
                sample_ms=[1080, 1100],
                apply_fade_in_out=False,
                audio_lib=audio_lib
            )
        except:
            continue

    print('Hello world!')
