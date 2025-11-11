# How to release the Agent and its Docker image

To release an updated version of the Agent perform the following steps:

1. Release an updated Docker image:

```sh
docker login ghcr.io -u YOUR_GITHUB_USERNAME
python release_tools/publish_docker.py ghcr.io/githubsecuritylab/seclab-taskflow-agent latest
```

Note: your login password is a GitHub PAT with packages write/read/delete scope enabled.

# Notes on our Docker image configuration

For simplicity we use a single Dockerfile that contains all the dependencies required for both our Agent and our various MCP servers.

Since we provide a mount path for the main agent that is configurable via an environment variable, you can provide custom data to the included stdio MCP servers without any Docker image requirements. By setting a path in the `MY_DATA` environment variable, that data will be available in `/app/my_data` to the Agent and its included MCP servers.

Likewise you can mount custom taskflows (`MY_TASKFLOWS`), personalities (`MY_PERSONALITIES`), and prompts (`MY_PROMPTS`) into the Docker image to make them available for use by the Agent.

See `docker/run.sh` for details on how to leverage those configurations. We do also provide the host Docker socket to the image such that 3rd party Docker MCP server images, such as the GitHub MCP server, work as expected.

The default entry point for our Agent Docker image is `/app/main.py`. If you'd like to deploy one of our MCP servers as a standalone server via the Docker image, use `--entrypoint` to set the appropriate entry point.

For example, a configuration to run the echo MCP server via Docker image instead, would look like:

```yaml
server_params:
  kind: stdio
  command: docker
  args: ["run", "--entrypoint", "python" "-i", "--rm", "ghcr.io/githubsecuritylab/seclab-taskflow-agent", "toolboxes/mcp_servers/echo/echo.py"]
```
