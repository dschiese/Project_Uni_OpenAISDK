# Uni Leipzig ASE OpenAI Agents SDK

Projekt der Universität Leipzig im Modul **Automated Software Engineering**. 

# Usage

## Set up swe-bench-lite-*

### Set up swe-bench-lite-api

```
sudo docker run -d \
-p 8081:8080 \
--name swe-bench-lite-api \
paulroewer/swe-bench-lite-api
```

### Set up swe-bench-lite-tester

```
sudo docker run -d \
-p 8082:8080 \
--name swe-bench-lite-tester \
-v REPLACE_WITH_PWD_TO_REPOSITORIES:/repos \
-v /var/run/docker.sock:/var/run/docker.sock \
paulroewer/swe-bench-lite-tester
```

Here, replace the volume mapping of "/repos" to the `repositories` directory in this repository.

## Replace BASE_PATH  `team.py` and `openai_agents_sdk_tools.py`

In the `team.py` and `multi_agent_system_helper/openai_agents_sdk_tools.py` replace the BASE_PATH with the absolute path to the `results` folder in this repository.

For example: `BASE_PATH = "/home/user/openai_agents_sdk/results"`

## Set LLM 

### LiteLLM

TODO

### OpenAI

Set the environment variable `OPENAI_API_KEY`. For example, `export OPENAI_API_KEY=sk-....`.

### Set Model

To set the used model, you can pass it to each agent separately.

## Run

Run the team script from the repository root directory with `python -m openai_agents_sdk.team`

# Known problems

## Too much context

When too much files are read and included in the context, it becomes too big to handle. Here, you might change the model used or re-run the process as this is often a result of the problem below (too much read-file tool calls).

## Too much files read

Sometimes, the planning agent utilizes the read_file_tool too often, and as there is a maximum turns limit (can be adjusted within the Runner!), the maximum turns are reached as it seems to be an endless loop.
An error like `agents.exceptions.MaxTurnsExceeded: Max turns (20) exceeded` will appear. Often, a re-run fixes the problem. If not, increase the max runs or adjust the prompts.


