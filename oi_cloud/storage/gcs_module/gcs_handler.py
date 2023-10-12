from google.cloud import storage
import os

class GCS_Handler:
    def __init__(self, project_name, bucket_name):
        self.client = storage.Client(project_name)
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, local_file_path, gcs_file_name):
        blob = self.bucket.blob(gcs_file_name)
        blob.upload_from_filename(local_file_path)
        print(f'File {local_file_path} uploaded to {gcs_file_name}.')

    def download_file(self, gcs_file_name, local_file_path):
        blob = self.bucket.blob(gcs_file_name)
        blob.download_to_filename(local_file_path)
        print(f'File {gcs_file_name} downloaded to {local_file_path}.')

    def list_files(self):
        blobs = self.client.list_blobs(self.bucket)
        for blob in blobs:
            print(blob.name)
