import os
import cv2
import numpy as np
from multiprocessing import Pool
from time import time
import json
import gc
import random

# Input and output paths
output_path = "/Volumes/transcend_ssd/itmo_screenology/full_frames"
videos_to_process_path = "itmo_screens/data/final_videos_with_paths_ssd.json"
green_frame_path = "/Users/viktorkertanov/projects/starless/itmo_screens/green_frame_output"
activation_matrix_path = "/Volumes/transcend_ssd/itmo_screenology/activation_matrix/activation_matrix.npy"
bigger_frames_path = "/Volumes/transcend_ssd/itmo_screenology/frames_185x104"

activation_matrix = np.load(activation_matrix_path)
bigger_frames_foldernames = os.listdir(bigger_frames_path)

# 8K resolution dimensions
frame_width = 7680
frame_height = 4320

# Frame dimensions and grid settings
small_frame_width = 52
small_frame_height = 92

bigger_frame_width = 104
bigger_frame_height = 185

num_cols = 147
num_rows = 46
num_img = num_cols * num_rows

# Total borders (these are added to the canvas to leave space between images)
total_border_width = 36
total_border_height = 88

# Border per frame (split equally)
horizontal_border_per_frame = total_border_width / 2
vertical_border_per_frame = total_border_height / 2

# Adjusted canvas size considering the borders: checking that everything is correct
canvas_width = num_cols * small_frame_width + total_border_width
canvas_height = num_rows * small_frame_height + total_border_height
