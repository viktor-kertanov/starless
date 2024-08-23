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

# # Adjusted canvas size considering the borders
# canvas_width = num_cols * small_frame_width + total_border_width
# canvas_height = num_rows * small_frame_height + total_border_height


def flat_idx_to_row_col(flat_idx, num_cols):
    """
    Convert a flat index to row and column indices in a grid.

    Parameters:
    flat_idx (int): The flat index to convert.
    num_cols (int): The number of columns in the grid.

    Returns:
    tuple: A tuple (row_idx, col_idx) representing the row and column indices.
    """
    row_idx = flat_idx // num_cols
    col_idx = flat_idx % num_cols
    
    return row_idx, col_idx


def get_center_coordinates(row_idx, col_idx, frame_width, frame_height):
    """Calculate the center coordinates for placing the bigger frame."""
    top_left_x = col_idx * small_frame_width + horizontal_border_per_frame
    top_left_y = row_idx * small_frame_height + vertical_border_per_frame
    center_x = int(top_left_x + (frame_width - small_frame_width) // 2)
    center_y = int(top_left_y + (frame_height - small_frame_height) // 2)
    return center_x, center_y


import cv2

import cv2

def overlay_bigger_frame(
    img, bigger_frame, center_x, center_y, frame_width, frame_height, border_width=3, color=(0, 255, 0),
    shadow_offset=(3, 3), shadow_opacity=0.8):
    """Overlay the bigger frame onto the original image, add a shadow, and draw a green rectangle."""
    
    # Calculate the top-left coordinates for the overlay
    top_left_x = center_x - frame_width // 2
    top_left_y = center_y - frame_height // 2
    
    # Calculate the bottom-right coordinates for the overlay
    bottom_right_x = top_left_x + frame_width
    bottom_right_y = top_left_y + frame_height
    
    # Adjust for borders (to ensure overlay doesn't go out of image bounds)
    if top_left_x < 0:
        top_left_x = 0
    if top_left_y < 0:
        top_left_y = 0
    if bottom_right_x > img.shape[1]:
        bottom_right_x = img.shape[1]
        top_left_x = bottom_right_x - frame_width
    if bottom_right_y > img.shape[0]:
        bottom_right_y = img.shape[0]
        top_left_y = bottom_right_y - frame_height
    
    # Calculate the shadow position (slightly offset)
    shadow_top_left_x = top_left_x + shadow_offset[0]
    shadow_top_left_y = top_left_y + shadow_offset[1]
    shadow_bottom_right_x = bottom_right_x + shadow_offset[0]
    shadow_bottom_right_y = bottom_right_y + shadow_offset[1]
    
    # Ensure shadow stays within image bounds
    shadow_top_left_x = min(max(0, shadow_top_left_x), img.shape[1])
    shadow_top_left_y = min(max(0, shadow_top_left_y), img.shape[0])
    shadow_bottom_right_x = min(max(0, shadow_bottom_right_x), img.shape[1])
    shadow_bottom_right_y = min(max(0, shadow_bottom_right_y), img.shape[0])
    
    # Draw the semi-transparent shadow
    shadow_rect = img[shadow_top_left_y:shadow_bottom_right_y, shadow_top_left_x:shadow_bottom_right_x]
    black_overlay = np.zeros_like(shadow_rect, dtype=np.uint8)
    black_overlay[:, :] = (0, 0, 0)  # Black color
    cv2.addWeighted(black_overlay, shadow_opacity, shadow_rect, 1 - shadow_opacity, 0, shadow_rect)

    # Calculate the region of interest in the original image
    roi_width = bottom_right_x - top_left_x
    roi_height = bottom_right_y - top_left_y
    
    # Calculate the region of interest in the bigger_frame
    frame_roi = bigger_frame[:roi_height, :roi_width]

    # Draw a green rectangle on the bigger_frame before overlaying
    cv2.rectangle(frame_roi, (0, 0), (roi_width - 1, roi_height - 1), color, thickness=border_width)
    
    # Overlay the bigger_frame region onto the img
    img[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = frame_roi
    
    return img


def process_frame(frame_idx, frame_path, video_ids, activation_matrix, bigger_frames_path):
    img = cv2.imread(frame_path)
    
    # Get the column from activation matrix for the current frame
    active_videos = activation_matrix[:, frame_idx]
    active_video_indices = np.where(active_videos == 1)[0]
    print(f"Num of active indices on {frame_idx} is {len(active_video_indices)}")

    for idx in active_video_indices:
        video_id = video_ids[idx]
        row_idx, col_idx = flat_idx_to_row_col(idx, num_cols)

        # Calculate the center coordinates for placing the bigger frame
        center_x, center_y = get_center_coordinates(row_idx, col_idx, 184, 104)

        # Load the corresponding bigger frame for the video
        bigger_frame_foldername = [f for f in bigger_frames_foldernames if video_id in f][0]
        num_frames_cur_video = int(bigger_frame_foldername.split('__frms_')[1].split('_')[0])
        bigger_frame_folder = os.path.join(bigger_frames_path, bigger_frame_foldername)
        bigger_frame_files = [
            f for f in os.listdir(bigger_frame_folder)
            if os.path.isfile(os.path.join(bigger_frame_folder, f)) and f.lower().endswith(('.jpg', '.jpeg'))
        ]
        bigger_frame_files = sorted(bigger_frame_files)
        frame_to_use = bigger_frame_files[frame_idx % num_frames_cur_video]
        bigger_frame_path = os.path.join(bigger_frame_folder, frame_to_use)
        bigger_frame = cv2.imread(bigger_frame_path)

        # Overlay the bigger frame onto the original image
        img = overlay_bigger_frame(
            img,
            bigger_frame,
            center_x, center_y,
            bigger_frame_width, bigger_frame_height
        )

    # Save the modified frame
    output_img_path = os.path.join(green_frame_path, os.path.basename(frame_path))
    cv2.imwrite(output_img_path, img)
    return


def draw_rectangle(img, position, rectange_width, rectangle_height, border_width, color):
    top_left = (position[0], position[1])
    bottom_right = (position[0] + rectange_width, position[1] + rectangle_height)
    cv2.rectangle(img, top_left, bottom_right, color, thickness=border_width)
    
    return img

def draw_rectangles_on_a_frame(
    frames_idndices_to_greenify: list[int],
    frame_input_path: str,
    frame_output_path: str,
    frame_color: tuple[int],
    boder_width: int=2,
    ):
    img = cv2.imread(frame_input_path)
    for to_frame_idx in frames_idndices_to_greenify:
        row_idx, col_idx = flat_idx_to_row_col(to_frame_idx, num_cols)
        top_left_x = col_idx * small_frame_width + horizontal_border_per_frame
        top_left_y = row_idx * small_frame_height + vertical_border_per_frame
        top_left_coord = (int(top_left_x), int(top_left_y))
        print(f"top left coord: {top_left_coord}")
        img = draw_rectangle(
            img,
            top_left_coord,
            small_frame_width,
            small_frame_height,
            border_width,
            frame_color
        ) 
        
    # Save the result image
    output_img_path = os.path.join(green_frame_path, frame_output_path)
    cv2.imwrite(output_img_path, img)
    return

def draw_rectangles_on_a_frame(
    frames_idndices_to_greenify: list[int],
    frame_input_path: str,
    frame_output_path: str,
    frame_color: tuple[int],
    boder_width: int=2,
    ):
    img = cv2.imread(frame_input_path)
    for to_frame_idx in frames_idndices_to_greenify:
        row_idx, col_idx = flat_idx_to_row_col(to_frame_idx, num_cols)
        top_left_x = col_idx * small_frame_width + horizontal_border_per_frame
        top_left_y = row_idx * small_frame_height + vertical_border_per_frame
        top_left_coord = (int(top_left_x), int(top_left_y))
        print(f"top left coord: {top_left_coord}")
        img = draw_rectangle(
            img,
            top_left_coord,
            small_frame_width,
            small_frame_height,
            border_width,
            frame_color
        ) 
        
    # Save the result image
    output_img_path = os.path.join(green_frame_path, frame_output_path)
    cv2.imwrite(output_img_path, img)
    return





if __name__ == "__main__":
    with open(videos_to_process_path, 'r', encoding='UTF-8') as f:
        videos_to_process = json.load(f)
    
    print(f"Num videos overall: {len(videos_to_process)}")
    num_videos = len(videos_to_process)
    videos_w_indices = [(idx, video_id) for idx, (video_id, path) in enumerate(videos_to_process.items())]

    video_ids = list(videos_to_process.keys())
    # video_ids.sort()
    
    frames_to_process = [
        f for f in os.listdir(output_path)
        if os.path.isfile(os.path.join(output_path,f)) and f.lower().endswith(('.jpg', '.jpeg'))
    ]
    frames_to_process.sort(key = lambda x: int(x.split('.jpg')[0].replace('frame', '')))
    frame_color = (0, 255, 0)
    border_width=2
    
    for frame_idx, frame_path in enumerate(frames_to_process[4000:5000]):
        input_path = os.path.join(output_path, frame_path)
        input_frame_idx = int(frame_path.split('.')[0].replace('frame', ''))
        process_frame(input_frame_idx, input_path, video_ids, activation_matrix, bigger_frames_path)
    

    print("Hello world!")