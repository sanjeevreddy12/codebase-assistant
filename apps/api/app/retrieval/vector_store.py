from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List,Dict,Optional
from app.db.session import get_db
from app.db.models import Repository, CodeChunk

class VectorStore:

    def __init__(self,db:Session=None):

        self.db = db
        self._should_Close_db=False

        if self.db is None:
            self.db = next(get_db())
            self._should_Close_db=True

    def __del__(self):
        if self._should_Close_db and self.db:
            self.db.close()

    def create_repository(
            self,
            name:str,
            url:str,
            branch:str="main"

    )->int:
        repo = self.db.query(Repository).filter(
            Repository.url == url

        ).first()
        if repo:
            repo.branch = branch
            repo.status = 'processing'
        else:
            repo = Repository(
                name = name,
                url = url,
                branch = branch,
                status = 'processing'
            )
            self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)
        return repo.id
    def upsert_chunks(
            self,
            repository_id:int,
            chunks: List[Dict],
            embeddings = List[List[float]]
    )->int:
        if len(chunks)!=len(embeddings):
            raise ValueError(
                f"Chunks({len(chunks)}) and embeddings({len(embeddings)}) must be same"


            )
        self.db.query(CodeChunk).filter(
            CodeChunk.repository_id ==repository_id
        ).delete()

        chunk_objects = []
        for chunk , embedding in zip(chunks,embeddings):
            chunk_obj = CodeChunk(
                repository_id = repository_id,
                file_path = chunk['file_path'],
                language = chunk['language'],
                chunk_type = chunk['type'],
                name = chunk['name'],
                docstring = chunk.get('docstring'),
                code = chunk['code'],
                start_line = chunk['start_line'],
                end_line = chunk['end_line'],
                embedding = embedding
            )
            chunk_objects.append(chunk_obj)

        self.db.bulk_save_objects(chunk_objects)
        self.db.commit()
        return len(chunk_objects)
    
    def search(
            self,
            query_embedding:List[float],
            repository_id:int = None,
            language: str = None,
            limit:int=5
    )->List[Dict]:
        query = self.db.query(
            CodeChunk,
            text("1 - (embedding <=> :query_emb) as similarity")
        )
        if repository_id:
            query = query.filter(CodeChunk.repository_id ==repository_id)

        if language:
            query.filter(CodeChunk.language == language)
        query = query.order_by(
            text("embedding <=> :query_emb")

        ).limit(limit)

        results = query.params(query_emb = str(query_embedding)).all()

        output = []
        for chunk, similarity in results:
            chunk_dict = chunk.to_dict()
            chunk_dict['similarity'] = float(similarity)
            output.append(chunk_dict)
        
        return output
    def mark_repository_complete(self, repository_id: int):
       
        repo = self.db.query(Repository).filter(
            Repository.id == repository_id
        ).first()
        
        if repo:
            repo.status = 'completed'
            from datetime import datetime
            repo.last_ingested_at = datetime.utcnow()
            self.db.commit()

    def mark_repository_failed(self, repository_id: int) -> None:
        repo = self.db.query(Repository).filter(
            Repository.id == repository_id
        ).first()

        if repo:
            repo.status = 'failed'
            self.db.commit()
    
    def get_repository(self, repository_id: int) -> Optional[Dict]:
       
        repo = self.db.query(Repository).filter(
            Repository.id == repository_id
        ).first()
        
        if repo:
            return {
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'branch': repo.branch,
                'status': repo.status,
                'last_ingested_at': repo.last_ingested_at,
                'created_at': repo.created_at
            }
        return None
    
    def list_repositories(self) -> List[Dict]:
        """List all repositories with chunk counts."""
        from sqlalchemy import func
        
        results = self.db.query(
            Repository,
            func.count(CodeChunk.id).label('chunk_count')
        ).outerjoin(CodeChunk).group_by(Repository.id).order_by(
            Repository.created_at.desc()
        ).all()
        
        
        output = []
        for repo, chunk_count in results:
            output.append({
                'id': repo.id,
                'name': repo.name,
                'url': repo.url,
                'branch': repo.branch,
                'status': repo.status,
                'last_ingested_at': repo.last_ingested_at,
                'created_at': repo.created_at,
                'chunk_count': chunk_count
            })
        
        return output
    
    def delete_repository(self, repository_id: int) -> bool:
       
        repo = self.db.query(Repository).filter(
            Repository.id == repository_id
        ).first()
        
        if repo:
            self.db.delete(repo)
            self.db.commit()
            return True
        
        return False
    
