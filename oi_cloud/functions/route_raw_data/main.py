import functions_framework
import requests
import google.auth
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

@functions_framework.http
def route_raw_data(request):
    """
      Routes the raw data based on the provided request.

      Args:
          request (flask.Request): The HTTP request object is expected to have a JSON body with the following structure:
              {
                  "knowledge_graph": str,   # The name of the knowledge graph to route the data to.
                  "name": str,              # The name of the data.
                  "description": str,       # A brief description of the data.
                  "type": str,              # The type/category of the data.
                  "data": List              # [bucket_name, pdf_path]
              }

      Returns:
          flask.Response: A response object generated based on the processed data.
      """

    # Parse the request
    try:
        request_json = request.get_json(silent=False)
        knowledge_graph = request_json['knowledge_graph']
        name = request_json['name']
        description = request_json['description']
        type_ = request_json['type'] 
        data = request_json['data']
    except Exception as e:
        print(f"Error processing request: {e}")

        return ("Bad Request: Incorrect JSON format", 400)

    if type_ == 'textbook':
        url = 'https://northamerica-northeast2-vigilant-yeti-400300.cloudfunctions.net/extract_text_pdf'
        
        # Get credentials and request an identity token
        creds, project = google.auth.default()
        auth_req = g_requests.Request()
        id_token_info = id_token.fetch_id_token(auth_req, url)

        # Include the identity token in the 'Authorization' header
        headers = {
            'Authorization': f'Bearer {id_token_info}'
        }

        #return requests.post(url, json=data, headers=headers)

        return 'Called extract_text', 200

    return 'None processed', 400