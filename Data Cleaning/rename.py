import os
import glob

def rename_images_in_folder(folder_path):
    # Get all image files in the folder
    image_files = glob.glob(os.path.join(folder_path, '*.*'))
    
    # Sort files to ensure consistent renaming order
    image_files.sort()
    
    # Initialize image counter
    image_counter = 46051
    
    # Rename each image in the current folder
    for image_file in image_files:
        # Get the file extension
        file_extension = os.path.splitext(image_file)[1]
        
        # Construct the new filename
        new_filename = f"{image_counter}{file_extension}"
        
        # Create the full path for the new file
        new_file_path = os.path.join(folder_path, new_filename)
        
        # Rename the image
        os.rename(image_file, new_file_path)
        
        # Increment the image counter
        image_counter += 1

    print(f"Renamed images in folder: {folder_path}")

# Usage
# Call the function with the specific folder path you want to rename files in.
folder_path = r' '
rename_images_in_folder(folder_path)
