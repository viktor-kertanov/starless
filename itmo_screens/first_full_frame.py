import os
import cv2
import numpy as np
from multiprocessing import Pool
from time import time
import json

# Input and output paths
input_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/frames_92x52"
output_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/full_frames"

# 8K resolution dimensions
frame_width = 7680
frame_height = 4320

# Frame dimensions and grid settings
small_frame_width = 52
small_frame_height = 92

num_cols = 147
num_rows = 46
num_img = num_cols * num_rows

# Total borders (these are added to the canvas to leave space between images)
total_border_width = 36
total_border_height = 88

# Border per frame (split equally)
horizontal_border_per_frame = total_border_width / 2
vertical_border_per_frame = total_border_height / 2

# Adjusted canvas size considering the borders
canvas_width = num_cols * small_frame_width + total_border_width
canvas_height = num_rows * small_frame_height + total_border_height

videos_to_process_path = "itmo_screens/data/final_videos_with_paths.json"

with open(videos_to_process_path, 'r', encoding='UTF-8') as f:
    videos_to_process = json.load(f)

paths_to_process = [v for _, v in videos_to_process.items()]

for p in paths_to_process:
    num_frames

def create_8k_frame_from_videos(paths_to_process: list[str], output_path: str, frame_number: int = 0, ):
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    subframe_indices = dict()
    for subdir_idx, subdir in enumerate(paths_to_process):
        files = [
            os.path.join(subdir, f) for f in os.listdir(subdir)
            if os.path.isfile(os.path.join(subdir, f)) and f.lower().endswith(('.jpg', '.jpeg'))
        ]
        files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
        file_idx = frame_number % len(files)
        file = files[file_idx]
        subframe_indices[subdir] = file
    
    print('Hello world')
    
    #     col_idx = subdir_idx % num_cols
    #     row_idx = subdir_idx // num_cols

    #     img = cv2.imread(file)
    #     x_offset = int(col_idx * small_frame_width + horizontal_border_per_frame)
    #     y_offset = int(row_idx * small_frame_height + vertical_border_per_frame)
    #     canvas[y_offset:y_offset + small_frame_height, x_offset:x_offset + small_frame_width] = img

    #     print(f"Frame # {frame_number}. Finished {subdir_idx} out of {len(paths_to_process)}")
    #     if subdir_idx % 100 == 0:
    #         output_file = os.path.join(output_path, f"{str(subdir_idx).zfill(5)}.jpg")
    #         cv2.imwrite(output_file, canvas)
    
    # output_file = os.path.join(output_path, f"finalframe_{str(frame_number).zfill(5)}.jpg")
    # cv2.imwrite(output_file, canvas)

def process_frames(f_idx):
    create_8k_frame_from_videos(input_path, output_path, frame_number=f_idx)


if __name__ == '__main__':
    num_frames = 180
    num_processes = 8  # Adjust based on your CPU cores
    frame_indices = range(1, num_frames)

    create_8k_frame_from_videos(paths_to_process, output_path, 0)
    
    with Pool(processes=num_processes) as pool:
        pool.map(process_frames, frame_indices)
    
    print("Processing complete.")
