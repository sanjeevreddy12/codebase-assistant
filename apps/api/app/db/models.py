from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class Repository(Base):
    
    __tablename__='repositories'

    id = Column(Integer, primary_key=True,index= True)

    name = Column(String(255),nullable=False)
    url = Column(Text, nullable = False,unique = True)
    branch = Column(String(200),default='main')
    status = Column(String(50),default='pending')

    last_ingested_at = Column(DateTime(timezone=True),nullable = True)
    created_at = Column(DateTime(timezone=True),server_default = func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    chunks = relationship(
        "CodeChunk",
        back_populates="repository",
        cascade = "all,delete-orphan"
    )

    def __repr__(self):
        return f"<Repository(id={self.id},name '{self.name},status='{self.status})"

class CodeChunk(Base):
   
    __tablename__ = 'code_chunks'
    
    
    id = Column(Integer, primary_key=True, index=True)
    
    
    repository_id = Column(
        Integer, 
        ForeignKey('repositories.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    file_path = Column(Text, nullable=False, index=True)
    language = Column(String(50), nullable=False, index=True)
    
 
    chunk_type = Column(String(50), nullable=False, index=True)  # 'function' or 'class'
    name = Column(String(255), nullable=False, index=True)
    docstring = Column(Text, nullable=True)
    code = Column(Text, nullable=False)
    
  
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    
    
    embedding = Column(Vector(384))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
    repository = relationship("Repository", back_populates="chunks")
    
    def __repr__(self):
        return f"<CodeChunk(id={self.id}, name='{self.name}', type='{self.chunk_type}')>"
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'repository_id': self.repository_id,
            'file_path': self.file_path,
            'language': self.language,
            'type': self.chunk_type,
            'name': self.name,
            'docstring': self.docstring,
            'code': self.code,
            'start_line': self.start_line,
            'end_line': self.end_line,
        }