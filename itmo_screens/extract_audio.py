import os
import ffmpeg
from multiprocessing import Pool

def extract_audio(video_info):
    input_video_path, output_audio_path = video_info

    try:
        # Set audio codec to 'libmp3lame' and specify the audio bitrate for high quality
        ffmpeg.input(input_video_path).output(output_audio_path, vn=None, acodec='libmp3lame', audio_bitrate='320k').run()
        print(f"Extracted audio from {input_video_path} to {output_audio_path}")
    except ffmpeg.Error as e:
        print(f"An error occurred while processing {input_video_path}: {e}")

def extract_audio_from_videos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [
        (os.path.join(input_folder, filename), os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.mp3"))
        for filename in os.listdir(input_folder)
        if filename.endswith(('.mp4', '.mkv', '.avi', '.mov'))  # Add other video file extensions as needed
    ]

    # Use multiprocessing to process files in parallel
    pool = Pool(processes=6)
    pool.map(extract_audio, video_files)
    pool.close()
    pool.join()

if __name__ == "__main__":
    input_folder = "/Users/viktorkertanov/Downloads/yt_shorts_itmo_screenology/yt_shorts"
    output_folder = "/Users/viktorkertanov/Downloads/yt_shorts_itmo_screenology/yt_shorts_audio"
    extract_audio_from_videos(input_folder, output_folder)
