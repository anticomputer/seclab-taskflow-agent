The Security Lab Taskflow Agent is an MCP enabled multi-Agent framework.

While the [Security Lab Copilot Extensions Framework](https://github.com/github/seclab-copilot-extensions) was created for team-internal prototyping and exploring various Agentic workflow ideas and approaches, the Taskflow Agent is intended as a "production" implementation.

The Taskflow Agent is built on top of the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) in contrast to the largely custom backend implementations of our original Copilot extensions framework.

As such the Taskflow Agent provides a more future-proof CLI focused Agent tool as we leverage the SDK for keeping pace with e.g. evolving MCP protocol specifications.

While the Taskflow Agent does not integrate into the dotcom Copilot UX, it does operate using the Copilot API (CAPI) as its backend.

# Core Concepts

The Taskflow Agent leverages a GitHub Workflow-esque YAML based grammar to perform a series of tasks using a set of Agents.

Agents are defined through [personalities](personalities/), that receive a [task](taskflows/) to complete given a set of [tools](toolboxes/).

Agents can cooperate to complete sequences of tasks through so-called [Taskflows](taskflows/GRAMMAR.md).

# Installation

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## System Requirements

Python >= 3.9

# Usage

Provide a Copilot entitled GitHub PAT via the `COPILOT_TOKEN` environment variable.

Run `python main.py` for help.

Example: deploying a prompt to an Agent Personality:

```
python main.py -p assistant 'explain modems to me please'
```

Example: deploying a Taskflow:

```
python main.py -t example
```

## Configuration

Set environment variables via an `.env` file in the project root as required.

# Personalities

Core characteristics for a single Agent. Configured through YAML files in `personalities/`.

These are system prompt level instructions.

Example:

```yaml
# personalities define the system prompt level directives for this Agent
personality: |
  You are a simple echo bot. You use echo tools to echo things.

task: |
  Echo user inputs using the echo tools.
  
# personality toolboxes map to mcp servers made available to this Agent
toolboxes:
  - echo
```

# Toolboxes

MCP servers that provide tools. Configured through YAML files in `toolboxes/`.

Example stdio config:

```yaml
# stdio mcp server configuration
server_params:
  kind: stdio
  command: python
  args:
    - toolboxes/echo/echo.py
  env:
    SOME: value
```

Example sse config:

```yaml
server_params:
  kind: sse
  # make sure you .env config the echo server, see echo_sse.py for example
  url: http://127.0.0.1:9000/echo
  headers:
    SomeHeader: "{{ env USER }}"
```

# Taskflows

A sequence of interdependent tasks performed by a set of Agents. Configured through a YAML based [grammar](taskflows/GRAMMAR.md) in [taskflows/](taskflows/).

Example:

```yaml
taskflow:
  - task:
      # taskflows can optionally choose any of the support CAPI models for a task
      model: gpt-4.1
      # taskflows can optionally limit the max allowed number of Agent task loop
      # iterations to complete a task, this defaults to 50 when not provided
      max_steps: 20
      must_complete: true
      # taskflows can set a primary (first entry) and handoff (additional entries) agent
      agents:
        - c_auditer
        - fruit_expert
      user_prompt: |
        Store an example vulnerable C program that uses `strcpy` in the
        `vulnerable_c_example` memory key and explain why `strcpy`
        is insecure in the C programming language. Do this before handing off
        to any other agent.
        
        Then provide a summary of a high impact CVE ID that involved a `strcpy`
        based buffer overflow based on your GHSA knowledge as an additional
        example.

        Finally, why are apples and oranges healthy to eat?
        
      # taskflows can set temporary environment variables, these support the general
      # "{{ env FROM_EXISTING_ENVIRONMENT }" pattern we use elsewhere as well
      # these environment variables can then be made available to any stdio mcp server
      # through its respective yaml configuration, see memcache.yaml for an example
      # you can use these to override top-level environment variables on a per-task basis
      env:
        MEMCACHE_STATE_DIR: "example_taskflow/"
        MEMCACHE_BACKEND: "dictionary_file"
      # taskflows can optionally override personality toolboxes, in this example
      # kevin normally only has the memcache toolbox, but we extend it here with
      # the GHSA toolbox
      toolboxes:
        - ghsa
        - memcache
  - task:
      must_complete: true
      model: gpt-4.1
      agents:
        - c_auditer
      user_prompt: |
        Retrieve C code for security review from the `vulnerable_c_example`
        memory key and perform a review.

        Clear the memory cache when you're done.
      env:
        MEMCACHE_STATE_DIR: "example_taskflow/"
        MEMCACHE_BACKEND: "dictionary_file"
      toolboxes:
        - memcache
```

Taskflows support [Agent handoffs](https://openai.github.io/openai-agents-python/handoffs/). Handoffs are useful for implementing triage patterns where the primary Agent can decide to handoff a task to any subsequent Agents in the `Agents` list.

See the [taskflow examples](taskflows/examples) for other useful Taskflow patterns such as repeatable and asynchronous templated prompts.

# Docker based deployments

You can find a Docker image for the Seclab Taskflow Agent [here](https://github.com/GitHubSecurityLab/seclab-taskflow-agent/pkgs/container/seclab-taskflow-agent)

Note that this image is based on the public release of the Taskflow Agent, and you will have to mount any custom taskflows, personalities, or prompts into the image for them to be available to the Agent. See [docker/run.sh](docker/run.sh) for examples of use.
