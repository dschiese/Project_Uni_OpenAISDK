from agents import function_tool, RunContextWrapper
from git import List
import requests
import os
from .helper_functions import resolve_file_path
import subprocess
from git import Repo

ollama = "http://localhost:11434/api/generate"
BASE_PATH = "/home/dennisschiese/Projekte/Master/2. Semester/Automated Software Engineering/Projekt/results"

@function_tool
def read_dir_structure():
    """
    Reads the directory structure of the current working directory and returns only .py files and their directories as a string.
    Returns:
        str: The filtered directory structure.
    """
    try:
        result = subprocess.run(
            "tree -P \"*.py\" -fi .",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"An error occurred while reading the directory structure: {e}")

@function_tool
def write_file_tool(path:str, content:str):
    """
    Writes the content (source code) to the origin file.
    Requires the complete source code of the file, not just the changes.
    """
    print(f">>>>>>>>>>>>>>> Writing_file_tool called with path: {path} and content length: {len(content)}")
    try:
        print(f"Writing to file: {path}")
        resolved_path = resolve_file_path(path)
        # Create directory if it doesn't exist
        directory = os.path.dirname(resolved_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(resolved_path, "w") as file:
            file.write(content)
        return f"Successfully wrote to {resolved_path}"
    except Exception as e:
        raise Exception(f"An error occurred while writing to the file: {e}")

@function_tool
def get_repository_structure():
    """
    Fetches the structure of the repository from the given directory
    Args:
        repository (str): The directory name of the repository.
    Returns:
        str: The structure of the repository.
    """
    print(f">>>>>>>>>>>>>>> get_repository_structure tool called")
    return subprocess.run(
        f"tree -P \"*.py\" -fi .",
        shell=True,
        check=True,
        capture_output=True,
        text=True
    ).stdout.strip()

@function_tool
def find_correct_path_for_passed_file(file:str):
    """
    Finds the correct path for a given file in the current working directory by prompting it to the local ollama instance.
    Args:
        file (str): The name of the file to find.
    Returns:
        str: The resolved path of the file.
    """
    try:
        payload = {
            "model": "phi3",
            "prompt": f"Find the correct path for the file '{file}' in the following directory structure:\n{get_repository_structure()}. Only return the path",
            "stream": False
        }
        response = requests.post(ollama, json=payload)
        return response.text.strip()
    except requests.RequestException as e:
        raise Exception(f"An error occurred while finding the file path: {e}")

@function_tool
def read_file_tool(path:str):
    """
    Reads a file from the given path and returns its content.
    """
    print(f">>>>>>>>>>>>>>> read_file_tool called with path: {path}")
    try:
        resolved_path = resolve_file_path(path)
        print(f"Resolved path: {resolved_path}")
        with open(resolved_path, "r") as file:
            result = file.read()
            print(f"Read {len(result)} characters from file: {resolved_path}")
            return {
                "file_path": resolved_path,
                "is_read": True,
                "content": result
            }
    except FileNotFoundError:
        raise Exception(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    
@function_tool
def test_changes_tool(instance_id: str, repoDir: str, FAIL_TO_PASS: List[str], PASS_TO_PASS: List[str]):
    """
    Tests the changes made in the repository by calling an external API.
    Args:
        instance_id (str): The instance ID for the test.
        repoDir (str): The local directory of the repository. Usually a number.
        FAIL_TO_PASS (List[str]): List of files that should fail the test.
        PASS_TO_PASS (List[str]): List of files that should pass the test.
    """
    print(f">>>>>>>>>>>>>>> test_changes_tool called with instance_id: {instance_id}, repoDir: {repoDir}, FAIL_TO_PASS: {FAIL_TO_PASS}, PASS_TO_PASS: {PASS_TO_PASS}")
    try:
        repo = Repo(os.path.join(os.getcwd(), repoDir))
        if not repo.untracked_files:
            print("No untracked files found in the repository.")
        payload = {
            "instance_id": instance_id,
            "repoDir": f"/repos/{repoDir}",
            "FAIL_TO_PASS": FAIL_TO_PASS,
            "PASS_TO_PASS": PASS_TO_PASS
        }
        response = requests.post("http://localhost:8082/test", json=payload)
        if response.status_code == 200:
            print(f"Test changes response: {response.text}")
            # Write to file
            with open(os.path.join(BASE_PATH + "/" + repoDir, "test_results.json"), "w") as file:
                file.write(response.text)
            return response.text
        else:
            raise Exception(f"Failed to test changes: {response.text}")
    except requests.RequestException as e:
        raise Exception(f"An error occurred while testing changes: {e}")

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
    
def test_changes_tool_plain(payload:dict, iterator:str):
    """
    Tests the changes made in the repository by calling an external API.
    Args:
        payload (dict): The payload containing instance_id, repoDir, FAIL_TO_PASS, and PASS_TO_PASS.
    Returns:
        str: The response from the test API.
    """
    response = requests.post("http://localhost:8082/test", json=payload)
    if response.status_code == 200:
        print(f"Test changes response: {response.text}")
        # Write to file
        with open(os.path.join(BASE_PATH + "/" + iterator, "test_results.json"), "w") as file:
            file.write(response.text)
        return response.text
    else:
        raise Exception(f"Failed to test changes: {response.text}")