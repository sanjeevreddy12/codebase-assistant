from typing import List, Dict

class ChunkProcessor :

    @staticmethod
    def clean_code(code:str)->str:
        return "\n".join(
            line.rstrip()
            for line in code.splitlines()
            if line.strip()
        )
    
    @staticmethod
    def create_chunk_text(chunk:Dict)->str:

        text = f"""
        File:{chunk['file_path']}
        Language: {chunk['language']}
        Type:{chunk['type']}
        Name:{chunk['name']}
        code:{chunk['code']}
       """
        return text.strip()
    
    @classmethod
    def process_chunks(cls,chunks:List[Dict])->List[Dict]:
        processed_chunks = []

        for chunk in chunks:
            cleaned_Code = cls.clean_code(chunk["code"])

            processed_chunk = {
                "text ": cls.create_chunk_text({
                    **chunk,
                    "code": cleaned_Code
                }),
                "metadata":{
                    "file_path":chunk["file_path"],
                    "language":chunk["language"],
                    "type":chunk['type'],
                    "name":chunk["name"],
                    "start_line":chunk["start_line"],
                    "end_line":chunk["end_line"]
                }
            }

            processed_chunks.append(processed_chunk)
        return processed_chunks
    
    
