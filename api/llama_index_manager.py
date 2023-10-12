from google.cloud import storage
from llama_index.node_parser import HierarchicalNodeParser
from llama_index import VectorStoreIndex, load_index_from_storage, SimpleDirectoryReader, StorageContext

from llama_index.schema import NodeWithScore

import os
import gcsfs

class LLAMA_Index_Manager:
    '''
    We just store the llama-index object in a json file on the cloud. You can add documents to the index and 
    use it to retrieve context from the documents.
    
    retieve_context(messages) -> str
    '''
    def __init__(self, project_name, bucket_name, llama_index_gcs_path):
        self.client = storage.Client(project_name)
        self.bucket = self.client.bucket(bucket_name)
        self.bucket_name = bucket_name
        self.node_parser = HierarchicalNodeParser.from_defaults()
        self.llama_index_gcs_path = llama_index_gcs_path
        
        self.gcs = gcsfs.GCSFileSystem(
            project=project_name,
            token='GOOGLE_APPLICATION_CREDENTIALS.json'
        )
        
        if self.check_folder_exists(llama_index_gcs_path):
            self.index = self.retrieve_index_from_gcs()    
            self.retriever = self.index.as_retriever()
        else:
            self.create_new_index()

    def dispatch(self, function_name, *args, **kwargs):
        function_map = {
            'create_new_index': self.create_new_index,
            'retrieve_context': self.retrieve_context,
            'save_index_to_gcs': self.save_index_to_gcs
        }
        if function_name not in function_map:
            raise ValueError(f"Function {function_name} not found.")
        return function_map[function_name](*args, **kwargs)
    
    def create_new_index(self):
        self.index = VectorStoreIndex([])
        self.index.set_index_id(os.path.basename(self.llama_index_gcs_path))
        self.save_index_to_gcs()
        self.retriever = self.index.as_retriever()
        return "Created new index successfully."
            
    def retrieve_context(self, messages):
        retriever = self.retriever
        retrieved_nodes: list[NodeWithScore] = retriever.retrieve(messages[-1]['message'])
        return ' '.join([node.text.replace('\n', ' ') for node in retrieved_nodes])
    
    def save_index_to_gcs(self):
        self.index.storage_context.persist(self.bucket_name + '/' + self.llama_index_gcs_path, fs=self.gcs)
        self.index = self.retrieve_index_from_gcs()
        return "Saved index successfully."

    def check_folder_exists(self, folder_prefix):
        blobs = self.bucket.list_blobs(prefix=folder_prefix)
        for blob in blobs:
            return True  # Folder exists as there are objects with the specified prefix
        return False  # Folder doesn't exist or is empty
    
    def retrieve_index_from_gcs(self):
        sc = StorageContext.from_defaults(persist_dir=self.bucket_name+'/'+self.llama_index_gcs_path, fs=self.gcs)
        return load_index_from_storage(sc, os.path.basename(self.llama_index_gcs_path))

    def save_index_to_gcs_from_local(self, index, bucket_name, llama_index_gcs_path):
        index.storage_context.persist(bucket_name + '/' + llama_index_gcs_path, fs=self.gcs)