import base64
import functions_framework
import helpers as h
import pytesseract

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
    
    # Upload extracted text to GCS
    h.upload_to_gcs('llmkb-test-bucket', f'ExtractedTextChunks/{pdf_id}/{page_num}.txt', extracted_text)
    
    # Merges chunks and saves to GCS if all pages are processed
    h.merge_chunks_if_done(pdf_id)