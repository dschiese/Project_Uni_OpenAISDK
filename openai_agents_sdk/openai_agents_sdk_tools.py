from agents import Agent, FunctionTool, RunContextWrapper, function_tool
import requests
import os
import subprocess

LITE_ENDPOINT = "http://localhost:8081/task/index/"

def fetch_problem_statement(index: int) -> dict:
    """
    Fetches the problem statement from the Lite server for a given index.
    Args:
        index (int): The index of the problem statement to fetch.
    Returns:
        dict: The problem statement as a JSON object.
    Raises:
        Exception: If the request fails or the status code is not in the 200-299 range.
    """
    response = requests.get(LITE_ENDPOINT + str(index))
    if 200 <= response.status_code < 300:
        return response.json()
    else:
        raise Exception(f"Failed to fetch problem statement")

def create_team_prompt(repository_data:dict, path_to_repo:str):
    print("CURRENT DICT: ", os.getcwd())
    try:
        with open("../prompts/solotasktemplate", "r") as file:
            task_template = file.read()
        repository_data["root_path"] = os.getcwd()
        repository_data["path_to_repository"] = path_to_repo
        return task_template.format(**repository_data)
    except FileNotFoundError:
        # List directory contents for debugging
        print("File not found: ../../prompts/solotasktemplate")
        print("Current directory contents:", os.listdir(os.getcwd()))

def resolve_file_path(path):
    """
    Resolves a file path by checking if it exists. If not, try to detect if it's missing
    a directory level and fix it.
    
    Args:
        path (str): The original file path
        
    Returns:
        str: The resolved file path
    """
    if os.path.exists(path):
        return path
        
    # Check if path is missing a directory level
    parts = path.split('/')
    repo_name = None
    
    # Find the repository name (which might be repeated in the path)
    for i, part in enumerate(parts):
        if part == "AutoGen" and i+1 < len(parts):
            repo_name = parts[i+1]
            break
            
    if repo_name:
        # Check if inserting the repo name again fixes the path
        new_parts = parts.copy()
        insert_index = parts.index(repo_name) + 1
        new_parts.insert(insert_index, repo_name)
        new_path = '/'.join(new_parts)
        
        if os.path.exists(new_path):
            return new_path
            
    # If we couldn't fix it automatically, return the original path
    return path



    


def clone_repository(git_clone_command:str):
    """
    Clones a repository using the provided git clone command.
    Args:
        git_clone_command (str): The git clone command to execute.
    Returns:
        None
    Raises:
        Exception: If the git clone command fails.
    """
    print(f"Cloning repository with command: {git_clone_command}")
    try:
        os.chdir(os.path.join(os.getcwd(), "repositories"))  # Ensure we are in the correct directory
        clone, dir, commit = separate_git_clone_command(git_clone_command)
        subprocess.run(clone, shell=True, check=True)
        subprocess.run(commit, cwd=dir, shell=True, check=True)
        current_dir = subprocess.run("pwd", shell=True, check=True, capture_output=True, text=True).stdout.strip()
        return dir  # Returns the correct path when clone has worked, otherwise the command failed and the dir is not changed.
    except:
        pass
        # raise Exception(f"Failed to clone repository with command")

def separate_git_clone_command(git_clone_command:str):
    """
    Separates the git clone command into its components: clone command, directory, and commit.
    """
    parts = git_clone_command.split("&&")
    if len(parts) < 3:
        raise ValueError("Git clone command must contain at least three parts: clone command, directory, and commit.")
    
    clone_command = " ".join(parts[:-2])  # Everything except the last two parts
    directory = parts[-2].replace("cd", "").strip();  # Second to last part
    commit = parts[-1]  # Last part
    
    return clone_command, directory, commit

def set_working_directory(directory_path:str):
    """
    Changes the current working directory to the specified path.
    Args:
        directory_path (str): The directory path to change to.
    Returns:
        str: The new working directory path.
    """
    try:
        os.chdir(directory_path)
        return f"Working directory changed to: {os.getcwd()}"
    except FileNotFoundError:
        raise Exception(f"Directory not found: {directory_path}")
    except Exception as e:
        raise Exception(f"An error occurred while changing the working directory: {e}")
