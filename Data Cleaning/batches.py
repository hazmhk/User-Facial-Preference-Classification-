import os
import shutil
import random

# Path to the original folder containing the images
source_folder = r"D:\Hasnain\Codes\Dataset\dataset"

# Paths to the destination folders
destination_folders = [
    r"D:\Hasnain\Codes\Dataset\1",
    r"D:\Hasnain\Codes\Dataset\2",
    r"D:\Hasnain\Codes\Dataset\3",
    r"D:\Hasnain\Codes\Dataset\4",
    r"D:\Hasnain\Codes\Dataset\5"
]

# Create destination folders if they don't exist
for folder in destination_folders:
    os.makedirs(folder, exist_ok=True)

# List all files in the source folder
images = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

# Shuffle the list of images randomly
random.shuffle(images)

# Calculate the number of images per folder
images_per_folder = len(images) // len(destination_folders)

# Distribute images across the 5 folders
for i, image in enumerate(images):
    # Determine which folder to move the image to
    folder_index = i // images_per_folder
    if folder_index >= len(destination_folders):
        folder_index = len(destination_folders) - 1  # Make sure any leftover images go to the last folder

    # Source and destination paths
    src_path = os.path.join(source_folder, image)
    dest_path = os.path.join(destination_folders[folder_index], image)

    # Move the image to the appropriate folder
    shutil.move(src_path, dest_path)

print("Images have been distributed into 5 folders.")
