from PyPDF2 import PdfReader, PdfWriter
from google.cloud import pubsub_v1, storage
import io
import os

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('vigilant-yeti-400300', 'extract_text_pdf_topic')
print(topic_path)

def split_pdf_and_publish(bucket_name, pdf_path):
    # Initialize GCS client and retrieve the PDF bytes
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(pdf_path)
    pdf_bytes = blob.download_as_bytes()
    pdf_id = str(os.path.basename(pdf_path).replace('.pdf', ''))

    # Load the PDF data from the bytes
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(pdf_reader.pages)
    print(type(num_pages))  # should print <class 'int'>
    print(type(str(num_pages)))  # should print <class 'str'>
    for page_num in range(num_pages):
        writer = PdfWriter()
        writer.add_page(pdf_reader.pages[page_num])
        
        page_byte_arr = io.BytesIO()
        writer.write(page_byte_arr)
        encoded_page = page_byte_arr.getvalue()

        # Publishing page to Pub/Sub
        attributes = {"page_num": "{}".format(page_num)}
        print(type(topic_path), topic_path)
        print(page_num)
        print(type(pdf_id), pdf_id)
        print(type(str(page_num)), str(page_num))
        publisher.publish(topic_path, data=encoded_page, attributes={"page_num":str(page_num), "pdf_id":pdf_id})

    return f"Published {num_pages} pages to Pub/Sub!", 200