import functions_framework
import helpers as h

@functions_framework.http
def extract_text_pdf(request):
    """
      Extracts text from a PDF per page horizontally

      Args:
          request (flask.Request): The HTTP request object is expected to have a JSON body with the following structure:
              {
                  "knowledge_graph": str, # The name of the knowledge graph to route the data to.
                  "name": str,          # The name of the data.
                  "description": str,   # A brief description of the data.
                  "type": str,          # The type/category of the data.
                  "data": List          # [bucket_name, pdf_path]
              }

      Returns:
          flask.Response: A response object generated based on the processed data.
      """

    request_json = request.get_json(silent=False)
    bucket_name = request_json['data'][0]
    pdf_path = request_json['data'][1]
    return h.split_pdf_and_publish(bucket_name, pdf_path)