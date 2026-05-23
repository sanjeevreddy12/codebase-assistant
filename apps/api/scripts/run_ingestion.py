"""
Ingest a Git repository into PostgreSQL + pgvector.

Run from ``apps/api``:

    python scripts/run_ingestion.py --url https://github.com/org/repo --branch main
"""

import argparse
import sys
from pathlib import Path

_api_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_api_root))

from bootstrap import setup_paths

setup_paths()


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(_api_root / ".env")
    except ImportError:
        pass


def main() -> None:
    _load_dotenv()

    parser = argparse.ArgumentParser(
        description="Clone, parse, embed, and store a repository in pgvector",
    )
    parser.add_argument("--url", required=True, help="Git repository URL")
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to clone (default: main)",
    )
    args = parser.parse_args()

    from app.services.ingestion_service import IngestionService

    service = IngestionService()
    result = service.ingest_repository(args.url, args.branch)

    if result.get("status") != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
