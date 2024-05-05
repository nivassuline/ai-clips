from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os


def upload_clip_to_blob(conn_string, container_name, local_file_path):
    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(conn_string)

    # Create a blob client
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"trimmed_tmp/{os.path.basename(local_file_path)}")

    # Upload the video file to blob storage
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data)
        
    return "Video uploaded successfully."




def download_blob_from_azure(connection_string, container_name, filename,blob_path):
    """
    Download a blob from Azure Blob Storage to a local file.

    Args:
    - connection_string (str): Azure Storage account connection string.
    - container_name (str): Name of the container where the blob is stored.
    - filename (str): Name of the blob to download.
    - local_file_path (str): Local path where the downloaded file will be saved.

    Returns:
    - bool: True if the blob was downloaded successfully, False otherwise.
    """
    try:
        local_file_path = f"tmp/{filename}"
        # Create a BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

        # Download blob data to a local file
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Blob '{filename}' downloaded to '{local_file_path}' successfully.")
        return local_file_path
    except Exception as e:
        print(f"Error downloading blob '{filename}': {e}")
        return False