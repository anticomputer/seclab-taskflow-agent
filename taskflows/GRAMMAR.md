# Taskflows

Taskflows are YAML lists of tasks.

Example:

```yaml
taskflow:
  - task:
    ...
  - task:
    ...
```

## Tasks

Tasks define, at minimum, a list of Agents to use and a User Prompt.

Example:

```yaml
  - task:
    agents:
      - assistant
    user_prompt: |
      This is a user prompt.
```

### Agents

Agents are defined through their own YAML grammar as so called personalities.

Example:

```yaml
personality: |
  You are a helpful assistant.
  
task: |
  Your primary task is to use available tools to complete user defined tasks.

  Always use available tools to complete your tasks. If the tools you require
  to complete a task are not available, politely decline the task.
  
toolboxes:
  - ...
```

Task agent lists can define one (primary) or more (handoff) agents.

Example:

```yaml
  - task:
    agents:
      - primary_agent
      - handoff_agent1
      - ...
      - handoff_agentN
    user_prompt: |
      ...
```

### Model

Tasks can optionally specify which Model to use on the configured inference endpoint:

```yaml
  - task:
    model: gpt-4.1
    agents:
      - assistant
    user_prompt: |
      This is a user prompt.
```

Note that model identifiers may differ between OpenAI compatible endpoint providers, make sure you change your model identifier accordingly when switching providers.

### Completion Requirement

Tasks can be marked as requiring completion, if a required task fails, the taskflow will abort. This defaults to false.

Example:

```yaml
  - task:
    must_complete: true
    agents:
      - assistant
    user_prompt: |
      ...
```

### Repeated Prompts

Tasks can define templated repeated prompts. A repeated prompt requires the last result output of the previous task in the taskflow to be a json formatted iterable.

Example:

```yaml
  # this task must result in a json iterable
  - task:
    ...
  # this task can iterate across the iterable
  - task:
    agents:
      - assistant
    repeat_prompt: true
    user_prompt: |
      This is a templated prompt. It can iterate the results in a list via {{ RESULT }}, 
      if the result is a dict you access its keys via {{ RESULT_key }}. 
```

### Context Exclusion

Tasks can specify that their tool results and output should be available at the Agent level but not included in the Model context, to e.g. save on tokens for data that does not need to be available to the Model but that still needs to be generated via a prompt inferred tool call.

Example:

```yaml
  - task:
    exclude_from_context: true
    agents:
      - assistant
    user_prompt: |
      List all the files in the codeql database `some/codeql/db`.
    toolboxes:
      - codeql
```

### Toolboxes / MCP Servers

Toolboxes are MCP server configurations. They can be defined at the Agent level or overridden at the task level. These MCP servers are started and made available to the Agents in the Agents list during a Task.

### Headless Runs

MCP server configurations can request confirmations for tool calls. These confirmations are prompted on the terminal. If you want to allow all tool calls by default for headless use, you can set a task to run headless.

Example:

```yaml
  - task:
    headless: true
    agents:
      - assistant
    user_prompt: |
      Clear the memory cache.
    toolboxes:
      - memcache
```

### Environment Variables

Tasks can be configured to set temporary os environment variables available during the task. This is primarily used to pass through configuration options to toolboxes (mcp servers).

Example:

```yaml
  - task:
    headless: true
    agents:
      - assistant
    user_prompt: |
      Store `hello` in the memory key `world`.
    toolboxes:
      - memcache
    env:
      MEMCACHE_STATE_DIR: "example_taskflow/"
      MEMCACHE_BACKEND: "dictionary_file"
```

### Shell Tasks

Tasks can be entirely shell based through the run directive. This allows you to e.g. pass in json iterable outputs from shellscripts into a prompt task.

Example:

```yaml
  - task:
    must_complete: true
    run: |
      echo '["apple", "banana", "orange"]'
  - task:
    repeat_prompt: true
    agents:
      - assistant
    user_prompt: |
      What kind of fruit is {{ RESULT }}?
```

Use shell tasks when you want to iterate on results that don't need to be generated via a prompt inferred tool call.

### Async Tasks

Tasks can be asynchronous with a specified number of async workers. This is primarily useful to parallelize repeated prompt tasks.

Example:

```yaml
  - task:
    must_complete: true
    run: |
      echo '["apple", "banana", "orange"]'
  - task:
    repeat_prompt: true
    async: true
    async_limit: 3
    agents:
      - assistant
    user_prompt: |
      What kind of fruit is {{ RESULT }}?
```

### Globals

Taskflows can define toplevel global variables available to every task.

Example:

```yaml
globals:
  fruit: bananas
taskflow:
  - task:
      agents:
        - fruit_expert
      user_prompt: |
        Tell me more about {{ GLOBALS_fruit }}.
```

### Inputs

Tasks can be provided with templated inputs.

Example:

```yaml
  - task:
    agents:
      - fruit_expert
    inputs:
      fruit: apples
    user_prompt: |
      Tell me more about {{ INPUTS_fruit }}.
```

### Reusable Prompts

Tasks can incorporate templated prompts from the prompts directory tree.

Example:

```yaml
  - task:
    agents:
      - fruit_expert
    user_prompt: |
      Tell me more about apples.

      {{ PROMPTS_examples/example_prompt }}
```

### Reusable Tasks

Tasks can reuse single step taskflows and optionally override any of its configurations.

Example:

```yaml
  - task:
    uses: single_step_taskflow
    model: gpt-4o
```
