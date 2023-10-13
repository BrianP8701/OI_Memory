from llama_index_manager import LLAMA_Index_Manager
from llama_index import SimpleDirectoryReader

manager = LLAMA_Index_Manager('vigilant-yeti-400300', 'oi-hackathon', 'blah/blah/eriks_vector_index')

# Retrieve vector store (If you put a path that doesen't exist, it will return a new empty index)
index = manager.retrieve_index_from_gcs()

# Add docs from local directory
documents = SimpleDirectoryReader('./test_library', recursive=True).load_data()
for doc in documents:
    index.insert(doc)
    
# Save index persistently back to gcs
manager.save_index_to_gcs_from_local(index, 'oi-hackathon', 'blah/blah/eriks_vector_index')

print(manager.retrieve_context([{ 'message': 'What is the use of Gaussian Micture Models here?' }]))
# Now you can retrieve the index from the gcs path again whenever you want and continue adding docs to it and retrieving context from it.