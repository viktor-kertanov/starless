import cv2
import numpy as np
import os
import json

def calculate_frame_properties(frame):
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Calculate the average color properties in BGR
    mean_bgr = np.mean(frame, axis=(0, 1))
    mean_b = mean_bgr[0]
    mean_g = mean_bgr[1]
    mean_r = mean_bgr[2]

    # Calculate the average brightness (V channel in HSV)
    mean_brightness = np.mean(hsv[:, :, 2])

    # Calculate other color metrics
    mean_hue = np.mean(hsv[:, :, 0])
    mean_saturation = np.mean(hsv[:, :, 1])

    return {
        'r': mean_r,
        'g': mean_g,
        'b': mean_b,
        'brightness': mean_brightness,
        'hue': mean_hue,
        'saturation': mean_saturation
    }

def process_video_frames(frames_dir, video_name, frame_analysis_output_dir):
    frame_files = [f for f in os.listdir(frames_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    total_properties = {
        'r': 0,
        'g': 0,
        'b': 0,
        'brightness': 0,
        'hue': 0,
        'saturation': 0
    }
    num_frames = len(frame_files)
    
    frame_data = {}

    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        frame = cv2.imread(frame_path)
        frame_properties = calculate_frame_properties(frame)
        
        frame_data[frame_file] = frame_properties
        
        for key in total_properties:
            total_properties[key] += frame_properties[key]
    
    # Calculate the average properties
    average_properties = {key: total_properties[key] / num_frames for key in total_properties}
    
    # Save frame-level data to JSON
    frame_analysis_file = os.path.join(frame_analysis_output_dir, f"{video_name}_frame_analysis.json")
    with open(frame_analysis_file, 'w') as f:
        json.dump(frame_data, f, indent=4)
    
    return average_properties

def process_all_videos(videos_frames_dirs, frame_analysis_output_dir, video_analysis_output_file):
    videos_properties = {}
    for video_name, frames_dir in videos_frames_dirs.items():
        videos_properties[video_name] = process_video_frames(frames_dir, video_name, frame_analysis_output_dir)
    
    # Save video-level aggregated data to JSON
    with open(video_analysis_output_file, 'w') as f:
        json.dump(videos_properties, f, indent=4)
    
    return videos_properties

# Example usage
videos_frames_dirs = {
    'video1': 'path/to/video1/frames',
    'video2': 'path/to/video2/frames',
    # Add more videos and their frame directories as needed
}

frame_analysis_output_dir = 'path/to/save/frame_analysis'
video_analysis_output_file = 'path/to/save/video_analysis.json'

# Create output directories if they don't exist
os.makedirs(frame_analysis_output_dir, exist_ok=True)

video_color_properties = process_all_videos(videos_frames_dirs, frame_analysis_output_dir, video_analysis_output_file)
for video, properties in video_color_properties.items():
    print(f"Video: {video}")
    for prop, value in properties.items():
        print(f"  {prop}: {value}")
