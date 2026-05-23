# File: scripts/init_db.py
"""
Initialize database with ORM.
"""

import sys
from pathlib import Path

_api_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_api_root))


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_api_root / ".env")
    except ImportError:
        pass


_load_dotenv()

from bootstrap import setup_paths

setup_paths()

from app.db.session import init_db, engine
from sqlalchemy import text

def setup_pgvector():
    """Enable pgvector extension."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("✅ pgvector extension enabled")

def create_indexes():
    """Create vector similarity index."""
    with engine.connect() as conn:
        # Create IVFFlat index for faster similarity search
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_code_chunks_embedding 
            ON code_chunks USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        conn.commit()
    print("✅ Vector index created")

def main():
    print("=" * 80)
    print("INITIALIZING DATABASE")
    print("=" * 80)
    
    # Enable pgvector
    setup_pgvector()
    
    # Create tables
    init_db()
    
    # Create indexes
    create_indexes()
    
    print("\n" + "=" * 80)
    print("✅ DATABASE INITIALIZATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()