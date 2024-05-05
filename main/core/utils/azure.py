from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os


def upload_clip_to_blob(conn_string, container_name, local_file_path):
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(conn_string)

    # Create a blob client
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"original_videos/{os.path.basename(local_file_path)}")

    # Upload the video file to blob storage
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data)
        
    return "Video uploaded successfully."

