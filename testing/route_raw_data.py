import requests
import os

token = os.environ.get('TOKEN')

def call_route_raw_data(data_payload):
    url = "https://northamerica-northeast2-vigilant-yeti-400300.cloudfunctions.net/raw_data_router"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data_payload, headers=headers)
    
    # response = requests.post(url, json=data_payload)
    
    print(response.status_code)
    print(response.text)


data_payload = {
    "knowledge_graph": "test_kg",
    "name": "DL_MIT",
    "description": "",
    "type": "textbook",
    "data": ["llmkb_test_bucket", "Raw_Data_Library/DL_MIT.pdf"]
}

call_route_raw_data(data_payload)
