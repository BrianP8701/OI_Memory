from PyPDF2 import PdfFileReader, PdfFileWriter
from google.cloud import pubsub_v1, storage
import io
from google.cloud import datastore


publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('vigilant-yeti-400300', 'extract_text_pdf_topic')

def split_pdf_and_publish(bucket_name, pdf_path):
    # Initialize GCS client and retrieve the PDF bytes
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(pdf_path)
    pdf_bytes = blob.download_as_bytes()

    pdf = PdfFileReader(io.BytesIO(pdf_bytes))
    total_pages = pdf.getNumPages()
    pdf_id = pdf_path.split('/')[-1].replace('.pdf', '')
    
    # Save to Datastore
    client = datastore.Client()
    entity = datastore.Entity(key=client.key('PDFStatus', pdf_id))
    entity.update({
        'total_pages': total_pages,
        'processed_pages': 0
    })
    client.put(entity)
    
    # Split PDF into individual pages
    for page_num in range(pdf.getNumPages()):
        writer = PdfFileWriter()
        writer.addPage(pdf.getPage(page_num))
        
        page_byte_arr = io.BytesIO()
        writer.write(page_byte_arr)
        encoded_page = page_byte_arr.getvalue()

        # Publishing page to Pub/Sub
        publisher.publish(topic_path, data=encoded_page, attributes={"page_num": str(page_num), "pdf_id": pdf_id})

    return f"Published {pdf.getNumPages()} pages to Pub/Sub!", 200