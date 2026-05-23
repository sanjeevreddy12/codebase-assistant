

import sys
from pathlib import Path

# Minimal path so bootstrap can be imported when this module is loaded directly.
_api_root = Path(__file__).resolve().parents[2]
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from bootstrap import setup_paths

setup_paths()

import tempfile
import shutil
from typing import Dict

from app.retrieval.vector_store import VectorStore
from packages.ingestion.embedder import SentenceTransformerEmbedder
from packages.parser_engine.parsers.repository_parser import RepositoryParser
from packages.utils.git_utils import clone_repository

class IngestionService:
   
    
    def __init__(self):
        
        print("Initializing ingestion service...")
        self.embedder = SentenceTransformerEmbedder()
      
        print("Ingestion service ready!")
    
    def ingest_repository(
        self, 
        repo_url: str,
        branch: str = "main"
    ) -> Dict:
        
        temp_dir = None
        repo_id = None
        vector_store = None

        try:
            repo_name = Path(repo_url).name.replace('.git', '')
            
            print(f"\n{'='*80}")
            print(f"INGESTING REPOSITORY: {repo_name}")
            print(f"{'='*80}\n")
            
           
            print("STEP 1: Cloning repository...")
            temp_dir = tempfile.mkdtemp(prefix="codebase_assistant_")
            clone_repository(repo_url, temp_dir, branch)
            print(f" Cloned to: {temp_dir}\n")
            
          
            print("STEP 2: Creating repository record...")
            vector_store = VectorStore()
            repo_id = vector_store.create_repository(
                name=repo_name,
                url=repo_url,
                branch=branch
            )
            print(f" Repository ID: {repo_id}\n")
            
            
            print("STEP 3: Parsing repository...")
            parser = RepositoryParser(temp_dir)
            stats = parser.get_repository_stats()
            print(f"Repository stats:")
            print(f"  Files: {stats['total_files']}")
            print(f"  Lines: {stats['total_lines']:,}")
            print(f"  Languages: {stats['languages']}")
            
            chunks = parser.parse_repository(verbose=True)
            
            if not chunks:
                print(" No parseable code found")
                return {
                    'status': 'error',
                    'error': 'No parseable code found'
                }
            
            print(f" Extracted {len(chunks)} chunks\n")
            
           
            print("STEP 4: Generating embeddings...")
            texts = [
                self.embedder.prepare_chunk_text(chunk) 
                for chunk in chunks
            ]
            embeddings = self.embedder.embed_batch(texts, verbose=True)
            print(f" Generated {len(embeddings)} embeddings\n")
            
            print("STEP 5: Storing in database...")
            count = vector_store.upsert_chunks(repo_id, chunks, embeddings)
            print(f" Stored {count} chunks\n")
            
           
            print("STEP 6: Finalizing...")
            vector_store.mark_repository_complete(repo_id)
            print(f" Repository ingestion complete!\n")
            
            result = {
                'status': 'success',
                'repository_id': repo_id,
                'repository_name': repo_name,
                'total_chunks': len(chunks),
                'total_files': stats['total_files'],
                'total_lines': stats['total_lines'],
                'languages': stats['languages']
            }
            
            print(f"{'='*80}")
            print(f"INGESTION SUMMARY")
            print(f"{'='*80}")
            print(f"Repository: {repo_name}")
            print(f"Repository ID: {repo_id}")
            print(f"Total chunks: {len(chunks)}")
            print(f"{'='*80}\n")
            
            return result
            
        except Exception as e:
            print(f"\n ERROR: {e}")
            import traceback
            traceback.print_exc()

            if repo_id is not None:
                store = vector_store or VectorStore()
                store.mark_repository_failed(repo_id)

            return {
                'status': 'error',
                'error': str(e)
            }
            
        finally:
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir)