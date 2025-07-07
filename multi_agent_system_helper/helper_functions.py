import os
import requests
import subprocess

ROOT_REPOSITORY_DIRECTORY = "/home/dennisschiese/Projekte/Master/2. Semester/Automated Software Engineering/Projekt/repositories"
LITE_ENDPOINT = "http://localhost:8081/task/index/"

def fetch_problem_statement(index:int):
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
    raise Exception(f"Failed to fetch repository with index {index}. Status code: {response.status_code}")

def clone_repository(clone:str):
    """
    Clones a repository using the provided git clone command.
    Args:
        git_clone_command (str): The git clone command to execute.
    Returns:
        None
    Raises:
        Exception: If the git clone command fails.
    """
    try:
        os.chdir(os.path.join(os.getcwd(), "repositories"))  #  Move to the repositories directory
        subprocess.run(clone, shell=True, check=True)
    except:
        raise Exception(f"Failed to clone repository with command: {clone}")
    
def resolve_file_path(file:str):
    """
    Resolves the relative path of a file
    Args:
        file (str): The file path to resolve.
    Returns:
        str: The relative path of the file.
    """
    # Current dir and the requested file
    print(f"Current dir: {os.getcwd()} and requested file: {file}")
    path = subprocess.run(f"find . -path '*/{file}'", shell=True, check=True, capture_output=True, text=True).stdout.strip()
    if not path:
        dir_path = os.path.dirname(file)
        alternatives_list = subprocess.run(f"ls {dir_path}", shell=True, check=True, capture_output=True, text=True).stdout.strip().split('\n')
        alternatives = "\n".join([os.path.join(dir_path, alt) for alt in alternatives_list if alt])
        return "Didn't found the file, do you mean of of these?\n" + alternatives;
    return path

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
    
def create_team_prompt(repository_data:dict, path_to_repo:str):
    with open("../prompts/taskTemplate", "r") as file: # TODO: Rename file
        task_template = file.read()
    repository_data["path_to_repository"] = path_to_repo
    return task_template.format(**repository_data)

def send_test(request_data:dict):
    try:
        response = requests.post(
            url="http://localhost:8082/test",
            json=request_data
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to test changes. Status code: {response.status_code}")
    except requests.RequestException as e:
        raise Exception(f"An error occurred while testing changes: {e}")
    
def fix_clone_command(git_clone_command:str, index:int):
    """
    Fixes the git clone command by appending the index to the command.
    Args:
        git_clone_command (str): The original git clone command.
        index (int): The index to append to the command.
    Returns:
        str: The modified git clone command with the index appended.
    """
    parts = git_clone_command.split("&&") 
    clone = parts[0] + f" {index}"
    cd = f"cd {index}"
    commit = parts[2]
    
    return clone + " && " + cd + " && " + commit