import fiass

import numpy as np

import pickle

import os

class VectorStore:

    def __init__(self, dimension:int = 384):
        self.dimension = dimension
        self.index = fiass.IndexFlatL2(dimension)

        self.metadata =[]

    def add_embeddings(self,embeddings,metadata):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self,query_embedding,top_k=5):

        query_embedding = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )
        results = []

        for idx in indices[0]:
            if idx == -1:
                continue

            results.append(
                self.metadata[idx]
            )
        return results
    
    def save(self, index_path:str,metadata_path:str):

        fiass.write_index(self.index,index_path)

        with open(metadata_path,"wb") as f:
            pickle.dump(self.metadata,f)

    @classmethod
    def load(cls,index_path:str,metadata_path:str):
        index = fiass.read_index(index_path)

        with open(metadata_path,"rb") as f:
            metadata = pickle.load(f)
        
        obj = cls(index.d)
        obj.index=index
        obj.metadata = metadata
        return obj
    
    
        

