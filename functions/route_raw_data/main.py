import functions_framework
import requests

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
        
        response = requests.post(url, json=data)
        return response.text, response.status_code

    return 'None processed', 400