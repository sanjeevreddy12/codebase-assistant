

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

class SentenceTransformerEmbedder:
    
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimensions = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded! Embedding dimension: {self.dimensions}")
    
    def embed_single(self, text: str) -> List[float]:
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(
        self, 
        texts: List[str],
        batch_size: int = 32,
        verbose: bool = True
    ) -> List[List[float]]:
       
        if verbose:
            print(f"Embedding {len(texts)} texts...")
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=verbose,
            convert_to_numpy=True
        )
        
     
        return embeddings.tolist()
    
    def prepare_chunk_text(self, chunk: Dict) -> str:
        """
        Prepare chunk for embedding.
        
        Combines docstring and code for better retrieval.
        
        Args:
            chunk: Chunk dictionary from parser
            
        Returns:
            Text string to embed
        """
        parts = []
        
        # Include function/class name (important for matching)
        parts.append(f"{chunk['type']}: {chunk['name']}")
        
        # Include file path for context
        parts.append(f"File: {chunk['file_path']}")
        
        # Include docstring if exists (high signal)
        if chunk.get('docstring'):
            parts.append(chunk['docstring'])
        
        
        code = chunk['code']
        if len(code) > 1000: 
            code = code[:1000] + "..."
        parts.append(code)
        
        return "\n".join(parts)