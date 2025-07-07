from agents import trace, ItemHelpers, Agent, Runner, RunContextWrapper
import asyncio
from multi_agent_system_helper.helper_functions import fix_clone_command, clone_repository
from multi_agent_system_helper.helper_functions import create_team_prompt, fetch_problem_statement
from multi_agent_system_helper.openai_agents_sdk_tools import test_changes_tool_plain, test_changes_tool, read_file_tool, write_file_tool, find_correct_path_for_passed_file, set_working_directory, read_dir_structure, get_repository_structure
import os
from pydantic import BaseModel
from typing import List
import subprocess
from dataclasses import dataclass
import requests
import json

BASE_PATH = "REPLACE"

# Dataclasses
@dataclass
class TestData:
    instance_id: str
    repoDir: str
    FAIL_TO_PASS: List[str]
    PASS_TO_PASS: List[str]

@dataclass
class ValidationData:
    fixed_file: str
    test_results: str

@dataclass
class CodingData:
    problem_description: str
    file: str

@dataclass
class Results:
    is_fixed: bool
    suggested_changes: str

### AGENTS ###

with open("prompts/coder", "r") as f:
    coder_instructions = f.read()

coding_agent = Agent[CodingData](
    name="coding_agent",
    instructions=coder_instructions,
    tools=[read_file_tool, write_file_tool],
    model="gpt-4o-mini"
)

with open("prompts/tester", "r") as f:
    tester_instructions = f.read()

test_agent = Agent[TestData](
    name="test_agent",
    instructions=tester_instructions,
    model="gpt-4o-mini",
    tools=[test_changes_tool]
)

with open("prompts/validator", "r") as f:
    validator_instructions = f.read()

validation_agent = Agent[ValidationData](
    name="validation_agent",
    instructions=validator_instructions,
    model="gpt-4o-mini",
    output_type=Results
)

with open("prompts/planner", "r") as f:
    planner_instructions = f.read()

planning_agent = Agent(
    name="planning_agent",
    instructions=planner_instructions, # = System message
    tools=[read_file_tool],
    model="gpt-4o-mini",
    output_type=CodingData
)

def ensure_list(val):
    if isinstance(val, str):
        return json.loads(val)
    return val

async def main():

    for i in range(26, 31): # 30 tasks
        index = str(i)

        # Prepare environment
        repository_data = fetch_problem_statement(index)
        git_clone_with_index = fix_clone_command(repository_data['git_clone'], index)  # Replace "1" with the iterator
        clone_repository(git_clone_with_index)
        process_log = BASE_PATH + "/" + index + "/process.txt"

        # Execute the task with X iterations
        result = None # Is the result of the validation agent
        for j in range(0, 1): # Sets the number of iterations to X, where X is the number of times the pipeline should be run
            repository_data["validator_input"] = result.suggested_changes if result else "No previous runs executed"
            prompt = create_team_prompt(repository_data, index)
            os.makedirs(os.path.join(BASE_PATH, index), exist_ok=True)
            with open(process_log, "a") as log_file:
                log_file.write(f"Running iteration {j+1} for task {index}\n")
                log_file.write(f"Prompt: {prompt}\n")
                log_file.write("---"*30 + "\n")
            result = await pipeline(prompt, repository_data, index, process_log)
            if result.is_fixed:
                break

        subprocess.run(f"sudo rm -r {index}", shell=True, check=True)  # Clean up the cloned repository
        os.chdir("..")

async def pipeline(prompt: str, repo_data:dict, iterator:str, process_log:str):

    print(f"Running pipeline with prompt: {prompt}")

    step1 = await Runner.run(
        planning_agent,
        input=prompt,
        max_turns=20
    )
    print(f"Step 1 output: {step1.final_output}")

    with open(process_log, "a") as log_file:
        log_file.write(f"Step 1 output: {step1.final_output}\n")
        log_file.write(f"Problem description: {step1.final_output.problem_description}\n")
        log_file.write(f"File: {step1.final_output.file}\n")
        log_file.write("---"*10 + "\n")

    step2 = await Runner.run( # It is possible to iterate over the files if more than one file is present in the data
        coding_agent,
        input=f"Described error: {step1.final_output.problem_description}\nFile: {step1.final_output.file}"
    )
    print(f"Step 2 output: {step2.final_output}")

    with open(process_log, "a") as log_file:
        log_file.write(f"Step 2 output: {step2.final_output}\n")
        log_file.write("---"*10 + "\n")

    payload = {
        "instance_id": repo_data['instance_id'],
        "repoDir": f"/repos/{iterator}",
        "FAIL_TO_PASS": ensure_list(repo_data['FAIL_TO_PASS']),
        "PASS_TO_PASS": ensure_list(repo_data['PASS_TO_PASS'])
    }

    test_results = test_changes_tool_plain(payload, iterator)
    print(f"Step 3/Test results: {test_results}")
    with open(process_log, "a") as log_file:
        log_file.write(f"Step 3/Test results: {test_results}\n")
        log_file.write("---"*10 + "\n")

    step4 = await Runner.run(
        validation_agent,
        input="Test results: " + test_results
    )
    print(f"Step 4 output: {step4.final_output}")
    with open(process_log, "a") as log_file:
        log_file.write(f"Step 4 output: {step4.final_output}\n")
        log_file.write("---"*10 + "\n")
    return step4.final_output # type::Results


if __name__ == "__main__":
    asyncio.run(main())
