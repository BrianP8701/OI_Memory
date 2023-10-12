from google.cloud import storage
import dill
from llama_index.node_parser import HierarchicalNodeParser
from llama_index import VectorStoreIndex
from llama_index import SimpleDirectoryReader
from llama_index.schema import NodeWithScore

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
            self.index = self.retrieve_pickle_object_from_gcs(llama_index_gcs_path)
            self.retriever = self.index.as_retriever()

    def create_new_index(self, gcs_index_path):
        self.index = VectorStoreIndex([])
        self.retriever = self.index.as_retriever()
        self.save_pickle_to_gcs(gcs_index_path, self.retriever)

    def upload_directory_to_index(self, local_directory_path):
        documents = SimpleDirectoryReader(local_directory_path, recursive=True).load_data()
        for doc in documents:
            self.index.insert(doc)
        self.retriever = self.index.as_retriever()
    
    def retrieve_context(self, messages):
        retriever = self.retriever
        retrieved_nodes: list[NodeWithScore] = retriever.retrieve(messages[-1]['message'])
        return '\n'.join([node.text for node in retrieved_nodes])

    def retrieve_index_from_gcs(self, filename):
        
        
        
        blob = self.bucket.blob(filename)
        data = blob.download_as_bytes()
        return dill.loads(data)  # Use dill.loads instead of pickle.loads
    
    def save_index_to_gcs(self, filename, obj):
        
        serialized_index = VectorStoreIndex.from_vector_store(self.index)
        index.persist('temp_serialized_index')
        
        blob = self.bucket.blob(filename)
        pickle_bytes = dill.dumps(obj)  # Use dill.dumps instead of pickle.dumps
        blob.upload_from_string(pickle_bytes, content_type='application/octet-stream')

my_oi_cloud = OI_Cloud_Handler('vigilant-yeti-400300', 'oi-hackathon')
print('okey')
my_oi_cloud.create_new_index('llama_index.pkl')
print('dokey')
my_oi_cloud.upload_document_to_index('library')
print('pokey')


from llama_index import VectorStoreIndex

# Assuming you have a VectorStoreIndex object named index
index = VectorStoreIndex.from_vector_store(vector_store)

# Persist the index
index.persist('path/to/save/index')

from llama_index import VectorStoreIndex

# Load the index
index = VectorStoreIndex.from_persist_path('path/to/save/index')