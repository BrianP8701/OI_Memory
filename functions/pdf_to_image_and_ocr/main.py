import base64
import functions_framework
import helpers as h
import pytesseract
from google.cloud import datastore
import requests

@functions_framework.cloud_event
def pdf_to_image_and_ocr(event):
    '''
        Triggered by an event on a Cloud Pub/Sub topic. The function decodes the event data 
        containing a PDF page, converts that page into an image, and then extracts the text 
        from the image using Optical Character Recognition (OCR).
        
        This functions expects 1 page of pdf per event, meant to be ran in parallel.

        Args:
            event (dict): The event data from the Cloud Pub/Sub, which contains:
                - data (base64-encoded): The PDF page data.
                - attributes (dict): Additional attributes, specifically the page number and pdf_id

        Returns:
            None. However, it internally processes the page to extract text using OCR.
    '''
    # Decode the Pub/Sub message
    page_data = base64.b64decode(event['data']).decode('utf-8')
    page_num = event['attributes']['page_num']
    pdf_id = event['attributes']['pdf_id']

    image = h.pdf_to_png(page_data)
    extracted_text = pytesseract.image_to_string(image)
    h.upload_to_gcs('vigilant-yeti-400300', f'ExtractedTextChunks/{pdf_id}/{page_num}.txt', extracted_text)
    
    client = datastore.Client()
    key = client.key('PDFStatus', pdf_id)
    entity = client.get(key)
    entity['processed_pages'] += 1
    client.put(entity)

    # Check if all pages are processed
    if entity['processed_pages'] == entity['total_pages']:
        # Reassemble chunks into a single list of extracted text
        url = "https://northamerica-northeast2-vigilant-yeti-400300.cloudfunctions.net/raw_data_router"
    
        response = requests.post(url, json={"pdf_id": pdf_id})
        client.delete(key)