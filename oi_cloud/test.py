from llama_index import VectorStoreIndex
from llama_index import SimpleDirectoryReader
import time

start_time = time.time()
index=VectorStoreIndex([])

documents = SimpleDirectoryReader('library', recursive=True).load_data()
for doc in documents:
    index.insert(doc)
retriever = index.as_retriever()
print("--- %s seconds ---" % (time.time() - start_time))
print(dir(index))
# Assuming you have a VectorStoreIndex object named index
serialized_index = VectorStoreIndex.from_vector_store(index)

# Persist the index
serialized_index.persist('path/to/save/index')



# from llama_index import VectorStoreIndex

# index = VectorStoreIndex([])
# serialized_index = VectorStoreIndex.from_vector_store(index)
# index.persist('temp_serialized_index')

# index = VectorStoreIndex.from_persist_path('temp_serialized_index')