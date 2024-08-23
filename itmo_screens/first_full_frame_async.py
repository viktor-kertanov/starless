import os
import cv2
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from time import time
import json
import gc
from multiprocessing import cpu_count
import cProfile
import pstats

# Input and output paths
input_path = "/Users/viktorkertanov/projects/itmo_screenology"
output_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/full_frames"
videos_to_process_path = "itmo_screens/data/final_videos_with_paths.json"

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

with open(videos_to_process_path, 'r', encoding='UTF-8') as f:
    videos_to_process = json.load(f)

paths_to_process = [v for _, v in videos_to_process.items()]

def flat_idx_to_row_col(flat_idx, num_cols):
    row_idx = flat_idx // num_cols
    col_idx = flat_idx % num_cols
    return row_idx, col_idx

def read_image(subframe_path):
    return cv2.imread(subframe_path)

async def create_8k_frame_from_videos(paths_to_process: list[str], output_path: str, frame_number: int = 0, batch_size: int = 500):
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
    subframe_paths = []
    subframes = []

    for subdir in paths_to_process:
        try:
            subdir_name = subdir.split('/')[-1]
            num_frames_str = subdir_name.split('__frms_')[-1].split('_')[0]
            video_id = subdir_name.split('__frms_')[0]

            if not num_frames_str.isdigit():
                raise ValueError(f"Invalid number of frames: {num_frames_str}")

            num_frames = int(num_frames_str)
            file_idx = frame_number % num_frames
            subframe_path = os.path.join(subdir, f'{video_id}_id_frame_{str(file_idx).zfill(5)}.jpg')
            subframe_paths.append(subframe_path)
            subframes.append(subframe_path)
        except Exception as e:
            print(f"Error processing subdir {subdir}: {e}")

    start = time()
    num_batches = int(np.ceil(len(subframes) / batch_size))

    for batch_idx in range(num_batches):
        start_subframe = batch_idx * batch_size
        end_subframe = min(start_subframe + batch_size, len(subframes))

        row_col_data = [flat_idx_to_row_col(el, num_cols) for el in range(start_subframe, end_subframe)]
        x_y_offsets = [
            (
                int(el[1] * small_frame_width + horizontal_border_per_frame),
                int(el[0] * small_frame_height + vertical_border_per_frame)
            )
            for el in row_col_data
        ]

        start_read_img = time()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=cpu_count()-1) as executor:
            imgs = await asyncio.gather(*[loop.run_in_executor(executor, read_image, path) for path in subframes[start_subframe:end_subframe]])

        end_read_img = time()
        print(f"\nFrame idx:{frame_number}//Batch: {batch_idx}-out-of-{num_batches}. Took: {end_read_img-start_read_img:.1f} sec\n")
        
        for img_idx, img in enumerate(imgs):
            if img is not None:
                x_offset = x_y_offsets[img_idx][0]
                y_offset = x_y_offsets[img_idx][1]
                canvas[y_offset:y_offset + small_frame_height, x_offset:x_offset + small_frame_width] = img
        
        del imgs
        gc.collect()

    output_file = os.path.join(output_path, f"frame{str(frame_number).zfill(5)}.jpg")
    cv2.imwrite(output_file, canvas)

    end = time()
    print(f"Elapsed time: {end - start:.1f} seconds")

async def process_frames(frame_idx):
    await create_8k_frame_from_videos(paths_to_process, output_path, frame_number=frame_idx, batch_size=300)

async def main():
    start_frame = 500
    stop_frame = 1000
    frame_indices = list(range(start_frame, stop_frame + 1))
    done_frames = [int(f.split('frame')[-1].split('.')[0]) for f in os.listdir(output_path) if '.jpg' in f]
    frame_indices = [f for f in frame_indices if f not in done_frames]
    print(f"Overall frames: {len(frame_indices)}")

    start = time()
    await asyncio.gather(*[process_frames(idx) for idx in frame_indices])
    end = time()
    print(f"Overall {len(frame_indices)} frames took {(end-start)/60:.1f} min")
    print("Processing complete.")

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(main())
    profiler.disable()

    with open("profile_stats.txt", "w") as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats()
