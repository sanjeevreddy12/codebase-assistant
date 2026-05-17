from sentence_transformer import SentenceTransformer

from typing import List

class Embedder:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )
    
    def embed_text(self,text:str)->List[float]:

        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def embed_chunks(self, chunks:List[dict])->List[List[float]]:

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.model.encode(texts)

        return [embedding.tolist() for embedding in embeddings]
    

    

