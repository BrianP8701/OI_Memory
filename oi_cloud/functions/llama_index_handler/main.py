from google.cloud import storage
import pickle
from llama_index.node_parser import HierarchicalNodeParser
from llama_index import VectorStoreIndex
from llama_index import SimpleDirectoryReader
from llama_index.schema import NodeWithScore
import functions_framework

@functions_framework.http
def llama_index_handler(request):
    """
    This function processes the HTTP request to interact with a llama index stored on Google Cloud Storage.
    It dispatches the request to various handlers based on the function name specified in the request JSON.

    Functions:
    - "create_new_index": Creates a new empty index and saves it to the specified GCS path.
    - "upload_document_to_index": Reads documents from a specified local directory and adds them to the index.
    - "retrieve_context": Retrieves context based on the given messages from the request JSON.
    
    Args:
        request (flask.Request): The request object. Expected JSON structure:
            {
                "function_name": str,           # Name of the function to call.
                "project_name": str,            # GCP project name.
                "bucket_name": str,             # GCS bucket name.
                "llama_index_gcs_path": str,    # GCS path to the llama index pickle file (optional).
                ...                             # Other fields depending on the function_name.
            }

    Returns:
        flask.Response: A response object with the result of the dispatched function call, or an error message.
    """
    request_json = request.get_json(silent=False)
    function_name = request_json['function_name']
    project_name = request_json['project_name']
    bucket_name = request_json['bucket_name']
    llama_index_gcs_path = request_json['llama_index_gcs_path']
    
    handler = OI_Cloud_Handler(project_name, bucket_name, llama_index_gcs_path)
    try:
        result = handler.dispatch(function_name, request_json)
        return result, 200
    except Exception as e:
        return f"Invalid Input: {e}", 500

class OI_Cloud_Handler:
    '''
    We just store the llama-index object in a pickle file on the cloud. You can add documents to the index and 
    use it to retrieve context from the documents.
    '''
    def __init__(self, project_name, bucket_name, llama_index_gcs_path=None):
        self.client = storage.Client(project_name)
        self.bucket = self.client.bucket(bucket_name)
        
        self.node_parser = HierarchicalNodeParser.from_defaults()
        if llama_index_gcs_path is not None:
            self.index = self.retrieve_pickle_object_from_gcs(bucket_name, llama_index_gcs_path)        
            self.retriever = self.index.as_retriever()

    def dispatch(self, function_name, *args, **kwargs):
        function_map = {
            'create_new_index': self.create_new_index,
            'upload_document_to_index': self.upload_document_to_index,
            'retrieve_context': self.retrieve_context
        }
        if function_name not in function_map:
            raise ValueError(f"Function {function_name} not found.")
        function_map[function_name](*args, **kwargs)
        return f"{function_name} called successfully."
    
    def create_new_index(self, gcs_index_path):
        self.index = VectorStoreIndex([])
        self.save_pickle_to_gcs(self.index, gcs_index_path)
        self.retriever = self.index.as_retriever()

    def upload_directory_to_index(self, local_directory_path):
        documents = SimpleDirectoryReader(local_directory_path, recursive=True).load_data()
        for doc in documents:
            self.index.insert(doc)
        self.retriever = self.index.as_retriever()
            
    def retrieve_context(self, messages):
        retriever = self.retriever
        retrieved_nodes: list[NodeWithScore] = retriever.retrieve(messages[-1]['message'])
        return '\n'.join([node.text for node in retrieved_nodes])

    def retrieve_pickle_object_from_gcs(self, filename):
        blob = self.bucket.blob(filename)
        data = blob.download_as_bytes()
        return pickle.loads(data)
    
    def save_pickle_to_gcs(self, filename, obj):
        blob = self.bucket.blob(filename)
        pickle_bytes = pickle.dumps(obj)
        blob.upload_from_string(pickle_bytes, content_type='application/octet-stream')