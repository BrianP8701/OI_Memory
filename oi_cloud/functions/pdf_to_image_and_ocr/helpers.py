from pdf2image import convert_from_bytes
from google.cloud import storage
from google.cloud import datastore
import json

def pdf_to_png(pdf):
    ''' Convert PDF bytes to images '''
    return convert_from_bytes(pdf)

def upload_to_gcs(bucket_name, path, data):
    """
    Uploads data to a specific path in a Google Cloud Storage bucket.

    Args:
    - bucket_name (str): Name of the GCS bucket.
    - path (str): Path (including filename) in the bucket to upload the data.
    - data (bytes): The data you want to upload.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.upload_from_string(data)
    
def delete_from_gcs(bucket_name, path):
    """
    Deletes a specific file from a Google Cloud Storage bucket.

    Args:
    - bucket_name (str): Name of the GCS bucket.
    - path (str): Path (including filename) in the bucket of the file to be deleted.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)
    blob.delete()
    
def merge_chunks_if_done(pdf_id):
    client = datastore.Client()
    key = client.key('PDFStatus', pdf_id)
    entity = client.get(key)
    entity['processed_pages'] += 1
    client.put(entity)

    # Check if all pages are processed
    if entity['processed_pages'] == entity['total_pages']:
        all_text = []
        storage_client = storage.Client()
        bucket = storage_client.bucket('llmkb-test-bucket')
        
        # Reassemble chunks into a single list of extracted text
        for page_num in range(entity['total_pages']):
            blob = bucket.blob(f'ExtractedTextChunks/{pdf_id}/{page_num}.txt')
            text = blob.download_as_string()
            all_text.append(text)
            blob.delete()
            
        # Upload extracted text to GCS
        blob = bucket.blob(f'Extracted_Text_From_Library/{pdf_id}.txt')
        data = json.dumps(all_text)
        blob.upload_from_string(data)
        client.delete(key)