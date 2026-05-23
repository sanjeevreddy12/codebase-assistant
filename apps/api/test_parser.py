import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bootstrap import setup_paths

setup_paths()

from packages.parser_engine.parsers.tree_sitter_parser import TreeSitterParser
from packages.parser_engine.parsers.repository_parser import RepositoryParser


# =========================
# CONFIG
# =========================
FILE_PATH = r"C:\Users\sanju reddy\python\auth-rbac\app\auth.py"
REPO_PATH = r"C:\Users\sanju reddy\python\auth-rbac"


# =========================
# AST PRINTER
# =========================
def print_ast(tree):
    def walk(node, prefix="", is_last=True):

        connector = "└── " if is_last else "├── "

        snippet = node.text.decode("utf8", errors="ignore")
        snippet = snippet.replace("\n", " ")[:50]

        print(prefix + connector + f"{node.type}  →  {snippet}")

        children = node.children
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            walk(child, new_prefix, is_last_child)

    print("\n" + "=" * 80)
    print("TREE-SITTER AST (VISUAL)")
    print("=" * 80)

    walk(tree.root_node)


# =========================
# 1. AST FOR SINGLE FILE
# =========================
print("\n\n🚀 STEP 1: AST FOR SINGLE FILE")


parser = TreeSitterParser.from_file_path(FILE_PATH)

if parser:
    tree = parser.parse_file(FILE_PATH)

    if tree:
        print_ast(tree)
    else:
        print("❌ Failed to parse file")
else:
    print("❌ Unsupported file type")


# =========================
# 2. FULL REPO CHUNKS
# =========================
print("\n\n🚀 STEP 2: REPOSITORY CHUNKS")

repo_parser = RepositoryParser(REPO_PATH)
print(RepositoryParser.get_directory_structure(repo_parser))

chunks = repo_parser.parse_repository(verbose=False)

print("\n" + "=" * 80)
print(f"TOTAL CHUNKS: {len(chunks)}")
print("=" * 80)


# =========================
# PRINT SAMPLE CHUNKS
# =========================
print("\n\nSAMPLE CHUNKS (first 10)\n")

for i, chunk in enumerate(chunks[:10]):
    print("\n" + "-" * 80)
    print(f"CHUNK #{i+1}")
    print("-" * 80)

    print("NAME:", chunk.get("name"))
    print("TYPE:", chunk.get("type"))
    print("FILE:", chunk.get("file_path"))
    print("LINES:", chunk.get("start_line"), "->", chunk.get("end_line"))

    print("\nCODE:")
    print(chunk.get("code")[:400])  # limit output

    print("\nDOCSTRING:")
    print(chunk.get("docstring"))