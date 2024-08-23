import numpy as np
from multiprocessing import Pool
from time import time
import json
import matplotlib.pyplot as plt
from itmo_screens.frame_activation.normalization import advanced_normalizing_function
import os

# Function to generate pauses
def generate_pauses(num_pauses=100):
    return np.random.choice(pause_durations, size=num_pauses, p=weights)

# Define a function to insert pauses into the y-values
def insert_pauses(y_vals, frame_interval=450):
    y_paused = y_vals.copy()
    num_frames = len(y_vals)
    pause_indices = np.arange(0, num_frames, frame_interval)
    
    for start_idx in pause_indices:
        pause_duration = generate_pauses(num_pauses=1)[0]
        end_idx = min(start_idx + pause_duration, num_frames)
        y_paused[start_idx:end_idx] = 0
    
    return y_paused

# Input and output paths
output_path = "/Volumes/transcend_ssd/itmo_screenology/full_frames"
videos_to_process_path = "itmo_screens/data/final_videos_with_paths_local.json"

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
print(f"Number of files to process: {len(paths_to_process)}")

x_start = -4
x_stop = 4
num_x = 1000

x = np.linspace(x_start, x_stop, num_x)
y = -.1 * x**2

NUM_FRAMES = 9000

points = advanced_normalizing_function(
    input=(0, NUM_FRAMES),
    output=(0, 53),
    function_range=(x_start, x_stop),
    function= lambda x: -.1 * x**2 + .4 * np.sin(15 * x),
    num_points=10000,
    do_plot=False
)

# Original values
y_vals = np.array([p[1] for p in points])
x_vals = [p[0] for p in points]
plt.figure(figsize=(10, 6))
plt.plot(x_vals, y_vals, label='Original Function', color='red', linestyle='--')

# Adding noise to the y-values
noise = np.random.normal(0, 5, size=len(y_vals))

y_vals += noise
y_vals = np.where(y_vals < 0, 0, y_vals)

# Adding pauses to the 
pause_durations = np.array([0, 15, 30, 60, 150, 300])
weights = np.array([0.3, 0.175, 0.1, 0.2, 0.1, 0.125])  # Adjust these weights as needed
print(f"Sum weights: {weights.sum()}")
# Normalize the weights to ensure they sum to 1
weights = weights / weights.sum()


# Adding noise to the y-values (original)
noise = np.random.normal(0, 5, size=len(y_vals))
y_vals += noise
y_vals = np.where(y_vals < 0, 0, y_vals)

# Adjust the y-values by subtracting a constant value
y_vals -= 40

# Insert pauses into the y-values
y_vals = insert_pauses(y_vals, frame_interval=300)
y_vals = np.where(y_vals < 0, 0, y_vals)

# Plotting the modified y-values with pauses
plt.plot(x_vals, y_vals, '-', linewidth=1, label='Function with Pauses', color='blue')
plt.plot((-100, NUM_FRAMES), (0, 0), 'k--', linewidth=2)

# Add labels and title
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Function with Random Noise and Pauses')
plt.legend()
# plt.show()


num_videos = 6762
num_frames = 9000
min_duration = 15  # Minimum duration for an active video in frames

# Initialize the matrix with zeros
activity_matrix = np.zeros((num_videos, num_frames), dtype=np.uint8)

# Example normal distribution for video duration
mean_duration = 60  # Mean duration in frames
std_duration = 20   # Standard deviation in frames

# Process each frame
for frame in range(num_frames):
    active_videos = int(y_vals[frame])  # Number of active videos for this frame
    
    # Get indices of currently active videos
    currently_active = np.where(activity_matrix[:, frame - 1] == 1)[0] if frame > 0 else np.array([])
    
    # Determine videos to keep active based on their previous duration
    if len(currently_active) > active_videos:
        durations = np.sum(activity_matrix[currently_active, :frame], axis=1)
        keep_active = currently_active[durations >= min_duration]
        if len(keep_active) > active_videos:
            keep_active = np.random.choice(keep_active, active_videos, replace=False)
        activity_matrix[keep_active, frame] = 1
        active_videos -= len(keep_active)
    
    # If more videos need to be activated
    if active_videos > 0:
        inactive_videos = np.where(activity_matrix[:, frame] == 0)[0]
        selected_videos = np.random.choice(inactive_videos, active_videos, replace=False)
        durations = np.random.normal(mean_duration, std_duration, size=selected_videos.shape).astype(int)
        for i, video in enumerate(selected_videos):
            end_frame = min(frame + durations[i], num_frames)
            activity_matrix[video, frame:end_frame] = 1

# Optionally, plot the activity matrix
plot_matrix = 1 - activity_matrix
plt.figure(figsize=(12, 8))
plt.imshow(plot_matrix, aspect='auto', cmap='gray')
plt.colorbar(label='Video Active (1) / Inactive (0)')
plt.xlabel('Frames')
plt.ylabel('Video Index')
plt.title('Video Activity Matrix')
plt.show()

#---------------------

num_videos, num_frames = activity_matrix.shape

# Step 1: Sum the number of `1`s in each column (total active videos per frame)
column_sums = np.sum(activity_matrix, axis=0)

# Step 2: Sort the columns by the number of `1`s in descending order
sorted_indices = np.argsort(column_sums)[::-1]  # [::-1] for descending order

# Step 3: Calculate the number of top columns to select (10% of the total columns)
top_10_percent_count = int(np.ceil(0.1 * num_frames))

# Select the indices of the top 10% columns
top_columns_indices = sorted_indices[:top_10_percent_count]

# Step 4: Print the selected columns and their counts
print("Top 10% columns with the most `1`s (active videos):")
for idx in top_columns_indices:
    print(f"Column {idx}: {column_sums[idx]} active videos")


print("Matrix processing complete!")

# Directory and file path to save the matrix
output_directory = "/Volumes/transcend_ssd/itmo_screenology/activation_matrix/"
output_file = os.path.join(output_directory, "activation_matrix.npy")

# Ensure the directory exists
os.makedirs(output_directory, exist_ok=True)

# Save the matrix as a .npy file
np.save(output_file, activity_matrix)

print(f"Matrix saved successfully at: {output_file}")

print("Hello world!")