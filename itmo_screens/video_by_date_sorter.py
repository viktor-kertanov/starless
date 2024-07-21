import json
import os
from datetime import datetime
from dateutil import parser


dates_path = "itmo_screens/data/original-watch-history-youtube.json"
output_path = "itmo_screens/data/sorted_videos_history.json"
folders_path = "/Volumes/KERTANOV_VIKTOR/itmo_screenology/frames_92x52"

with open(dates_path, 'r', encoding='UTF-8') as f:
    file_data = json.load(f)

dates_by_video = {e.get('titleUrl','').split('?v=')[-1]:e['time'] for e in  file_data}

folders = [e.split('/')[-1].split('__frms')[0] for e in os.listdir(folders_path) if '.' not in e]


final_data = {f: parser.isoparse(dates_by_video[f]) for f in folders}

sorted_final_data = dict(sorted(final_data.items(), key=lambda item: item[1]))
sorted_final_data = {k: v.isoformat() for k, v in sorted_final_data.items()}

with open(output_path, 'w', encoding='UTF-8') as f:
    json.dump(sorted_final_data, f, ensure_ascii=False, indent=4)

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

folders_path = "itmo_screens/data/final_videos_sorted_by_date.json"
with open(folders_path, 'r', encoding='UTF-8') as f:
    videos_to_process = json.load(f)

video_ids_sorted = [e for e in videos_to_process][:num_img]

subdirs = [
    os.path.join(input_path, d) for d in os.listdir(input_path)
    if os.path.isdir(os.path.join(input_path, d))
]

video_paths = {e.split('/')[-1].split('__frms')[0]:e for e in subdirs}
video_ids_w_paths = {e:video_paths[e] for e in video_ids_sorted}

videos_to_process_data_path = "itmo_screens/data/final_videos_with_paths.json"
with open(videos_to_process_data_path, 'w', encoding='UTF-8') as f:
    json.dump(video_ids_w_paths, f, ensure_ascii=False, indent=4)

print("HEllo world!")