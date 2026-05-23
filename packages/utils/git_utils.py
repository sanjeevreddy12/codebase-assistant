
import subprocess
from pathlib import Path
from typing import Optional

def clone_repository(
    repo_url: str, 
    target_dir: str,
    branch: str = "main"
) -> None:
   
    try:
        
        cmd = [
            'git', 'clone',
            '--depth', '1',
            '--branch', branch,
            repo_url,
            target_dir
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully cloned {repo_url} to {target_dir}")
        
    except subprocess.CalledProcessError as e:
       
        if branch == "main":
            print(f"Branch 'main' not found, trying 'master'...")
            clone_repository(repo_url, target_dir, branch="master")
        else:
            raise Exception(f"Failed to clone repository: {e.stderr}")

