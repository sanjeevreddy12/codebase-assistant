"""
Detecg Programming language from file extension.
Maps file extensions to tree-sitter language names
"""

from pathlib import Path
from typing import Optional

class LanguageDetector:
    """Detect programming language from file path"""

    EXTENSION_TO_LANGUAGE = {

        # Python
        '.py': 'python',
        '.pyw': 'python',
        '.pyi': 'python',  
        
        # JavaScript/TypeScript
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.mjs': 'javascript',
        '.cjs': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',

    }

    @classmethod
    def detect_language(cls, file_path : str)->Optional[str]:
        """
        Detects language from file extension 
        Args: file path
        returns : language name
        """
        ext = Path(file_path).suffix.lower()
        return cls.EXTENSION_TO_LANGUAGE.get(ext)
    
    @classmethod
    def is_supported(cls,file_path :str)->bool :
        """check file is supported"""
        return cls.detect_language(file_path) is not None
    

    @classmethod
    def get_supported_extensions(cls)->set:
        """get all supported extensions"""
        return set(cls.EXTENSION_TO_LANGUAGE.keys())
    
    