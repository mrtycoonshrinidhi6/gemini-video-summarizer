from google.cloud import storage
from config.config import Config
import os

class CloudProcessor:
    def __init__(self):
        self.bucket_name = Config.CLOUD_BUCKET_NAME
        self.client = storage.Client(project=Config.CLOUD_PROJECT_ID)
        
    def upload_file(self, source_path, destination_blob_name):
        """Upload file to cloud storage"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(source_path)
        return f"gs://{self.bucket_name}/{destination_blob_name}"
    
    def download_file(self, blob_name, destination_path):
        """Download file from cloud storage"""
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        blob.download_to_filename(destination_path)
        return destination_path
    
    def process_video_from_cloud(self, blob_name, local_path):
        """Download video from cloud, process, and upload results"""
        # Download video
        video_path = self.download_file(blob_name, local_path)
        
        # Process video (this would be integrated with other components)
        # ...
        
        # Upload results
        result_paths = []
        # ... upload summary and keyframes
        
        return result_paths