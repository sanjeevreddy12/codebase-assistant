"""
Language specific code parser using tree sitter
"""

from tree_sitter_languages import get_parser
from typing import List, Dict, Optional 
from pathlib import Path

from  packages.parser_engine.parsers.language_detecter import LanguageDetector

class TreeSitterParser:
    """
    Multi language code parser using tree sitter
    """
    FUNCTION_NODE_TYPES = {
        'python' : ['function_definition'],
        'javascript' : ['function_declaration','arrow_function','function'],
        'typescript' : ['function_declaration','arrow_function','function']


    }

    CLASS_NODE_TYPES = {
        'python': ['class_definition'],
        'javascript' : ['class_declaration'],
        'typescript' : ['class_declaration']
    }

    def __init__(self , language : str):
        """
        Initialize parsers for different language
        Args : name - python, javascript,...
    
        """
        self.language = language
        print("LANGUAGE:", language)
        try:
            self.parser = get_parser(language)
        except Exception as e:
            raise ValueError(f"Failed to load parser for {language}")
        
        print("LANGUAGE:", language)
        print("PARSER:", self.parser)
        print("TYPE:", type(self.parser))
        
    @classmethod
    def from_file_path(cls, file_path:str)->Optional['TreeSitterParser']:
        """
        create parser by detecting language from file extension.

        Args : file_path

        returns TreeSitterParser instance or None if not supported

        """
        language = LanguageDetector.detect_language(file_path)
        if not language:
            return None
        try:
            return cls(language)
        except ValueError:
            return None
        
    def parse_file(self, file_path:str)->Optional['object']:
        """
        Parse a file and return the AST
        Args : filepath
        returns :Treesitter tree object or none if fails
        """

        try:
            with open(file_path,'rb') as f:
                code_bytes = f.read()
            return self.parser.parse(code_bytes)
        except Exception as e:
            print(f"Error parsing {file_path}:{e}")
        print("ROOT TYPE:", self.parser.parse(code_bytes).root_node.type)

    
    def parse_code(self, code:str)->Optional['object']:
        """Parse code string directly"""
        try:
            return self.parser.parse(bytes(code,'utf8'))
        except Exception as e:
            print(f"Error parsing code : {e}")
            return None

    def extract_functions(self,tree)->List['Dict']:
        """
        Extract all functions from tree
        Args : treesitter object
        Returns : List of function metadata dictionaries"""

        if not tree:
            print("no tree object")
            return[]
        
        root_node = tree.root_node
        function_types = self.FUNCTION_NODE_TYPES.get(self.language,[])

        if not function_types:
            print("function type or language not  exists")
            return []
        functions =[]

        for func_type in function_types:
            functions.extend(
                self._extract_nodes_by_type(root_node,func_type,'function')

            )
        return functions
    
    def extract_classes(self,tree)->List['Dict']:
        """
        Extract all classes"""

        if not tree:
            return []

        root_node = tree.root_node
        class_types = self.CLASS_NODE_TYPES.get(self.language,[])
        if not class_types:
            return []

        classes = []
        for class_type in class_types:
            classes.extend(
                self._extract_nodes_by_type(root_node,class_type,'class')
            )   

        return classes

    def _extract_nodes_by_type(
            self,
            node,
            node_type:str,
            category:str
    )->List["Dict"]:
        """
        Recursively find all nodes with specfic types like classes , functions etc
        """    
        results = []

        if node.type == node_type:
            metadata = self._extract_node_metadata(node,category)
            if metadata:
                results.append(metadata)
        for child in node.children:
            results.extend(
                self._extract_nodes_by_type(child,node_type,category)

            )
        return results
    
    def _extract_node_metadata(self,node,category:str)->Optional['Dict']:

        name_node = node.child_by_field_name('name')
        if not name_node:
            name = f"anonymous_{category}_{node.start_point[0]}"
        else:
            name = name_node.text.decode('utf8')

        
        docstring = self._extract_docstring(node)
        code = node.text.decode('utf8')
        start_line = node.start_point[0]+1
        end_line = node.end_point[0]+1

        return {
            'name':name,
            'docstring':docstring,
            'code':code,
            'start_line':start_line,
            'end_line':end_line,
            'type':category,
            'language':self.language

        }
    
    def _extract_docstring(self,node)->Optional['str']:
        if self.language == 'python':
            return self._extract_python_docstring(node)
        elif self.language in ['javascript', 'typescript']:
            return self._Extract_jsdoc(node)

    def _extract_python_docstring(self,node)->Optional['str']:
        body = node.child_by_field_name('body')
        if not body or len(body.children)==0:
            return None
        
        first_stmt = body.children[0]
        if first_stmt.type == 'expression_statement' and len(first_stmt.children) > 0:
            potential_string = first_stmt.children[0]
            if potential_string.type == 'string':
                text = potential_string.text.decode('utf8')
                text = text.strip('"""').strip("'''").strip('"').strip("'").strip()
                return text
        
        return None
    
    def _extract_jsdoc(self, node) -> Optional[str]:
        """Extract JSDoc comment (before function)."""
        prev_sibling = node.prev_sibling
        
        
        while prev_sibling and prev_sibling.type in ['\n', ' ', 'comment']:
            if prev_sibling.type == 'comment':
                comment_text = prev_sibling.text.decode('utf8')
                
                if comment_text.strip().startswith('/**'):
                    
                    comment_text = comment_text.replace('/**', '').replace('*/', '')
                    lines = comment_text.split('\n')
                    cleaned_lines = [
                        line.strip().lstrip('*').strip() 
                        for line in lines
                    ]
                    return '\n'.join(cleaned_lines).strip()
            prev_sibling = prev_sibling.prev_sibling
        
        return None
    #testing AST looks like 

    def print_ast(self, tree):
        def walk(node, indent=0):
            code_snippet = node.text.decode("utf8")[:40].replace("\n", " ")
            print("  " * indent + f"{node.type} -> {code_snippet}")

            for child in node.children:
                walk(child, indent + 1)

        walk(tree.root_node)
