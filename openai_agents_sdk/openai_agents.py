from agents import trace, ItemHelpers, Agent, Runner, RunContextWrapper
import asyncio
from multi_agent_system_helper.helper_functions import fix_clone_command, clone_repository
from multi_agent_system_helper.helper_functions import create_team_prompt, fetch_problem_statement
from multi_agent_system_helper.openai_agents_sdk_tools import test_changes_tool, read_file_tool, write_file_tool, find_correct_path_for_passed_file, set_working_directory, read_dir_structure, get_repository_structure
import os
from pydantic import BaseModel
from typing import List
import subprocess
from dataclasses import dataclass

BASE_PATH = "/home/dennisschiese/Projekte/Master/2. Semester/Automated Software Engineering/Projekt/results"

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
class RepositoryData:
    git_clone: str
    problem_statement: str
    patch: str
    instance_id: str
    FAIL_TO_PASS: List[str]
    PASS_TO_PASS: List[str]
    VALIDATOR_RESPONSE: str

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
    tools=[read_file_tool],
    model="gpt-4o-mini"
)

with open("prompts/planner", "r") as f:
    planner_instructions = f.read()

planning_agent = Agent(
    name="planning_agent",
    instructions=planner_instructions, # = System message
    tools=[
        coding_agent.as_tool(
            tool_name="coding_agent_tool",
            tool_description="Fixes code in assigned files based on the task description. Provide a problem statement and the file." # Define required data in prompt or here?
    ),
        test_agent.as_tool(
            tool_name="test_agent_tool",
            tool_description="Tests the code changes made by the coding agent. Provide the instance_id, repoDir, FAIL_TO_PASS, and PASS_TO_PASS lists from the repository data." # Define required data in prompt or here?
    ),
        validation_agent.as_tool(
            tool_name="validation_agent_tool",
            tool_description="Validates the code changes made by the coding agent. Provide the fixed file."
    ),
    read_file_tool],
    model="gpt-4o-mini"
)



async def main():
    for i in range(6, 11):
        try:
            repository_data = fetch_problem_statement(i)
            git_clone_with_index = fix_clone_command(repository_data['git_clone'], str(i))  # Replace "1" with the iterator
            clone_repository(git_clone_with_index)
            prompt = create_team_prompt(repository_data, str(i)) # Replace 1 with iterator
            # Create directory in BASE_PATH with the "1" as folder name
            os.makedirs(os.path.join(BASE_PATH, str(i)), exist_ok=True) # Replace 1 with iterator
            with trace(str(i)):
                result = Runner.run_streamed(
                    planning_agent,
                    context={"repos_data": repository_data}, # Move "repos_data" to constant
                    input=prompt
                )
                async for event in result.stream_events():
                    if event.type == "raw_response_event":
                        continue
                    elif event.type == "agent_updated_stream_event":
                        print(f"Agent updated: {event.new_agent.name}")
                        continue
                    elif event.type == "run_item_stream_event":
                        if event.item.type == "tool_call_item":
                            print(f"-- Tool was called by the agent: {event.item.agent.name}")
                            print(f"Tool: {event.item.raw_item}")
                        elif event.item.type == "tool_call_output_item":
                            print(f"-- Tool output: {event.item.output}")
                        elif event.item.type == "message_output_item":
                            print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
        except Exception as e:
            continue
        subprocess.run(f"sudo rm -r {i}", shell=True, check=True)  # Clean up the cloned repository

if __name__ == "__main__":
    asyncio.run(main())