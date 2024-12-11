import os
from google.cloud import storage

def download_all_blobs(bucket_name, destination_folder):
    # Initialize a storage client
    client = storage.Client()

    # Get the bucket object
    bucket = client.bucket(bucket_name)

    # List all the blobs in the bucket
    blobs = bucket.list_blobs()

    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Download each blob
    for blob in blobs:
        # Create the full local file path
        file_path = os.path.join(destination_folder, blob.name)

        # Ensure the folder structure is preserved
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Download the blob to the file
        blob.download_to_filename(file_path)
        print(f'Downloaded {blob.name} to {file_path}')

# Example usage
bucket_name = ' '
destination_folder = ' '
download_all_blobs(bucket_name, destination_folder)
