from pathlib import Path
from typing import List, Dict, Optional, Set
from packages.parser_engine.parsers.tree_sitter_parser import TreeSitterParser
from  packages.parser_engine.parsers.language_detecter import LanguageDetector
import os 
class RepositoryParser:

    IGNORE_DIRECTORIES = {
        # Version control
        '.git', '.svn', '.hg', '.bzr',
        
        # Python
        '__pycache__', '.pytest_cache', '.mypy_cache', '.tox',
        'venv', 'env', '.venv', '.env', 'virtualenv',
        '*.egg-info', 'dist', 'build', '.eggs',
        
        # JavaScript/Node
        'node_modules', '.npm', '.yarn', 'bower_components',
        '.next', '.nuxt', 'out', '.cache',
        
        # Build outputs
        'target',  # Rust, Java
        'bin', 'obj',  # C#
        'vendor',  # Go, PHP
        'build', 'dist', '.build',
        
        # IDE
        '.idea', '.vscode', '.vs', '.eclipse',
        '.settings', '*.xcodeproj', '*.xcworkspace',
        
        # OS
        '.DS_Store', 'Thumbs.db',
        
        # Coverage/test outputs
        'coverage', '.coverage', 'htmlcov', '.nyc_output',
        
        # Logs
        'logs', '*.log',
    }
    IGNORE_FILES = {
        # Compiled
        '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe', '.bin',
        
        # Archives
        '.zip', '.tar', '.gz', '.rar', '.7z',
        
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.bmp', '.tiff', '.webp',
        
        # Documents
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        
        # Config/Lock files
        'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock',
        'Gemfile.lock', 'Cargo.lock', 'composer.lock',
        
        # Environment
        '.env', '.env.local', '.env.production',
        
        # Misc
        '.gitignore', '.dockerignore', '.editorconfig',
        'LICENSE', 'README.md', 'CHANGELOG.md',
    }

    def __init__(self,repo_path:str,max_file_Size_mb:int =10):
        
        self.repo_path = Path(repo_path).resolve()
        self.max_file_size_bytes = max_file_Size_mb*1024*1024

        if not self.repo_path.exists():
            raise ValueError(f"Repository not found : {repo_path}")
        if not self.repo_path.is_dir():
            raise ValueError(f"path is not a directory : {repo_path}")
        

    def parse_repository(self, verbose:bool = True)->List[Dict]:
        """
        Parse entire repository and extract all chunks"""

        if verbose:
            print(f"starting repository parse : {self.repo_path}")
        
        code_files = self._find_code_files()

        if verbose:
            print(f"Found {len(code_files)} code files to parse")

        if not code_files:
            print("No code files in repo")
            return []
        
        all_chunks=[]
        parsed_count=0
        failed_count=0

        for i, file_path in enumerate(code_files,1):
            if verbose and i%10 ==0:
                print(f"progress : {i/len(code_files)} files parsed")

            chunks = self._parse_single_file(file_path)


            if chunks:
                all_chunks.extend(chunks)
                parsed_count+=1
            else:
                failed_count+=1
        if verbose:
            print(f"\nParsing complete!")
            print(f"Successfully parsed: {parsed_count} files")
            print(f"Failed to parse: {failed_count} files")
            print(f"Total chunks extracted: {len(all_chunks)}")
        
        return all_chunks
    
    def _find_code_files(self)->List[Path]:

        """
        Recursively find ALL code files in repository.
        
        This method:
        1. Uses os.walk() to traverse ALL directories recursively
        2. Filters out ignored directories
        3. Filters out ignored files
        4. Checks file size limits
        5. Verifies file is parseable
        
        Returns:
            List of Path objects for all parseable code files
        """

        code_files = []

        for root,dirs,files in os.walk(self.repo_path):
            root_path = Path(root)

            original_dirs = dirs.copy()
            dirs[:]= [
                d for d in original_dirs
                if not self._should_ignore_directory(d)
            ]

            for file_name in files:
                file_path = root_path/file_name

                if self._should_ignore_file(file_name):
                    continue

                if not LanguageDetector.is_supported(str(file_path)):
                    continue

                if not self._check_file_size(file_path):
                    continue

                code_files.append(file_path)
        return code_files
    def _should_ignore_directory(self,dir_name:str)->bool:
        
        if dir_name in self.IGNORE_DIRECTORIES:
            return True
        
        if dir_name.startswith('.'):
            return True
        
        for pattern in self.IGNORE_DIRECTORIES:
            if '*' in pattern:
                pattern_base = pattern.replace('*','')
                if pattern_base in dir_name:
                    return True
        return False
    def _should_ignore_file(self,file_name:str)->bool:

        if file_name in self.IGNORE_FILES:
            return True
        
        file_path = Path(file_name)
        if file_path.suffix.lower() in self.IGNORE_FILES:
            return True
        
        if file_name.startswith('.'):
            return True
        
        return False
    
    def _check_file_size(self, file_path:Path)->bool:

        try:
            file_size = file_path.stat().st_size
            if file_size> self.max_file_size_bytes:
                print(f"skiping large file ({file_size/1024/1024:.1f} mb):{file_path}")

                return False
            return True
        except Exception as e:
            print(f"exception :{e}")
            return False
    
    def _parse_single_file(self, file_path: Path)->List[Dict]:

        try :
            parser = TreeSitterParser.from_file_path(str(file_path))

            if not parser:
                return []
            
            tree = parser.parse_file(str(file_path))

            if not tree:
                return []
            
            functions = parser.extract_functions(tree)
            classes = parser.extract_classes(tree)

            all_chunks = functions+classes

            relative_path = file_path.relative_to(self.repo_path)

            for chunk in all_chunks:
                chunk['file_path'] = str(relative_path)
                chunk['absolute_path'] = str(file_path)

            return all_chunks
        except Exception as e:
            print(f"Error parsing {file_path:} {e}")
            return []
    
    def get_Repository_stats(self)->Dict:

        code_files = self._find_code_files()

        language_counts = {}
        
        for file_path in code_files:
            language = LanguageDetector.detect_language(str(file_path))
            if language:
                language_counts[language]=language_counts.get(language,0)+1
        total_lines = 0
        for file_path in code_files:
            try:
                with open(file_path,'r',encoding='utf-8',errors='ignore') as f:
                    total_lines+=sum(1 for _ in f)
            except:
                pass


        total_size_bytes = sum(
            file_path.stat().st_size 
            for file_path in code_files
        )
        
        return {
            'repo_path': str(self.repo_path),
            'total_files': len(code_files),
            'total_lines': total_lines,
            'total_size_mb': total_size_bytes / 1024 / 1024,
            'languages': language_counts,
        }
    def get_directory_structure(self, max_depth: int = 3) -> Dict:
        """
        Get directory structure visualization.
        
        Args:
            max_depth: Maximum depth to show
            
        Returns:
            Dictionary representing directory tree
        """
        def build_tree(path: Path, current_depth: int) -> Dict:
            if current_depth > max_depth:
                return {'...': 'max depth reached'}
            
            tree = {}
            
            try:
                for item in sorted(path.iterdir()):
                    if item.is_dir():
                        if not self._should_ignore_directory(item.name):
                            tree[f"{item.name}/"] = build_tree(item, current_depth + 1)
                    else:
                        if LanguageDetector.is_supported(str(item)):
                            tree[item.name] = 'file'
            except PermissionError:
                tree['<permission denied>'] = None
            
            return tree
        
        return build_tree(self.repo_path, 0)




            


