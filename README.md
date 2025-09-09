# Seclab Taskflow Agent

The Security Lab Taskflow Agent is an MCP enabled multi-Agent framework.

The Taskflow Agent is built on top of the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

While the Taskflow Agent does not integrate into the GitHub Doctom Copilot UX, it does operate using the Copilot API (CAPI) as its backend, similar to Copilot IDE extensions.

## Core Concepts

The Taskflow Agent leverages a GitHub Workflow-esque YAML based grammar to perform a series of tasks using a set of Agents.

It's primary value proposition is as a CLI tool that allows users to quickly define and script Agentic workflows without having to write any code.

Agents are defined through [personalities](personalities/), that receive a [task](taskflows/) to complete given a set of [tools](toolboxes/).

Agents can cooperate to complete sequences of tasks through so-called [Taskflows](taskflows/GRAMMAR.md).

## Requirements

Python >= 3.9 or Docker

# Usage

Provide a Copilot entitled GitHub PAT via the `COPILOT_TOKEN` environment variable.

## Source

First install the required dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Then run `python main.py`.

Example: deploying a prompt to an Agent Personality:

```sh
python main.py -p assistant 'explain modems to me please'
```

Example: deploying a Taskflow:

```sh
python main.py -t example
```

## Docker

Alternatively you can deploy the Agent via its Docker image using `docker/run.sh`. 

The image entrypoint is `main.py` and thus it operates the same as invoking the Agent from source directly.

You can find the Docker image for the Seclab Taskflow Agent [here](https://github.com/GitHubSecurityLab/seclab-taskflow-agent/pkgs/container/seclab-taskflow-agent) and how it is built [here](release_tools/).

Note that this image is based on a public release of the Taskflow Agent, and you will have to mount any custom taskflows, personalities, or prompts into the image for them to be available to the Agent. 

See [docker/run.sh](docker/run.sh) for configuration details.

Example: deploying a Taskflow:

```sh
docker/run.sh -t example
```
Example: deploying a custom taskflow:

```sh
MY_TASKFLOWS=~/my_taskflows docker/run.sh -t custom_taskflow
```

Available image mount points are:

- Custom data via `MY_DATA` environment variable
- Custom personalities via `MY_PERSONALITIES` environment variable
- Custom taskflows via `MY_TASKFLOWS` environment variable
- Custom prompts via `MY_PROMPTS` environment variable
- Custom toolboxes via `MY_TOOLBOXES` environment variable

For more advanced scenarios like e.g. making custom MCP server code available, you can alter the run script to mount your custom code into the image and configure your toolboxes to use said code accordingly.

Example: custom MCP server deployment via Docker image:

```sh
export MY_MCP_SERVERS=./mcp_servers
export MY_TOOLBOXES=./toolboxes
export MY_PERSONALITIES=./personalities
export MY_TASKFLOWS=./taskflows
export MY_PROMPTS=./prompts

if [ ! -f ".env" ]; then
    touch ".env"
fi

docker run \
       --volume /var/run/docker.sock:/var/run/docker.sock \
       --volume logs:/app/logs \
       --mount type=bind,src=.env,dst=/app/.env,ro \
       ${MY_DATA:+--mount type=bind,src=$MY_DATA,dst=/app/my_data} \
       ${MY_MCP_SERVERS:+--mount type=bind,src=$MY_MCP_SERVERS,dst=/app/my_mcp_servers,ro} \
       ${MY_TASKFLOWS:+--mount type=bind,src=$MY_TASKFLOWS,dst=/app/taskflows/my_taskflows,ro} \
       ${MY_TOOLBOXES:+--mount type=bind,src=$MY_TOOLBOXES,dst=/app/toolboxes/my_toolboxes,ro} \
       ${MY_PROMPTS:+--mount type=bind,src=$MY_PROMPTS,dst=/app/prompts/my_prompts,ro} \
       ${MY_PERSONALITIES:+--mount type=bind,src=$MY_PERSONALITIES,dst=/app/personalities/my_personalities,ro} \
       "ghcr.io/githubsecuritylab/seclab-taskflow-agent" "$@"
```

Our default run script makes the Docker socket available to the image, which contains the Docker cli, so 3rd party Docker based stdio MCP servers also function as normal.

Example: a toolbox configuration for the official GitHub MCP Server:

```yaml
server_params:
  kind: stdio
  command: docker
  args: ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "ghcr.io/github/github-mcp-server"]
  env:
    GITHUB_PERSONAL_ACCESS_TOKEN: "{{ env GITHUB_PERSONAL_ACCESS_TOKEN }}"
```

## Framework Configuration

Set environment variables via an `.env` file in the project root.

Example: a persistent Agent configuration with various MCP server environment variables set:

```sh
# Tokens
COPILOT_TOKEN=...
# Docker config, MY_DATA is mounted to /app/my_data
MY_DATA="/home/user/my_data"
# MCP configs
GITHUB_PERSONAL_ACCESS_TOKEN=...
CODEQL_DBS_BASE_PATH="/app/my_data/"
```

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

## License 

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) file for the full terms.

## Maintainers 

[CODEOWNERS](./CODEOWNERS)

## Support

[SUPPORT](./SUPPORT.md)

## Acknowledgement

Security Lab team members @m-y-mo and @p- for contributing heavily to the testing and development of this framework, as well as the rest of the Security Lab team for helpful discussions and use cases.
