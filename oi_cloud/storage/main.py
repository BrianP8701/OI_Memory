'''
Make sure to first set the environment variable to the service account key.:
    export GOOGLE_APPLICATION_CREDENTIALS="GOOGLE_APPLICATION_CREDENTIALS.json"
'''
from gcs_module.gcs_handler import GCSHandler

def main():
    bucket_name = 'oi-hackathon'
    gcs_handler = GCSHandler(bucket_name)

    # To upload a file:
    gcs_handler.upload_file('local_file_path.txt', 'gcs_file_name.txt')

    # To download a file:
    gcs_handler.download_file('gcs_file_name.txt', 'local_file_path.txt')

    # To list all files in the bucket:
    gcs_handler.list_files()

if __name__ == "__main__":
    main()
