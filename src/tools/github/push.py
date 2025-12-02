import os
import shutil
import subprocess
from agents import function_tool
from tools.shared import log

@function_tool
def push_to_public_repo(local_file_path: str) -> str:
    USER = os.getenv("GITHUB_USER")
    TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPO")
    EMAIL = os.getenv("GITHUB_EMAIL")
    
    if not all([USER, TOKEN, REPO_NAME, EMAIL]):
        return "Error: Missing GitHub configuration environment variables (GITHUB_USER, GITHUB_TOKEN, GITHUB_REPO, GITHUB_EMAIL)."

    repo_url = f"https://{TOKEN}@github.com/{USER}/{REPO_NAME}.git"
    
    repo_dir = os.path.abspath("temp_data_repo")
    
    final_filename = os.path.basename(local_file_path)

    log(f"🚀 Puching dataset to public repo {local_file_path}...")

    try:
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True, capture_output=True)

        subprocess.run(["git", "config", "user.email", EMAIL], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", USER], cwd=repo_dir, check=True, capture_output=True)

        for item in os.listdir(repo_dir):
            if item == ".git":
                continue
            item_path = os.path.join(repo_dir, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        abs_local_path = os.path.abspath(local_file_path)
        if not os.path.exists(abs_local_path):
            return f"Error: Local file {local_file_path} does not exist."

        destination_path = os.path.join(repo_dir, final_filename)
        
        shutil.copy(abs_local_path, destination_path)
        
        status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
        
        if status.stdout.strip():
            subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Automatic dataset update"], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "push"], cwd=repo_dir, check=True, capture_output=True)
            result_msg = "✅ Success! Dataset pushed to public repo."
        else:
            result_msg = "⚠️ No changes detected in data. Push skipped."

        log(result_msg)
        return result_msg

    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Git Error: {e}"
        log(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Unexpected Error: {str(e)}"
        log(error_msg)
        return error_msg
    finally:
        if os.path.exists(repo_dir):
            def handle_remove_readonly(func, path, exc):
                import stat
                os.chmod(path, stat.S_IWRITE)
                func(path)
                
            try:
                shutil.rmtree(repo_dir, onexc=handle_remove_readonly)
            except Exception as e:
                log(f"⚠️ Warning: Could not remove temp dir: {e}")